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
# from pushbullet import Pushbullet  # Temporarily disabled - causes freeze

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from config import LOGIN_URL, HEADLESS, IMPLICIT_WAIT, STAKE_AMOUNT, ACCUMULATED_STAKE

dotenv.load_dotenv()

def solve_math_challenge(question_text):
    """Solve simple math challenges like '5 + 3 = ?' or 'What is 7 - 2?'"""
    try:
        import re
        
        print(f"🧮 Parsing math question: {question_text}")
        
        # Clean the text
        text = question_text.lower().strip()
        
        # Pattern 1: "5 + 3 = ?" or "5 + 3 ="
        pattern1 = r'(\d+)\s*([+\-*×])\s*(\d+)\s*=\s*\??'
        match = re.search(pattern1, text)
        
        if match:
            num1, operator, num2 = match.groups()
            num1, num2 = int(num1), int(num2)
            
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator in ['*', '×']:
                result = num1 * num2
            else:
                return None
                
            print(f"🧮 Solved: {num1} {operator} {num2} = {result}")
            return result
        
        # Pattern 2: "What is 7 - 2?" or "Calculate 5 + 3"
        pattern2 = r'(\d+)\s*([+\-*×])\s*(\d+)'
        match = re.search(pattern2, text)
        
        if match:
            num1, operator, num2 = match.groups()
            num1, num2 = int(num1), int(num2)
            
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator in ['*', '×']:
                result = num1 * num2
            else:
                return None
                
            print(f"🧮 Solved: {num1} {operator} {num2} = {result}")
            return result
        
        print(f"❌ Could not parse math question: {question_text}")
        return None
        
    except Exception as e:
        print(f"❌ Math solving error: {e}")
        return None

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
        # Temporarily disabled - pushbullet causes freeze on Windows
        print(f"Pushbullet disabled: {title} - {message}")
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
    
    # Disable headless mode - using virtual display instead
    # options.add_argument("--headless=new")
    
    # Essential Chrome arguments for virtual display
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    
    # Virtual display optimizations
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-extensions")
    
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.popups": 1
    })
    
    print("⏳ Initializing Chrome (this may take 30-60 seconds)...")
    
    try:
        print("🔄 Creating Chrome instance...")
        import sys
        sys.stdout.flush()  # Force flush before potentially blocking operation
        
        # Windows doesn't support SIGALRM, so skip timeout for now
        driver = uc.Chrome(options=options)
        print("✅ Chrome driver initialized successfully")
        
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
        time.sleep(random.uniform(1.0, 2.5))  # Random human-like delay
        
        print("🔐 Filling password field...")
        # Fill password field using send_keys (triggers validation)
        pass_input.send_keys(password)
        print(f"✅ Password field filled (length: {len(pass_input.get_attribute('value'))})")
        time.sleep(random.uniform(1.0, 2.0))  # Random human-like delay
        
        print("⌨️ Triggering validation with Tab key...")
        # Trigger validation by pressing tab
        pass_input.send_keys(Keys.TAB)
        time.sleep(random.uniform(1.5, 3.0))  # Random wait for validation
        
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
        time.sleep(random.uniform(4, 7))  # Longer random wait for login processing
        
        current_url = driver.current_url
        print(f"📍 URL after login attempt: {current_url}")
        
        # Check for math challenge/CAPTCHA first
        print("🔍 Checking for math challenge...")
        try:
            # Look for common math challenge patterns
            math_selectors = [
                "input[placeholder*='math']",
                "input[placeholder*='challenge']", 
                "input[placeholder*='captcha']",
                "input[name*='math']",
                "input[name*='challenge']",
                "input[name*='captcha']",
                ".math-challenge input",
                ".captcha input",
                ".challenge input",
                "input[type='text']:not([id='inputEmail']):not([id='inputPassword'])"
            ]
            
            math_input = None
            math_question = None
            
            for selector in math_selectors:
                try:
                    math_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found potential math input with selector: {selector}")
                    break
                except:
                    continue
            
            if math_input:
                # Look for the math question text
                print("🔍 Looking for math question text...")
                # Try to find question in various places
                question_selectors = [
                    "label[for='" + (math_input.get_attribute('id') or '') + "']",
                    ".math-challenge",
                    ".captcha",
                    ".challenge",
                    "p", "div", "span"
                ]
                
                for selector in question_selectors:
                    try:
                        question_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in question_elements:
                            text = element.text.strip()
                            # Look for math patterns in the text
                            if text and any(op in text for op in ['+', '-', '*', '×', '=', 'What is', 'Calculate']):
                                math_question = text
                                print(f"✅ Found math question: {math_question}")
                                break
                        if math_question:
                            break
                    except:
                        continue
                
                # If no specific question found, look around the input and check page source
                if not math_question:
                    try:
                        # Check the entire page for math patterns
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        lines = page_text.split('\n')
                        for line in lines:
                            if any(op in line for op in ['+', '-', '*', '×']) and any(char.isdigit() for char in line):
                                if 'What is' in line or any(op + ' ' in line for op in ['+', '-', '*', '×']):
                                    math_question = line.strip()
                                    print(f"🔍 Found math question in page: {math_question}")
                                    break
                    except:
                        pass
                
                if math_question:
                    print(f"🧮 Solving math challenge: {math_question}")
                    answer = solve_math_challenge(math_question)
                    
                    if answer is not None:
                        print(f"✅ Math answer: {answer}")
                        
                        # Try multiple ways to input the answer
                        try:
                            # Method 1: Clear and send keys
                            math_input.clear()
                            math_input.send_keys(str(answer))
                            print("✅ Method 1: send_keys successful")
                        except Exception as e1:
                            print(f"❌ Method 1 failed: {e1}")
                            try:
                                # Method 2: JavaScript input
                                driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true})); arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", math_input, str(answer))
                                print("✅ Method 2: JavaScript input successful")
                            except Exception as e2:
                                print(f"❌ Method 2 failed: {e2}")
                                try:
                                    # Method 3: Focus and type
                                    driver.execute_script("arguments[0].focus();", math_input)
                                    time.sleep(0.5)
                                    math_input.send_keys(str(answer))
                                    print("✅ Method 3: Focus and type successful")
                                except Exception as e3:
                                    print(f"❌ Method 3 failed: {e3}")
                                    print("❌ All input methods failed")
                                    return False
                        
                        time.sleep(random.uniform(0.8, 1.5))  # Random delay after input
                        
                        # Look for submit button for the challenge
                        try:
                            challenge_submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .challenge button, .math-challenge button")
                            challenge_submit.click()
                            print("✅ Submitted math challenge")
                            time.sleep(random.uniform(8, 12))  # Longer wait for processing
                        except:
                            # Try pressing Enter
                            try:
                                math_input.send_keys(Keys.RETURN)
                                print("✅ Pressed Enter on math input")
                                time.sleep(random.uniform(8, 12))  # Longer wait for processing
                            except:
                                # Try JavaScript submit
                                try:
                                    driver.execute_script("arguments[0].form.submit();", math_input)
                                    print("✅ JavaScript form submit")
                                    time.sleep(random.uniform(8, 12))  # Longer wait for processing
                                except:
                                    print("⚠️  Could not submit math challenge")
                        
                        # Check if page redirected automatically
                        current_url = driver.current_url
                        print(f"📍 URL after math challenge: {current_url}")
                        
                        # If still on login page, try refreshing and checking again
                        if "login" in current_url.lower():
                            print("🔄 Still on login page, trying page refresh...")
                            driver.refresh()
                            time.sleep(random.uniform(3, 5))
                            
                            # Check URL again after refresh
                            current_url = driver.current_url
                            print(f"📍 URL after refresh: {current_url}")
                            
                            # If still on login, maybe the math challenge needs to be solved again
                            if "login" in current_url.lower():
                                print("⚠️  Still on login page after refresh - math challenge may need re-solving")
                        
                        # Re-check URL after math challenge
                        current_url = driver.current_url
                        print(f"📍 Final URL after math challenge: {current_url}")
                    else:
                        print("❌ Could not solve math challenge")
                        return False
                else:
                    print("❌ Found math input but no question text")
                    # Try to get placeholder or any hint
                    placeholder = math_input.get_attribute('placeholder')
                    if placeholder:
                        print(f"🔍 Input placeholder: {placeholder}")
            else:
                print("ℹ️  No math challenge detected")
                
        except Exception as e:
            print(f"🔍 Math challenge check error: {e}")
        
        # Final check - are we still on login page?
        current_url = driver.current_url
        print(f"📍 Final URL check: {current_url}")
        
        # Check if we're still on login page (failed) or redirected (success)
        if "login" in current_url.lower():
            print("❌ Still on login page - login failed")
            
            # Look for specific error messages
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
                # Look for odds cards specifically
                odds_cards = driver.find_elements(By.CSS_SELECTOR, ".odds-card")
                
                if odds_cards:
                    print(f"✅ Found {len(odds_cards)} odds card(s)")
                    
                    # Check if there are actual bets or just "no bets" message
                    first_card = odds_cards[0]
                    card_text = first_card.text.lower()
                    
                    if "no value bets" in card_text or "no bets" in card_text:
                        print("ℹ️  No value bets available")
                    else:
                        print("🎯 Value bets found!")
                        
                        # Extract details from up to 10 bet cards
                        bet_details = []
                        cards_to_process = min(len(odds_cards), 10)
                        
                        for i, card in enumerate(odds_cards[:cards_to_process]):
                            try:
                                # Extract value percentage
                                value_element = card.find_element(By.CSS_SELECTOR, ".text-valuebet")
                                value_percent = value_element.text.strip()
                                
                                # Extract bet description (match info)
                                bet_desc_element = card.find_element(By.CSS_SELECTOR, ".odds-card-text span")
                                bet_description = bet_desc_element.text.strip()
                                
                                # Extract league/sport
                                league_elements = card.find_elements(By.CSS_SELECTOR, ".text-muted div")
                                league = league_elements[0].text.strip() if league_elements else "Unknown"
                                
                                # Extract bookmaker and time
                                time_book_elements = card.find_elements(By.CSS_SELECTOR, ".text-muted span")
                                time_left = ""
                                bookmaker = ""
                                if len(time_book_elements) >= 2:
                                    time_left = time_book_elements[0].text.strip()
                                    bookmaker = time_book_elements[1].text.strip()
                                
                                bet_info = {
                                    'value': value_percent,
                                    'description': bet_description,
                                    'league': league,
                                    'time_left': time_left,
                                    'bookmaker': bookmaker
                                }
                                
                                bet_details.append(bet_info)
                                print(f"📊 Bet {i+1}: {value_percent} - {bet_description} ({bookmaker})")
                                
                            except Exception as e:
                                print(f"⚠️  Could not extract details from bet card {i+1}: {e}")
                        
                        if bet_details:
                            # Create detailed notification message with shorter lines for Telegram
                            message_lines = [f"🎯 {len(bet_details)} Value Bets Found!"]
                            message_lines.append("")  # Empty line
                            
                            for i, bet in enumerate(bet_details, 1):
                                # Truncate long descriptions to prevent wrapping
                                description = bet['description']
                                if len(description) > 35:
                                    description = description[:32] + "..."
                                
                                # Truncate bookmaker if too long
                                bookmaker = bet['bookmaker']
                                if len(bookmaker) > 12:
                                    bookmaker = bookmaker[:9] + "..."
                                
                                # Use shorter formatting
                                message_lines.append(f"{i}. {bet['value']}")
                                message_lines.append(f"• {description}")
                                message_lines.append(f"• {bet['league']} | {bookmaker}")
                                message_lines.append(f"• {bet['time_left']}")
                                message_lines.append("")  # Empty line between bets
                            
                            message_lines.append(f"🔗 Check RebelBetting")
                            
                            detailed_message = "\n".join(message_lines)
                            
                            print(f"📱 Sending detailed notification for {len(bet_details)} bets...")
                            notifier.notify("Value Bets Available!", detailed_message)
                        else:
                            print("⚠️  Found cards but could not extract bet details")
                else:
                    print("❌ No odds cards found")
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
                        print(f"⚠️  No odds cards found on page: {current_url}")
                            
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
            
            print("💤 Waiting 5 minutes...")
            sys.stdout.flush()
            time.sleep(300)  # 5 minutes = 300 seconds
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