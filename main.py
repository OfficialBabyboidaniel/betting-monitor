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
from webdriver_manager.chrome import ChromeDriverManager
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
        self.email_to = os.getenv("EMAIL_TO", self.email_user)  # Default to same email
        
    def send_pushbullet(self, title, message):
        """Send notification via Pushbullet"""
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
        """Send notification via Telegram"""
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
        """Send notification via Discord webhook"""
        if not self.discord_webhook:
            return False
        try:
            data = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 0x00ff00,  # Green color
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
        """Send notification via email"""
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
        """Send notification via all available services"""
        success = False
        success |= self.send_pushbullet(title, message)
        success |= self.send_telegram(f"<b>{title}</b>\n{message}")
        success |= self.send_discord(title, message)
        success |= self.send_email(title, message)
        return success

def main():
    notifier = NotificationService()
    
    def start_driver():
        """Initialize and return Chrome driver"""
        options = uc.ChromeOptions()
        # Force headless mode in Docker
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Allow popups
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 1
        })
        
        # Use webdriver-manager to get the correct ChromeDriver version
        driver_path = ChromeDriverManager().install()
        driver = uc.Chrome(driver_executable_path=driver_path, options=options)
        driver.implicitly_wait(IMPLICIT_WAIT)
        
        # Navigate to login page immediately
        print(f"Navigating to login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        print("Page loaded successfully!")
        return driver
    def automated_login(driver, username, password):
        """Attempt automated login"""
        driver.get(LOGIN_URL)
        try:
            WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            print("Page loaded. Waiting extra seconds for scripts...")
            time.sleep(random.uniform(0.3, 0.6))
            
            user_input = driver.find_element(By.ID, "inputEmail")
            pass_input = driver.find_element(By.ID, "inputPassword")
            
            driver.execute_script('arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event("input", {bubbles:true})); arguments[0].dispatchEvent(new Event("change", {bubbles:true}));', user_input, username)
            time.sleep(random.uniform(0.3, 0.6))
            driver.execute_script('arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event("input", {bubbles:true})); arguments[0].dispatchEvent(new Event("change", {bubbles:true}));', pass_input, password)
            time.sleep(random.uniform(0.3, 0.6))
            
            try:
                submit = driver.find_element(By.CSS_SELECTOR, "button[type=submit], button.btn-primary")
                submit.click()
            except NoSuchElementException:
                pass
            time.sleep(random.uniform(0.3, 0.6))
        except TimeoutException:
            print("Timed out waiting for login form — the automated login may not work. Please log in manually.")
            wait_for_manual_login(driver)
        pass
    def wait_for_manual_login(driver):
        """Open login page and wait for manual login"""
        print("Opening login page. Please log in manually in the browser window.")
        driver.get(LOGIN_URL)
        input("When you've completed login, press Enter here to continue...")

    driver = start_driver()
    try:
        username = os.getenv("REBEL_USERNAME")
        password = os.getenv("REBEL_PASSWORD")
        
        if username and password:
            print("REBEL_USERNAME found in env — attempting automated login (may fail).")
            automated_login(driver, username, password)
        else:
            print("REBEL_USERNAME not found in env — please log in manually.")
            wait_for_manual_login(driver)

        #input("Login completed. Press Enter to continue with bet placement...")
        
        #check if there actually are any bet cards 
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        print("Page loaded. Waiting extra seconds for scripts...")
        time.sleep(random.uniform(0.3, 0.6))
        time.sleep(0.5)  # Wait for potential dynamic content to load
        while True:  
            WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            print("Page loaded. Waiting extra seconds for scripts...")
            time.sleep(random.uniform(0.3, 0.6))
            # Close backdrop popups if present (attempt multiple selectors)
            try:
                # WHAT IS THE CORRECT HTML SELECTOR FOR REBEL BETTING POPUPS?
                popup_close = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[data-testid='CloseLargeOutlinedIcon']"))
                )
                popup_close.click()
                print("Closed BetMGM popup")
                time.sleep(random.uniform(0.3, 0.6))
            except:
                pass
            try:
                # Check if the odds-card contains "No value bets" message
                odds_card = driver.find_element(By.CSS_SELECTOR, ".odds-card")
                if "No value bets" in odds_card.text:
                    print("No value bets available with current filters")
                else:
                    print("Value bets found! Proceeding with pinging...")
                    # Send notification when bets are found
                    bet_count = len(driver.find_elements(By.CSS_SELECTOR, ".bet-row, .value-bet"))
                    message = f"🎯 {bet_count} value bets detected on RebelBetting!\n\nCheck your dashboard: {LOGIN_URL}"
                    notifier.notify("Value Bets Available!", message)
            except:
                pass  # Continue if no odds-card found
            time.sleep(60)
            # Refresh the page to check for new bets
            driver.refresh()
            
    except Exception as e:
        pass
    
if __name__ == '__main__':
    main()