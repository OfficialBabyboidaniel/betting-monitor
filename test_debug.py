#!/usr/bin/env python3
"""
Debug script to find where it's hanging
"""

print("🐍 Starting debug script...")

try:
    print("📦 Testing basic imports...")
    import time
    import os
    import random
    print("✅ Basic imports OK")
    
    print("📦 Testing dotenv...")
    import dotenv
    print("✅ dotenv OK")
    
    print("📦 Testing requests...")
    import requests
    print("✅ requests OK")
    
    print("📦 Testing selenium...")
    from selenium.webdriver.common.by import By
    print("✅ selenium OK")
    
    print("📦 Testing undetected_chromedriver...")
    import undetected_chromedriver as uc
    print("✅ undetected_chromedriver OK")
    
    print("📦 Testing pushbullet...")
    from pushbullet import Pushbullet
    print("✅ pushbullet OK")
    
    print("🔧 Testing Chrome options...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    print("✅ Chrome options OK")
    
    print("🚀 Testing Chrome driver creation...")
    driver = uc.Chrome(options=options)
    print("✅ Chrome driver created!")
    
    print("🌐 Testing navigation...")
    driver.get("https://www.google.com")
    print(f"✅ Page title: {driver.title}")
    
    driver.quit()
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error at: {e}")
    import traceback
    traceback.print_exc()