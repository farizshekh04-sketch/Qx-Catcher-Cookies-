#!/usr/bin/env python3
# ============================================================
# QUOTEX COOKIE EXTRACTOR - TERMUX COMPLETE SOLUTION
# ============================================================

import json
import time
import os
import sys
import subprocess
from datetime import datetime
import base64
import re

# ============================================================
# TERMUX SETUP AND DEPENDENCY CHECK
# ============================================================

def check_termux_dependencies():
    """Check and install required dependencies for Termux"""
    print("🔍 Checking Termux dependencies...")
    
    # Check for required packages
    packages = {
        'chromium': 'chromium',
        'python': 'python',
        'pip': 'python-pip'
    }
    
    missing = []
    for pkg, name in packages.items():
        try:
            subprocess.run(['which', pkg], capture_output=True, check=True)
            print(f"✅ {pkg} installed")
        except subprocess.CalledProcessError:
            missing.append(name)
    
    if missing:
        print(f"📦 Installing missing packages: {', '.join(missing)}")
        for pkg in missing:
            subprocess.run(['pkg', 'install', pkg, '-y'], check=True)
    
    # Install Python packages
    try:
        import selenium
    except ImportError:
        print("📦 Installing selenium...")
        subprocess.run(['pip', 'install', 'selenium'], check=True)
    
    try:
        import webdriver_manager
    except ImportError:
        print("📦 Installing webdriver-manager...")
        subprocess.run(['pip', 'install', 'webdriver-manager'], check=True)

def check_chromedriver_termux():
    """Setup ChromeDriver for Termux"""
    chromedriver_path = "/data/data/com.termux/files/usr/bin/chromedriver"
    
    if not os.path.exists(chromedriver_path):
        print("📦 Installing ChromeDriver for Termux...")
        try:
            # Download Chromedriver for ARM
            url = "https://github.com/termux/termux-packages/raw/master/packages/chromedriver/chromedriver"
            subprocess.run(['curl', '-L', url, '-o', chromedriver_path], check=True)
            subprocess.run(['chmod', '+x', chromedriver_path], check=True)
            print("✅ ChromeDriver installed")
        except Exception as e:
            print(f"⚠️ Could not install ChromeDriver: {e}")
            return False
    else:
        print("✅ ChromeDriver found")
    return True

# ============================================================
# TERMUX WEB DRIVER WRAPPER
# ============================================================

