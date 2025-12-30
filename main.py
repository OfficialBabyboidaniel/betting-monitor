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
def main():
    print("🎯 Starting Rebel Betting Monitor...")
    notifier = NotificationService()
    driver = None
    
    try:
        driver = start_driver()
        
        username = os.getenv("REBEL_USERNAME")
        password = os.getenv("REBEL_PASSWORD")
        
        if username and password:
            print("🔑 REBEL_USERNAME found in env — attempting automated login (may fail).")
            login_success = automated_login(driver, username, password)
            if not login_success:
                print("⚠️  Automated login failed, but continuing to monitor anyway...")
        else:
            print("ℹ️  REBEL_USERNAME not found in env — continuing without login.")

        print("🔄 Starting betting monitor loop...")
        
        #check if there actually are any bet cards 
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        print("✅ Page loaded. Waiting extra seconds for scripts...")
        time.sleep(random.uniform(0.3, 0.6))
        time.sleep(0.5)  # Wait for potential dynamic content to load
        
        loop_count = 0
        while True:  
            loop_count += 1
            print(f"\n--- 🔍 Monitor Loop #{loop_count} ---")
            print(f"Current URL: {driver.current_url}")
            
            WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            print("✓ Page loaded completely")
            time.sleep(random.uniform(0.3, 0.6))
            
            # Close backdrop popups if present (attempt multiple selectors)
            try:
                # WHAT IS THE CORRECT HTML SELECTOR FOR REBEL BETTING POPUPS?
                popup_close = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[data-testid='CloseLargeOutlinedIcon']"))
                )
                popup_close.click()
                print("✓ Closed BetMGM popup")
                time.sleep(random.uniform(0.3, 0.6))
            except:
                pass
            
            try:
                # Check if the odds-card contains "No value bets" message
                odds_card = driver.find_element(By.CSS_SELECTOR, ".odds-card")
                print(f"✓ Found odds card with text: {odds_card.text[:100]}...")
                
                if "No value bets" in odds_card.text:
                    print("ℹ️  No value bets available with current filters")
                else:
                    print("🎯 Value bets found! Proceeding with pinging...")
                    # Send notification when bets are found
                    bet_count = len(driver.find_elements(By.CSS_SELECTOR, ".bet-row, .value-bet"))
                    message = f"🎯 {bet_count} value bets detected on RebelBetting!\n\nCheck your dashboard: {LOGIN_URL}"
                    print(f"📱 Sending notification for {bet_count} bets...")
                    notifier.notify("Value Bets Available!", message)
            except Exception as e:
                print(f"⚠️  Could not find odds card: {e}")
                # Debug: Print available elements
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text[:200]
                    print(f"Page content preview: {body_text}...")
                except:
                    pass
            
            print(f"💤 Waiting 60 seconds before next check...")
            time.sleep(60)
            # Refresh the page to check for new bets
            print("🔄 Refreshing page...")
            driver.refresh()
            
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal, shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("🧹 Cleaning up Chrome driver...")
            try:
                driver.quit()
            except:
                pass
        print("👋 Goodbye!")
        """Initialize and return Chrome driver"""
        print("🚀 Starting Chrome driver...")
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
        
        try:
            print("⏳ Initializing Chrome (this may take 30-60 seconds)...")
            # Don't use webdriver-manager, let undetected-chrome handle it
            driver = uc.Chrome(options=options)
            print("✅ Chrome driver initialized successfully")
            
            driver.implicitly_wait(IMPLICIT_WAIT)
            
            # Navigate to login page immediately
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
        """Attempt automated login with detailed debugging"""
        print(f"Starting automated login for user: {username}")
        driver.get(LOGIN_URL)
        try:
            WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            print("✓ Page loaded completely")
            time.sleep(random.uniform(0.3, 0.6))
            
            # Debug: Print page title and URL
            print(f"Current URL: {driver.current_url}")
            print(f"Page title: {driver.title}")
            
            # Debug: Check if login form exists
            try:
                user_input = driver.find_element(By.ID, "inputEmail")
                print("✓ Found email input field")
            except NoSuchElementException:
                print("✗ Email input field not found")
                print("Available input fields:")
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for i, inp in enumerate(inputs):
                    print(f"  Input {i}: type='{inp.get_attribute('type')}', id='{inp.get_attribute('id')}', name='{inp.get_attribute('name')}'")
                return False
            
            try:
                pass_input = driver.find_element(By.ID, "inputPassword")
                print("✓ Found password input field")
            except NoSuchElementException:
                print("✗ Password input field not found")
                return False
            
            # Fill in credentials
            print("Filling in email...")
            driver.execute_script('arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event("input", {bubbles:true})); arguments[0].dispatchEvent(new Event("change", {bubbles:true}));', user_input, username)
            time.sleep(random.uniform(0.3, 0.6))
            
            print("Filling in password...")
            driver.execute_script('arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event("input", {bubbles:true})); arguments[0].dispatchEvent(new Event("change", {bubbles:true}));', pass_input, password)
            time.sleep(random.uniform(0.3, 0.6))
            
            # Debug: Check if values were set
            email_value = driver.execute_script('return arguments[0].value;', user_input)
            print(f"Email field value: {email_value[:5]}...")  # Only show first 5 chars for security
            
            # Find and click submit button
            try:
                submit = driver.find_element(By.CSS_SELECTOR, "button[type=submit], button.btn-primary")
                print(f"✓ Found submit button: {submit.text}")
                
                # Check if button is disabled
                if submit.get_attribute("disabled"):
                    print("⚠️  Submit button is disabled, waiting for it to be enabled...")
                    # Wait a bit longer for form validation
                    time.sleep(2)
                    # Try to trigger form validation by clicking on the form or pressing tab
                    try:
                        pass_input.send_keys(Keys.TAB)
                        time.sleep(1)
                    except:
                        pass
                
                # Try JavaScript click if regular click fails
                try:
                    submit.click()
                    print("✓ Clicked submit button")
                except Exception as click_error:
                    print(f"Regular click failed: {click_error}")
                    print("Trying JavaScript click...")
                    driver.execute_script("arguments[0].click();", submit)
                    print("✓ JavaScript click successful")
                    
            except NoSuchElementException:
                print("✗ Submit button not found")
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print("Available buttons:")
                for i, btn in enumerate(buttons):
                    print(f"  Button {i}: text='{btn.text}', type='{btn.get_attribute('type')}', class='{btn.get_attribute('class')}', disabled='{btn.get_attribute('disabled')}'")
                return False
            
            time.sleep(random.uniform(2, 4))  # Wait for login to process
            
            # Debug: Check URL after login attempt
            print(f"URL after login attempt: {driver.current_url}")
            print(f"Page title after login: {driver.title}")
            
            # Check for error messages
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".alert, .error, [class*='error'], [class*='invalid']")
                if error_elements:
                    print("Found potential error messages:")
                    for err in error_elements:
                        if err.text.strip():
                            print(f"  Error: {err.text}")
            except:
                pass
            
            # Check if login was successful by looking for dashboard elements
            try:
                WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".odds-card")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='dashboard']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='bet']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='value']"))
                    )
                )
                print("✓ Login appears successful - dashboard elements found")
                return True
            except TimeoutException:
                print("✗ Login may have failed - no dashboard elements found")
                # Debug: Print page source snippet
                page_text = driver.find_element(By.TAG_NAME, "body").text[:500]
                print(f"Page content preview: {page_text}...")
                return False
                
        except TimeoutException:
            print("✗ Timed out waiting for login form")
            return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            import traceback
            traceback.print_exc()
            return False
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
            login_success = automated_login(driver, username, password)
            if not login_success:
                print("Automated login failed, but continuing to monitor anyway...")
        else:
            print("REBEL_USERNAME not found in env — continuing without login.")

        print("Starting betting monitor loop...")
        
        #check if there actually are any bet cards 
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        print("Page loaded. Waiting extra seconds for scripts...")
        time.sleep(random.uniform(0.3, 0.6))
        time.sleep(0.5)  # Wait for potential dynamic content to load
        
        loop_count = 0
        while True:  
            loop_count += 1
            print(f"\n--- Monitor Loop #{loop_count} ---")
            print(f"Current URL: {driver.current_url}")
            
            WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            print("✓ Page loaded completely")
            time.sleep(random.uniform(0.3, 0.6))
            
            # Close backdrop popups if present (attempt multiple selectors)
            try:
                # WHAT IS THE CORRECT HTML SELECTOR FOR REBEL BETTING POPUPS?
                popup_close = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[data-testid='CloseLargeOutlinedIcon']"))
                )
                popup_close.click()
                print("✓ Closed BetMGM popup")
                time.sleep(random.uniform(0.3, 0.6))
            except:
                pass
            
            try:
                # Check if the odds-card contains "No value bets" message
                odds_card = driver.find_element(By.CSS_SELECTOR, ".odds-card")
                print(f"✓ Found odds card with text: {odds_card.text[:100]}...")
                
                if "No value bets" in odds_card.text:
                    print("ℹ️  No value bets available with current filters")
                else:
                    print("🎯 Value bets found! Proceeding with pinging...")
                    # Send notification when bets are found
                    bet_count = len(driver.find_elements(By.CSS_SELECTOR, ".bet-row, .value-bet"))
                    message = f"🎯 {bet_count} value bets detected on RebelBetting!\n\nCheck your dashboard: {LOGIN_URL}"
                    print(f"Sending notification for {bet_count} bets...")
                    notifier.notify("Value Bets Available!", message)
            except Exception as e:
                print(f"⚠️  Could not find odds card: {e}")
                # Debug: Print available elements
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text[:200]
                    print(f"Page content preview: {body_text}...")
                except:
                    pass
            
            print(f"💤 Waiting 60 seconds before next check...")
            time.sleep(60)
            # Refresh the page to check for new bets
            print("🔄 Refreshing page...")
            driver.refresh()
            
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal, shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("🧹 Cleaning up Chrome driver...")
            try:
                driver.quit()
            except:
                pass
        print("👋 Goodbye!")
    
if __name__ == '__main__':
    main()