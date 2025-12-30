#!/usr/bin/env python3
"""
Simple Chrome test script to debug Docker container issues
"""
import sys
import time

def test_chrome_basic():
    print("🧪 Testing basic Chrome functionality...")
    
    try:
        print("1️⃣ Testing undetected-chromedriver...")
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        print("   Creating Chrome instance...")
        sys.stdout.flush()
        
        driver = uc.Chrome(options=options)
        print("   ✅ undetected-chromedriver works!")
        
        print("   Testing navigation...")
        driver.get("https://www.google.com")
        print(f"   Page title: {driver.title}")
        
        driver.quit()
        print("   ✅ Navigation successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ undetected-chromedriver failed: {e}")
        
        try:
            print("2️⃣ Testing regular selenium...")
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            
            service = Service()
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            driver = webdriver.Chrome(service=service, options=options)
            print("   ✅ Regular selenium works!")
            
            driver.get("https://www.google.com")
            print(f"   Page title: {driver.title}")
            
            driver.quit()
            print("   ✅ Regular selenium navigation successful!")
            return True
            
        except Exception as e2:
            print(f"   ❌ Regular selenium also failed: {e2}")
            return False

def test_system_info():
    print("🔍 System Information:")
    
    import os
    import subprocess
    
    print(f"   Python version: {sys.version}")
    print(f"   Platform: {sys.platform}")
    print(f"   User: {os.getenv('USER', 'unknown')}")
    
    try:
        chrome_version = subprocess.check_output(['google-chrome', '--version'], text=True).strip()
        print(f"   Chrome: {chrome_version}")
    except:
        print("   Chrome: Not found or not accessible")
    
    try:
        display = os.getenv('DISPLAY', 'Not set')
        print(f"   DISPLAY: {display}")
    except:
        pass

if __name__ == "__main__":
    print("🚀 Chrome Test Script Starting...")
    
    test_system_info()
    print()
    
    success = test_chrome_basic()
    
    if success:
        print("\n✅ Chrome test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Chrome test failed!")
        sys.exit(1)