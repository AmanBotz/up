# main.py
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# Environment variables
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("iloveimg_upscale_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def process_image(image_path: str, scale: int = 4) -> str:
    """Process image through iloveimg's upscale API"""
    base_url = "https://api.iloveimg.com/v1"
    
    with requests.Session() as session:
        # Upload image
        upload_url = f"{base_url}/upload"
        files = {"file": open(image_path, "rb")}
        response = session.post(upload_url, files=files)
        server_filename = response.json()["server_filename"]

        # Start processing
        process_url = f"{base_url}/upscale"
        payload = {
            "server_filename": server_filename,
            "scale": scale,
            "output_format": "webp"
        }
        response = session.post(process_url, json=payload)
        task_id = response.json()["task"]

        # Wait for processing
        while True:
            status_url = f"{base_url}/task/{task_id}"
            status = session.get(status_url).json()
            if status["status"] == "success":
                break

        # Get download URL
        return f"{base_url}/download/{task_id}"

@app.on_message(filters.command("upscale") & filters.photo)
async def upscale_handler(client: Client, message: Message):
    msg = await message.reply("⏳ Downloading image...")
    
    try:
        # Download image
        image_path = await message.download()
        
        await msg.edit("⚡ Processing image (4x upscale)...")
        
        # Process image through iloveimg
        download_url = process_image(image_path)
        
        await msg.edit("📤 Uploading enhanced image...")
        
        # Download processed image
        response = requests.get(download_url)
        output_path = f"processed_{message.photo.file_id}.webp"
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        # Send result
        await message.reply_document(
            document=output_path,
            caption="✅ Image upscaled 4x using iloveimg.com"
        )
        
        # Cleanup
        os.remove(image_path)
        os.remove(output_path)
        await msg.delete()
    
    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    print("Bot started...")
    app.run()
