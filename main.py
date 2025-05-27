import os
import time
from pyrogram import Client, filters
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Client(
    "iloveimg_bot",
    api_id=os.environ["API_ID"],
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"]
)

def get_chrome_options():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")
    return options

def automate_iloveimg(image_path):
    driver = uc.Chrome(options=get_chrome_options(), version_main=114)
    try:
        driver.get("https://www.iloveimg.com/upscale-image")
        
        # Accept cookies
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ez-accept-all"))
            ).click()
        except:
            pass

        # Upload image
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        ).send_keys(image_path)

        # Select 4x upscale
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'4×')]"))
        ).click()

        # Start processing
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Upscale Image')]"))
        ).click()

        # Wait for download link
        download_link = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'downloader')]"))
        ).get_attribute("href")
        
        return download_link
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