class TermuxWebDriver:
    """Custom WebDriver for Termux environment"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver for Termux"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            
            # Termux specific options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--silent')
            
            # Disable automation flags
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Try different Chromedriver paths
            chromedriver_paths = [
                "/data/data/com.termux/files/usr/bin/chromedriver",
                "/data/data/com.termux/files/usr/lib/chromium/chromedriver",
                "chromedriver"
            ]
            
            service = None
            for path in chromedriver_paths:
                try:
                    service = Service(executable_path=path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                    print("✅ Chrome driver initialized")
                    return True
                except:
                    continue
            
            # Fallback to regular Chrome
            try:
                self.driver = webdriver.Chrome(options=options)
                print("✅ Chrome driver initialized (fallback)")
                return True
            except:
                pass
            
            print("❌ Could not initialize Chrome driver")
            return False
            
        except Exception as e:
            print(f"❌ Driver initialization error: {e}")
            return False
    
    def get(self, url):
        if self.driver:
            self.driver.get(url)
    
    def get_cookies(self):
        if self.driver:
            return self.driver.get_cookies()
        return []
    
    def add_cookie(self, cookie):
        if self.driver:
            self.driver.add_cookie(cookie)
    
    def refresh(self):
        if self.driver:
            self.driver.refresh()
    
    def current_url(self):
        if self.driver:
            return self.driver.current_url
        return ""
    
    def quit(self):
        if self.driver:
            self.driver.quit()
    
    def find_element(self, by, value):
        if self.driver:
            return self.driver.find_element(by, value)
        return None
    
    def execute_script(self, script):
        if self.driver:
            return self.driver.execute_script(script)
        return None

# ============================================================
# QUOTEX COOKIE EXTRACTOR FOR TERMUX
# ============================================================

class QuotexTermuxExtractor:
    """Quotex cookie extractor optimized for Termux"""
    
    def __init__(self):
        self.driver = None
        self.cookies_file = "quotex_cookies.json"
        self.setup_termux()
    
    def setup_termux(self):
        """Setup Termux environment"""
        print("="*60)
        print("🍪 QUOTEX COOKIE EXTRACTOR - TERMUX")
        print("="*60)
        
        # Check dependencies
        check_termux_dependencies()
        
        # Setup ChromeDriver
        if not check_chromedriver_termux():
            print("⚠️ ChromeDriver setup failed. Trying alternative method...")
        
        # Initialize driver
        self.driver = TermuxWebDriver()
        if not self.driver.driver:
            print("\n❌ Failed to initialize browser. Trying alternative approach...")
            self.use_alternative_method()
    
    def use_alternative_method(self):
        """Alternative method using direct HTTP requests"""
        print("🔄 Using alternative method (requests based)...")
        try:
            import requests
            self.session = requests.Session()
            self.use_requests = True
            print("✅ Using requests-based method")
            return True
        except ImportError:
            print("❌ Requests not available")
            self.use_requests = False
            return False
    
    def login_with_requests(self, email, password):
        """Login using requests (alternative method)"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            print("🌐 Logging in via requests...")
            
            # Get login page
            session = requests.Session()
            response = session.get("https://market-qx.trade/en/sign-in")
            
            # Extract CSRF token
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = None
            for input_tag in soup.find_all('input'):
                if input_tag.get('name') == '_token':
                    csrf_token = input_tag.get('value')
                    break
            
            if not csrf_token:
                print("⚠️ CSRF token not found, trying without...")
            
            # Prepare login data
            login_data = {
                'email': email,
                'password': password,
            }
            if csrf_token:
                login_data['_token'] = csrf_token
            
            # Login
            login_response = session.post(
                "https://market-qx.trade/en/sign-in",
                data=login_data,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36',
                    'Referer': 'https://market-qx.trade/en/sign-in'
                },
                allow_redirects=True
            )
            
            # Extract cookies
            cookies = session.cookies.get_dict()
            
            if cookies:
                print(f"✅ Login successful! Extracted {len(cookies)} cookies")
                self.cookies = cookies
                self.session = session
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Request login error: {e}")
            return False
    
    def login_quotex(self, email, password):
        """Login to Quotex using Selenium"""
        if hasattr(self, 'use_requests') and self.use_requests:
            return self.login_with_requests(email, password)
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print("🌐 Navigating to Quotex login...")
            self.driver.get("https://market-qx.trade/en/sign-in")
            time.sleep(3)
            
            try:
                # Try finding email field
                print("📧 Entering email...")
                email_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
                email_input.clear()
                email_input.send_keys(email)
                time.sleep(1)
                
                print("🔑 Entering password...")
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                password_input.clear()
                password_input.send_keys(password)
                time.sleep(1)
                
                print("🔄 Clicking login...")
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                time.sleep(5)
                
                # Check login success
                if "trade" in self.driver.current_url() or "dashboard" in self.driver.current_url():
                    print("✅ Login successful!")
                    return True
                else:
                    print("❌ Login failed. Check your credentials.")
                    return False
                    
            except Exception as e:
                print(f"❌ Login error: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Selenium login error: {e}")
            return False
    
    def extract_cookies(self):
        """Extract cookies from current session"""
        if hasattr(self, 'use_requests') and self.use_requests and hasattr(self, 'cookies'):
            return self.cookies
        
        try:
            cookies = self.driver.get_cookies()
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            return cookie_dict
        except Exception as e:
            print(f"❌ Cookie extraction error: {e}")
            return {}
    
    def decode_jwt(self, token):
        """Decode JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Decode payload
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)
            
        except Exception as e:
            return f"Error decoding: {e}"
    
    def save_cookies(self, cookies, filename=None):
        """Save cookies to file"""
        if filename is None:
            filename = self.cookies_file
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'platform': 'Termux',
            'cookies': cookies,
            'count': len(cookies)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Cookies saved to {filename}")
        return filename
    
    def load_cookies(self, filename=None):
        """Load cookies from file"""
        if filename is None:
            filename = self.cookies_file
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return data.get('cookies', {})
        except FileNotFoundError:
            print(f"❌ File {filename} not found")
            return {}
    
    def display_cookies(self, cookies):
        """Display cookies in readable format"""
        print("\n" + "="*60)
        print("🍪 QUOTEX COOKIES EXTRACTED")
        print("="*60)
        print(f"📊 Total: {len(cookies)} cookies")
        print("-"*60)
        
        for idx, (name, value) in enumerate(cookies.items(), 1):
            is_jwt = value.count('.') == 2 and len(value) > 50
            
            if len(value) > 100:
                display = value[:100] + "..."
            else:
                display = value
            
            print(f"{idx:2}. {name}")
            print(f"   → {display}")
            if is_jwt:
                print("   🔐 JWT Token detected")
                # Try to decode
                decoded = self.decode_jwt(value)
                if decoded and isinstance(decoded, dict):
                    print(f"   📋 Decoded: {json.dumps(decoded, indent=2)[:200]}...")
            print("-"*60)
    
    def run(self, email=None, password=None):
        """Main execution method"""
        print("\n" + "="*60)
        print("🚀 STARTING COOKIE EXTRACTION")
        print("="*60 + "\n")
        
        # Get credentials if not provided
        if not email:
            email = input("📧 Quotex Email: ").strip()
        if not password:
            password = input("🔑 Quotex Password: ").strip()
        
        if not email or not password:
            print("❌ Email and password are required")
            return None
        
        # Login
        if not self.login_quotex(email, password):
            print("❌ Login failed")
            return None
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Extract cookies
        cookies = self.extract_cookies()
        
        if cookies:
            self.display_cookies(cookies)
            self.save_cookies(cookies)
            
            # Check for important cookies
            important = ['session', 'token', 'user_id', 'auth']
            found = [k for k in important if k in cookies]
            if found:
                print(f"\n✅ Key cookies found: {', '.join(found)}")
            
            return cookies
        else:
            print("❌ No cookies found")
            return None
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

# ============================================================
# COOKIE INJECTOR FOR TERMUX
# ============================================================

class QuotexTermuxInjector:
    """Inject cookies to auto-login in Termux"""
    
    def __init__(self):
        self.driver = TermuxWebDriver()
        self.cookies_file = "quotex_cookies.json"
    
    def inject_cookies(self):
        """Inject cookies to login automatically"""
        try:
            # Load cookies
            with open(self.cookies_file, 'r') as f:
                data = json.load(f)
                cookies = data.get('cookies', {})
            
            if not cookies:
                print("❌ No cookies found in file")
                return False
            
            print("🌐 Navigating to Quotex...")
            self.driver.get("https://market-qx.trade/en/trade")
            time.sleep(3)
            
            # Add cookies
            for name, value in cookies.items():
                self.driver.add_cookie({'name': name, 'value': value})
            
            # Refresh page
            self.driver.refresh()
            time.sleep(3)
            
            print(f"✅ Injected {len(cookies)} cookies")
            print(f"🌐 Current URL: {self.driver.current_url()}")
            return True
            
        except Exception as e:
            print(f"❌ Injection error: {e}")
            return False
    
    def close(self):
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()

# ============================================================
# MAIN MENU
# ============================================================

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def main_menu():
    """Display main menu"""
    clear_screen()
    print("="*60)
    print("🍪 QUOTEX COOKIE EXTRACTOR - TERMUX")
    print("="*60)
    print("\n📋 Options:")
    print("  1. Extract Cookies (Login Required)")
    print("  2. Inject Cookies (Auto-Login)")
    print("  3. View Saved Cookies")
    print("  4. Decode JWT Token")
    print("  5. Clear Saved Cookies")
    print("  6. Exit")
    print("\n" + "-"*60)
    
    choice = input("👉 Enter choice (1-6): ").strip()
    return choice

def view_saved_cookies():
    """View saved cookies"""
    try:
        with open("quotex_cookies.json", 'r') as f:
            data = json.load(f)
        
        print("\n" + "="*60)
        print("📋 SAVED COOKIES")
        print("="*60)
        print(f"📅 Extracted: {data.get('timestamp', 'Unknown')}")
        print(f"📱 Platform: {data.get('platform', 'Unknown')}")
        print(f"📊 Count: {data.get('count', 0)}")
        print("-"*60)
        
        cookies = data.get('cookies', {})
        for idx, (name, value) in enumerate(cookies.items(), 1):
            display = value[:60] + "..." if len(value) > 60 else value
            print(f"{idx:2}. {name}: {display}")
        
        print("\n" + "="*60)
        input("\nPress Enter to continue...")
        
    except FileNotFoundError:
        print("❌ No saved cookies found. Run extraction first.")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(2)

def decode_jwt_menu():
    """Decode JWT token from saved cookies"""
    try:
        with open("quotex_cookies.json", 'r') as f:
            data = json.load(f)
        
        cookies = data.get('cookies', {})
        jwt_cookies = {k: v for k, v in cookies.items() if v.count('.') == 2 and len(v) > 50}
        
        if not jwt_cookies:
            print("❌ No JWT tokens found in saved cookies")
            time.sleep(2)
            return
        
        print("\n🔐 JWT Tokens Found:")
        for idx, (name, value) in enumerate(jwt_cookies.items(), 1):
            print(f"  {idx}. {name}")
        
        choice = input("\nSelect token to decode (1-{}): ".format(len(jwt_cookies))).strip()
        try:
            idx = int(choice) - 1
            name = list(jwt_cookies.keys())[idx]
            value = jwt_cookies[name]
            
            extractor = QuotexTermuxExtractor()
            decoded = extractor.decode_jwt(value)
            
            print("\n" + "="*60)
            print(f"🔐 Decoded JWT: {name}")
            print("="*60)
            print(json.dumps(decoded, indent=2))
            print("="*60)
            input("\nPress Enter to continue...")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            time.sleep(2)
            
    except FileNotFoundError:
        print("❌ No saved cookies found")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(2)

def clear_cookies():
    """Clear saved cookies"""
    confirm = input("⚠️ Are you sure you want to delete all saved cookies? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            os.remove("quotex_cookies.json")
            print("✅ Cookies cleared")
        except FileNotFoundError:
            print("❌ No cookies file found")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(2)
    else:
        print("Cancelled")
        time.sleep(1)

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Main function"""
    # Check if running in Termux
    is_termux = '/data/data/com.termux' in os.getenv('PREFIX', '')
    
    if is_termux:
        print("📱 Running in Termux environment")
    else:
        print("💻 Running in standard environment")
    
    while True:
        choice = main_menu()
        
        if choice == "1":
            # Extract cookies
            extractor = QuotexTermuxExtractor()
            try:
                email = input("📧 Quotex Email: ").strip()
                password = input("🔑 Quotex Password: ").strip()
                extractor.run(email, password)
            except KeyboardInterrupt:
                print("\n❌ Cancelled")
            finally:
                extractor.close()
                input("\nPress Enter to continue...")
                
        elif choice == "2":
            # Inject cookies
            injector = QuotexTermuxInjector()
            try:
                injector.inject_cookies()
                input("\nPress Enter to close browser...")
            except KeyboardInterrupt:
                print("\n❌ Cancelled")
            finally:
                injector.close()
                
        elif choice == "3":
            view_saved_cookies()
            
        elif choice == "4":
            decode_jwt_menu()
            
        elif choice == "5":
            clear_cookies()
            
        elif choice == "6":
            print("\n👋 Goodbye!")
            sys.exit(0)
            
        else:
            print("❌ Invalid choice")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
