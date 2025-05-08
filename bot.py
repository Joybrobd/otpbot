from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# === CONFIGURATION ===
SEVEN1TEL_USERNAME = "nafew21"
SEVEN1TEL_PASSWORD = "Nafew@12345"
TELEGRAM_BOT_TOKEN = "7857715184:AAGSkc4KH-V7pDRYO4aSkxp5KQWdD3SrPvw"
TELEGRAM_CHAT_ID = "-1002508827613"  # ✅ Make sure the minus is there

# === SETUP CHROME (headless) ===
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# === LOGIN TO SEVEN1TEL ===
def login_seven1tel():
    driver.get("https://seven1tel.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(SEVEN1TEL_USERNAME)
    driver.find_element(By.NAME, "password").send_keys(SEVEN1TEL_PASSWORD)
    driver.find_element(By.XPATH, '//button[contains(text(), "Login")]').click()
    time.sleep(3)

# === FETCH SMS ===
def get_sms():
    driver.get("https://seven1tel.com/sms-test")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    sms_elements = driver.find_elements(By.XPATH, "//table//tr")
    messages = []
    
    for row in sms_elements[1:]:
        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) >= 2:
            number = columns[0].text.strip()
            message = columns[1].text.strip()
            messages.append(f"From: {number}\nMessage: {message}")
    
    return messages

# === SEND TO TELEGRAM ===
def send_to_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }
    requests.post(url, data=payload)

# === TRACK NEW SMS ONLY ===
old_sms = []

def run():
    login_seven1tel()
    global old_sms
    
    while True:
        try:
            new_sms = get_sms()
            fresh = [sms for sms in new_sms if sms not in old_sms]
            
            for sms in fresh:
                send_to_telegram(sms)
                print(f"Sent: {sms}")
            
            old_sms = new_sms
            time.sleep(60)
        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# === MAIN ===
if __name__ == "__main__":
    run()
