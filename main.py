import os
import time
from pyrogram import Client, filters
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure Pyrogram Bot
app = Client(
    "iloveimg_bot",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"]
)

# Configure Selenium (Koyeb needs headless setup)
CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--disable-gpu")
CHROME_OPTIONS.add_argument("--no-sandbox")

def automate_iloveimg(image_path: str):
    driver = webdriver.Chrome(options=CHROME_OPTIONS)
    try:
        driver.get("https://www.iloveimg.com/upscale-image")
        
        # Upload image
        upload_btn = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        upload_btn.send_keys(image_path)
        
        # Select 4x option
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'4×')]"))
        ).click()
        
        # Start processing
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Upscale Image')]"))
        ).click()
        
        # Wait for download button
        download_btn = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Download')]"))
        )
        return download_btn.get_attribute("href")
    finally:
        driver.quit()

@app.on_message(filters.command("upscale") & filters.photo)
async def handle_upscale(client, message):
    msg = await message.reply("🔄 Processing...")
    
    try:
        # Download image
        img_path = await message.download()
        
        # Get processed image URL
        download_url = automate_iloveimg(os.path.abspath(img_path))
        
        # Upload to Telegram
        await message.reply_document(
            document=download_url,
            caption="✅ 4x Upscaled via iloveimg.com"
        )
        
    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    app.run()
