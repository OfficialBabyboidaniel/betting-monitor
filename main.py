import time
import os
import random
import signal
import sys
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
    print("🔧 Setting up Chrome options...")
    
    options = uc.ChromeOptions()
    
    # Essential Docker Chrome arguments
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    
    # Memory and performance optimizations for containers
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")
    
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.popups": 1
    })
    
    print("⏳ Initializing Chrome (this may take 30-60 seconds)...")
    
    try:
        print("🔄 Creating Chrome instance...")
        import sys
        sys.stdout.flush()  # Force flush before potentially blocking operation
        
        # Add timeout mechanism
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Chrome initialization timed out after 120 seconds")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(120)  # 2 minute timeout
        
        try:
            driver = uc.Chrome(options=options)
            signal.alarm(0)  # Cancel timeout
            print("✅ Chrome driver initialized successfully")
        except TimeoutError:
            print("❌ Chrome initialization timed out - this usually indicates Chrome can't start in container")
            raise
        
        driver.implicitly_wait(IMPLICIT_WAIT)
        
        print(f"🌐 Navigating to login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        print("✅ Page loaded successfully!")
        return driver
        
    except Exception as e:
        print(f"❌ Failed to start Chrome driver: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Try alternative approach with regular selenium
        print("🔄 Attempting fallback to regular selenium Chrome...")
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            
            service = Service()
            fallback_options = webdriver.ChromeOptions()
            fallback_options.add_argument("--headless=new")
            fallback_options.add_argument("--no-sandbox")
            fallback_options.add_argument("--disable-dev-shm-usage")
            fallback_options.add_argument("--disable-gpu")
            
            fallback_driver = webdriver.Chrome(service=service, options=fallback_options)
            print("✅ Fallback Chrome driver initialized")
            return fallback_driver
            
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            raise e

def debug_page_content(driver):
    """Debug function to understand page content"""
    try:
        print(f"🔍 Debug - Current URL: {driver.current_url}")
        print(f"🔍 Debug - Page title: {driver.title}")
        
        # Check for common elements
        common_selectors = [
            "h1", "h2", ".card", ".content", ".main", 
            "[class*='bet']", "[class*='odds']", ".alert", ".error"
        ]
        
        for selector in common_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"🔍 Found {len(elements)} elements with selector '{selector}'")
                    if elements[0].text.strip():
                        preview = elements[0].text.strip()[:50]
                        print(f"   First element text: {preview}...")
            except:
                pass
                
    except Exception as e:
        print(f"🔍 Debug error: {e}")

def automated_login(driver, username, password):
    """Attempt automated login with proper validation triggering + debug logs"""
    print(f"🔑 Starting automated login for user: {username}")
    driver.get(LOGIN_URL)
    try:
        print("⏳ Waiting for page to load completely...")
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        print("✅ Page loaded completely")
        print(f"📍 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        time.sleep(random.uniform(2, 3))  # Give more time for page to fully load
        
        # Check for any existing error messages
        try:
            error_msg = driver.find_element(By.CSS_SELECTOR, ".alert-danger, .error, .invalid-feedback")
            print(f"⚠️  Found error message: {error_msg.text}")
        except:
            print("✅ No existing error messages found")
        
        print("🔍 Looking for email input field...")
        try:
            user_input = driver.find_element(By.ID, "inputEmail")
            print("✅ Found email input field")
        except NoSuchElementException:
            print("❌ Email input field not found")
            return False
        
        print("🔍 Looking for password input field...")
        try:
            pass_input = driver.find_element(By.ID, "inputPassword")
            print("✅ Found password input field")
        except NoSuchElementException:
            print("❌ Password input field not found")
            return False
        
        print("🧹 Clearing fields first...")
        # Clear fields first
        user_input.clear()
        pass_input.clear()
        time.sleep(0.5)
        
        print("📝 Filling email field...")
        # Fill email field using send_keys (triggers validation)
        user_input.send_keys(username)
        print(f"✅ Email set to: {user_input.get_attribute('value')}")
        time.sleep(random.uniform(0.5, 1.0))
        
        print("🔐 Filling password field...")
        # Fill password field using send_keys (triggers validation)
        pass_input.send_keys(password)
        print(f"✅ Password field filled (length: {len(pass_input.get_attribute('value'))})")
        time.sleep(random.uniform(0.5, 1.0))
        
        print("⌨️ Triggering validation with Tab key...")
        # Trigger validation by pressing tab
        pass_input.send_keys(Keys.TAB)
        time.sleep(1)
        
        print("🔍 Looking for submit button...")
        try:
            submit = driver.find_element(By.CSS_SELECTOR, "button[type=submit], button.btn-primary")
            print(f"✅ Found submit button: '{submit.text}'")
            print(f"🔍 Button enabled: {not submit.get_attribute('disabled')}")
            print(f"🔍 Button classes: {submit.get_attribute('class')}")
            
            # Wait a bit more if still disabled
            if submit.get_attribute("disabled"):
                print("⚠️  Submit button still disabled, waiting and trying to trigger validation...")
                pass_input.send_keys(Keys.TAB)
                time.sleep(2)
                
                # Check again
                if submit.get_attribute("disabled"):
                    print("⚠️  Button still disabled, trying to submit anyway...")
            
            print("🖱️ Attempting to click submit button...")
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", submit)
                time.sleep(0.5)
                submit.click()
                print("✅ Submit button clicked successfully")
            except Exception as click_error:
                print(f"❌ Regular click failed: {click_error}")
                print("🔄 Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", submit)
                print("✅ JavaScript click successful")
                
        except NoSuchElementException:
            print("❌ Submit button not found - trying Enter key...")
            # Try pressing Enter on password field
            try:
                print("⌨️ Pressing Enter on password field...")
                pass_input.send_keys(Keys.RETURN)
                print("✅ Enter key pressed on password field")
            except Exception as e:
                print(f"❌ Enter key failed: {e}")
                return False
        
        # Wait for navigation or error
        print("⏳ Waiting for login response...")
        time.sleep(random.uniform(0.3, 0.6))
        
        current_url = driver.current_url
        print(f"📍 URL after login attempt: {current_url}")
        
        # Check if we're still on login page (failed) or redirected (success)
        if "login" in current_url.lower():
            print("❌ Still on login page - login failed")
            
            # Check for error messages
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".alert, .error, .invalid-feedback, .text-danger")
                if error_elements:
                    for error in error_elements:
                        if error.text.strip():
                            print(f"🚨 Error message found: {error.text}")
                else:
                    print("🔍 No error messages found on page")
            except Exception as e:
                print(f"🔍 Error checking failed: {e}")
            
            return False
        else:
            print("✅ Redirected from login page - login appears successful!")
            return True
        
    except TimeoutException:
        print("⏰ Timed out waiting for login form")
        return False
    except NoSuchElementException as e:
        print(f"❌ Could not find required element: {e}")
        return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎯 Starting Rebel Betting Monitor...")
    notifier = NotificationService()
    driver = None
    
    try:
        print("🔄 Attempting to start Chrome driver...")
        sys.stdout.flush()
        
        driver = start_driver()
        print("✅ Chrome driver started successfully")
        
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
            print(f"📍 Current URL: {driver.current_url}")
            sys.stdout.flush()
            
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
                # Try multiple selectors for the betting content
                odds_card = None
                selectors_to_try = [
                    ".odds-card",
                    ".value-bet",
                    ".betting-card", 
                    "[class*='bet']",
                    "[class*='odds']",
                    ".card",
                    ".content"
                ]
                
                for selector in selectors_to_try:
                    try:
                        odds_card = driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"✓ Found content with selector: {selector}")
                        break
                    except:
                        continue
                
                if odds_card:
                    card_text = odds_card.text.lower()
                    print(f"📄 Content preview: {card_text[:100]}...")
                    
                    if "no value bets" in card_text or "no bets" in card_text:
                        print("ℹ️  No value bets available")
                    elif "value bet" in card_text or "bet" in card_text:
                        print("🎯 Potential value bets found!")
                        bet_elements = driver.find_elements(By.CSS_SELECTOR, ".bet-row, .value-bet, [class*='bet']")
                        bet_count = len(bet_elements)
                        message = f"🎯 {bet_count} potential value bets detected!\n\nCheck: {driver.current_url}"
                        print(f"📱 Sending notification for {bet_count} bets...")
                        notifier.notify("Value Bets Available!", message)
                    else:
                        print("ℹ️  Content found but no clear bet indicators")
                else:
                    # Check if we're on login page
                    current_url = driver.current_url
                    if "login" in current_url.lower():
                        print("⚠️  Back on login page - session may have expired")
                        if username and password:
                            print("🔄 Attempting to re-login...")
                            login_success = automated_login(driver, username, password)
                            if login_success:
                                continue  # Skip this loop iteration and try again
                    else:
                        print(f"⚠️  No recognizable content found on page: {current_url}")
                        # Try to navigate to the main betting page
                        try:
                            main_page = "https://vb.rebelbetting.com/"
                            print(f"🔄 Navigating to main page: {main_page}")
                            driver.get(main_page)
                            time.sleep(3)
                        except:
                            pass
                            
            except Exception as e:
                print(f"⚠️  Error during monitoring: {e}")
                # Check if we need to re-login
                try:
                    if "login" in driver.current_url.lower():
                        print("🔄 Detected login page, attempting re-login...")
                        if username and password:
                            automated_login(driver, username, password)
                except:
                    pass
            
            print("💤 Waiting 60 seconds...")
            sys.stdout.flush()
            time.sleep(60)
            print("🔄 Refreshing...")
            driver.refresh()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Send error notification
        try:
            error_message = f"❌ Betting Monitor Error: {str(e)[:200]}"
            notifier.notify("Monitor Error", error_message)
        except:
            pass
            
    finally:
        if driver:
            print("🧹 Cleaning up...")
            try:
                driver.quit()
            except:
                pass
        print("👋 Goodbye!")
        sys.stdout.flush()

if __name__ == '__main__':
    print("🐍 Python script starting...")
    print("📦 Imports successful")
    print("🔧 About to call main()")
    main()
    print("✅ Main function completed")