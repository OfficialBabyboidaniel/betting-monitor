import time
import os
import random
import dotenv
import undetected_chromedriver as uc
import requests
import smtplib
from email.mime.text import MIMEText
from pushbullet import Pushbullet

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from config import LOGIN_URL, HEADLESS, IMPLICIT_WAIT, STAKE_AMOUNT, ACCUMULATED_STAKE

dotenv.load_dotenv()

class NotificationService:
    def __init__(self):
        self.pushbullet_token = os.getenv("PUSHBULLET_TOKEN")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        self.email_to = os.getenv("EMAIL_TO", self.email_user)
        
    def send_pushbullet(self, title, message):
        if not self.pushbullet_token:
            return False
        try:
            pb = Pushbullet(self.pushbullet_token)
            pb.push_note(title, message)
            print(f"Pushbullet notification sent: {title}")
            return True
        except Exception as e:
            print(f"Pushbullet error: {e}")
            return False
    
    def send_telegram(self, message):
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("Telegram notification sent")
                return True
            else:
                print(f"Telegram error: {response.text}")
                return False
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def send_discord(self, title, message):
        if not self.discord_webhook:
            return False
        try:
            data = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 0x00ff00,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
                }]
            }
            response = requests.post(self.discord_webhook, json=data)
            if response.status_code == 204:
                print("Discord notification sent")
                return True
            else:
                print(f"Discord error: {response.status_code}")
                return False
        except Exception as e:
            print(f"Discord error: {e}")
            return False
    
    def send_email(self, title, message):
        if not self.email_user or not self.email_pass:
            return False
        try:
            msg = MIMEText(message)
            msg['Subject'] = title
            msg['From'] = self.email_user
            msg['To'] = self.email_to
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            print("Email notification sent")
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def notify(self, title, message):
        success = False
        success |= self.send_pushbullet(title, message)
        success |= self.send_telegram(f"<b>{title}</b>\n{message}")
        success |= self.send_discord(title, message)
        success |= self.send_email(title, message)
        return success

def start_driver():
    print("🚀 Starting Chrome driver...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.popups": 1
    })
    
    try:
        print("⏳ Initializing Chrome (this may take 30-60 seconds)...")
        driver = uc.Chrome(options=options)
        print("✅ Chrome driver initialized successfully")
        
        driver.implicitly_wait(IMPLICIT_WAIT)
        
        print(f"🌐 Navigating to login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        print("✅ Page loaded successfully!")
        return driver
    except Exception as e:
        print(f"❌ Failed to start Chrome driver: {e}")
        import traceback
        traceback.print_exc()
        raise

def automated_login(driver, username, password):
    print(f"Starting automated login for user: {username}")
    driver.get(LOGIN_URL)
    try:
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        print("✓ Page loaded completely")
        time.sleep(random.uniform(0.3, 0.6))
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        try:
            user_input = driver.find_element(By.ID, "inputEmail")
            print("✓ Found email input field")
        except NoSuchElementException:
            print("✗ Email input field not found")
            return False
        
        try:
            pass_input = driver.find_element(By.ID, "inputPassword")
            print("✓ Found password input field")
        except NoSuchElementException:
            print("✗ Password input field not found")
            return False
        
        print("Filling in credentials...")
        driver.execute_script('arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event("input", {bubbles:true}));', user_input, username)
        time.sleep(random.uniform(0.3, 0.6))
        driver.execute_script('arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event("input", {bubbles:true}));', pass_input, password)
        time.sleep(random.uniform(0.3, 0.6))
        
        try:
            submit = driver.find_element(By.CSS_SELECTOR, "button[type=submit], button.btn-primary")
            print(f"✓ Found submit button: {submit.text}")
            
            if submit.get_attribute("disabled"):
                print("⚠️  Submit button is disabled, waiting...")
                time.sleep(2)
                try:
                    pass_input.send_keys(Keys.TAB)
                    time.sleep(1)
                except:
                    pass
            
            try:
                submit.click()
                print("✓ Clicked submit button")
            except Exception as click_error:
                print(f"Regular click failed: {click_error}")
                driver.execute_script("arguments[0].click();", submit)
                print("✓ JavaScript click successful")
                
        except NoSuchElementException:
            print("✗ Submit button not found")
            return False
        
        time.sleep(random.uniform(2, 4))
        
        print(f"URL after login attempt: {driver.current_url}")
        
        try:
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".odds-card")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='dashboard']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='bet']"))
                )
            )
            print("✓ Login appears successful")
            return True
        except TimeoutException:
            print("✗ Login may have failed")
            return False
            
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False

def main():
    print("🎯 Starting Rebel Betting Monitor...")
    notifier = NotificationService()
    driver = None
    
    try:
        driver = start_driver()
        
        username = os.getenv("REBEL_USERNAME")
        password = os.getenv("REBEL_PASSWORD")
        
        if username and password:
            print("🔑 Attempting automated login...")
            login_success = automated_login(driver, username, password)
            if not login_success:
                print("⚠️  Login failed, continuing anyway...")
        else:
            print("ℹ️  No credentials found, continuing without login...")

        print("🔄 Starting monitor loop...")
        
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        
        loop_count = 0
        while True:  
            loop_count += 1
            print(f"\n--- 🔍 Loop #{loop_count} ---")
            
            WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(random.uniform(0.3, 0.6))
            
            try:
                popup_close = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[data-testid='CloseLargeOutlinedIcon']"))
                )
                popup_close.click()
                print("✓ Closed popup")
            except:
                pass
            
            try:
                odds_card = driver.find_element(By.CSS_SELECTOR, ".odds-card")
                
                if "No value bets" in odds_card.text:
                    print("ℹ️  No value bets available")
                else:
                    print("🎯 Value bets found!")
                    bet_count = len(driver.find_elements(By.CSS_SELECTOR, ".bet-row, .value-bet"))
                    message = f"🎯 {bet_count} value bets detected!\n\nCheck: {LOGIN_URL}"
                    print(f"📱 Sending notification for {bet_count} bets...")
                    notifier.notify("Value Bets Available!", message)
            except Exception as e:
                print(f"⚠️  Could not find odds card: {e}")
            
            print("💤 Waiting 60 seconds...")
            time.sleep(60)
            print("🔄 Refreshing...")
            driver.refresh()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("🧹 Cleaning up...")
            try:
                driver.quit()
            except:
                pass
        print("👋 Goodbye!")

if __name__ == '__main__':
    main()