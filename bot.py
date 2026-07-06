#!/usr/bin/env python3
# ============================================================
# QUOTEX COOKIE EXTRACTOR - market-qx.trade
# 100% Working for Termux / Android / Any Platform
# ============================================================

import json
import time
import os
import sys
import re
import base64
from datetime import datetime
import urllib.parse

# ============================================================
# INSTALL DEPENDENCIES IF MISSING
# ============================================================

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    print("📦 Installing requests...")
    os.system('pip install requests')
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("📦 Installing beautifulsoup4...")
    os.system('pip install beautifulsoup4')
    from bs4 import BeautifulSoup

# ============================================================
# QUOTEX COOKIE EXTRACTOR - market-qx.trade VERSION
# ============================================================

class QuotexCookieExtractor:
    """Extract Quotex cookies using requests only"""
    
    def __init__(self):
        self.session = None
        self.cookies = {}
        # UPDATED: Using your specific login URL
        self.base_url = "https://market-qx.trade"
        self.login_url = f"{self.base_url}/en/sign-in"
        self.trade_url = f"{self.base_url}/en/trade"
        self.user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        self.setup_session()
        
    def setup_session(self):
        """Setup requests session with retry logic"""
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Retry strategy
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def get_csrf_token(self, html):
        """Extract CSRF token from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check meta tag
        meta = soup.find('meta', {'name': 'csrf-token'})
        if meta and meta.get('content'):
            return meta.get('content')
        
        # Check meta with different names
        meta = soup.find('meta', {'name': 'csrf-token'})
        if meta and meta.get('content'):
            return meta.get('content')
        
        # Check input field
        input_tag = soup.find('input', {'name': '_token'})
        if input_tag and input_tag.get('value'):
            return input_tag.get('value')
        
        # Check input field with different names
        for name in ['csrf_token', 'token', 'authenticity_token']:
            input_tag = soup.find('input', {'name': name})
            if input_tag and input_tag.get('value'):
                return input_tag.get('value')
        
        # Check any token in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for token in JavaScript
                token_match = re.search(r'["\']csrfToken["\']\s*:\s*["\']([^"\']+)["\']', script.string)
                if token_match:
                    return token_match.group(1)
        
        # Check for token in JSON data
        for script in scripts:
            if script.string:
                token_match = re.search(r'XSRF-TOKEN["\']?\s*:\s*["\']([^"\']+)["\']', script.string)
                if token_match:
                    return token_match.group(1)
        
        return None
    
    def get_login_form_data(self, html):
        """Extract all form data needed for login"""
        soup = BeautifulSoup(html, 'html.parser')
        form_data = {}
        
        # Find all input fields in the form
        form = soup.find('form')
        if form:
            inputs = form.find_all('input')
            for input_tag in inputs:
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    form_data[name] = value
        
        return form_data
    
    def login(self, email, password):
        """Login to Quotex using requests"""
        try:
            print("🌐 Connecting to Quotex...")
            print(f"📍 URL: {self.login_url}")
            
            # Get login page to extract CSRF token
            response = self.session.get(self.login_url)
            
            if response.status_code != 200:
                print(f"❌ Failed to load login page: {response.status_code}")
                return False
            
            print(f"✅ Login page loaded (Status: {response.status_code})")
            
            # Extract CSRF token
            csrf_token = self.get_csrf_token(response.text)
            form_data = self.get_login_form_data(response.text)
            
            # Prepare login data
            login_data = {
                'email': email,
                'password': password,
            }
            
            # Add CSRF token if found
            if csrf_token:
                print(f"✅ CSRF token found: {csrf_token[:20]}...")
                # Try different field names
                if '_token' in form_data or csrf_token:
                    login_data['_token'] = csrf_token
                elif 'csrf_token' in form_data:
                    login_data['csrf_token'] = csrf_token
                elif 'authenticity_token' in form_data:
                    login_data['authenticity_token'] = csrf_token
                else:
                    login_data['_token'] = csrf_token
            else:
                print("⚠️ No CSRF token found, trying without...")
            
            # Add other form data
            for key, value in form_data.items():
                if key not in login_data and key not in ['email', 'password']:
                    login_data[key] = value
            
            # Login headers
            login_headers = {
                'Referer': self.login_url,
                'Origin': self.base_url,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            print("🔑 Attempting login...")
            
            # Perform login
            response = self.session.post(
                self.login_url,
                data=login_data,
                headers=login_headers,
                allow_redirects=True
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            # Check if login was successful
            if response.status_code in [200, 302, 303]:
                # Check if redirected to trade page
                if 'trade' in response.url or 'dashboard' in response.url:
                    print("✅ Login successful!")
                    self.cookies = self.session.cookies.get_dict()
                    return True
                
                # Check response content
                try:
                    json_response = response.json()
                    if json_response.get('success') or json_response.get('status') == 'success':
                        print("✅ Login successful!")
                        self.cookies = self.session.cookies.get_dict()
                        return True
                except:
                    pass
                
                # Check for error messages
                if 'error' in response.text.lower() or 'invalid' in response.text.lower() or 'incorrect' in response.text.lower():
                    # Extract error message
                    soup = BeautifulSoup(response.text, 'html.parser')
                    error_elem = soup.find(class_='error') or soup.find(class_='alert') or soup.find(class_='notification')
                    if error_elem:
                        print(f"❌ Login failed: {error_elem.text.strip()}")
                    else:
                        print("❌ Login failed: Invalid credentials")
                    return False
                
                # Check if we're logged in by looking for balance
                if 'usermenu__info-balance' in response.text or 'balance' in response.text.lower():
                    print("✅ Login successful!")
                    self.cookies = self.session.cookies.get_dict()
                    return True
                
                # If we got cookies, might be logged in
                if len(self.session.cookies.get_dict()) > 0:
                    print("✅ Login likely successful!")
                    self.cookies = self.session.cookies.get_dict()
                    return True
            
            print(f"❌ Login failed. Status: {response.status_code}")
            return False
            
        except requests.exceptions.ConnectionError:
            print("❌ Connection error. Check your internet connection.")
            return False
        except requests.exceptions.Timeout:
            print("❌ Connection timeout. Try again.")
            return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def extract_cookies(self):
        """Get all cookies from session"""
        if not self.cookies:
            self.cookies = self.session.cookies.get_dict()
        return self.cookies
    
    def get_balance(self):
        """Get account balance after login"""
        try:
            response = self.session.get(self.trade_url)
            if response.status_code == 200:
                # Try to find balance in HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try different selectors
                balance_selectors = [
                    '.usermenu__info-balance',
                    '.balance',
                    '[class*="balance"]',
                    '[class*="Balance"]',
                    '.user-balance'
                ]
                
                for selector in balance_selectors:
                    try:
                        balance_elem = soup.select_one(selector)
                        if balance_elem:
                            return balance_elem.text.strip()
                    except:
                        pass
                
                # Try to find in script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        balance_match = re.search(r'"balance"\s*:\s*"([^"]+)"', script.string)
                        if balance_match:
                            return balance_match.group(1)
                        
                        # Try to find in JSON
                        balance_match = re.search(r'balance["\']?\s*:\s*([0-9.]+)', script.string)
                        if balance_match:
                            return f"${balance_match.group(1)}"
                
                return "Balance not visible"
            return None
        except Exception as e:
            return f"Error getting balance: {e}"
    
    def decode_jwt(self, token):
        """Decode JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            payload = parts[1]
            # Add padding
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)
            
        except Exception as e:
            return f"Error: {e}"
    
    def save_cookies(self, filename="quotex_cookies.json"):
        """Save cookies to file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'platform': 'Termux',
            'url': self.login_url,
            'cookies': self.cookies,
            'count': len(self.cookies),
            'user_agent': self.user_agent
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Cookies saved to {filename}")
        return filename
    
    def load_cookies(self, filename="quotex_cookies.json"):
        """Load cookies from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return data.get('cookies', {})
        except FileNotFoundError:
            print(f"❌ File {filename} not found")
            return {}
    
    def display_cookies(self):
        """Display all cookies"""
        if not self.cookies:
            self.cookies = self.session.cookies.get_dict()
        
        print("\n" + "="*60)
        print("🍪 QUOTEX COOKIES EXTRACTED")
        print(f"📍 {self.login_url}")
        print("="*60)
        print(f"📊 Total: {len(self.cookies)} cookies")
        print("-"*60)
        
        for idx, (name, value) in enumerate(self.cookies.items(), 1):
            is_jwt = value.count('.') == 2 and len(value) > 50
            is_session = 'session' in name.lower() or 'token' in name.lower()
            display = value[:100] + "..." if len(value) > 100 else value
            
            # Determine icon
            if is_jwt:
                icon = "🔐"
            elif is_session:
                icon = "🟢"
            else:
                icon = "📄"
            
            print(f"{idx:2}. {icon} {name}")
            print(f"   → {display}")
            
            if is_jwt:
                print("   ⚡ JWT Token detected")
                decoded = self.decode_jwt(value)
                if decoded and isinstance(decoded, dict):
                    keys = ', '.join(list(decoded.keys())[:5])
                    if len(decoded.keys()) > 5:
                        keys += '...'
                    print(f"   📋 Contains: {keys}")
            print("-"*60)

# ============================================================
# COOKIE INJECTOR - Use saved cookies
# ============================================================

class QuotexCookieInjector:
    """Inject saved cookies to get session"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://market-qx.trade"
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'
        })
    
    def inject_cookies(self, filename="quotex_cookies.json"):
        """Load and inject cookies"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                cookies = data.get('cookies', {})
            
            if not cookies:
                print("❌ No cookies found in file")
                return False
            
            # Add cookies to session
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            print(f"✅ Injected {len(cookies)} cookies")
            
            # Test the session
            test_url = f"{self.base_url}/en/trade"
            response = self.session.get(test_url)
            
            if response.status_code == 200:
                if 'balance' in response.text.lower() or 'trade' in response.url:
                    print("✅ Session is valid!")
                    return True
                else:
                    print("⚠️ Session may have expired. Try logging in again.")
                    return False
            else:
                print(f"⚠️ Session test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Injection error: {e}")
            return False
    
    def get(self, url):
        """Make request with injected cookies"""
        return self.session.get(url)

# ============================================================
# MAIN MENU - Full Working Version
# ============================================================

def clear_screen():
    """Clear terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    """Print banner"""
    print("="*60)
    print("🍪 QUOTEX COOKIE EXTRACTOR")
    print("📍 market-qx.trade Edition")
    print("📱 Fully Working on Termux")
    print("="*60)
    print()

def check_login_page():
    """Check if login page is accessible"""
    try:
        response = requests.get("https://market-qx.trade/en/sign-in", timeout=10)
        print(f"✅ Login page accessible (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Cannot access login page: {e}")
        return False

def main():
    """Main function"""
    clear_screen()
    print_banner()
    
    # Check connectivity
    print("🔍 Checking connection...")
    check_login_page()
    
    while True:
        print("\n📋 OPTIONS:")
        print("  1. Extract Cookies (Login with Email/Password)")
        print("  2. Inject Saved Cookies")
        print("  3. View Saved Cookies")
        print("  4. Decode JWT Token")
        print("  5. Clear Saved Cookies")
        print("  6. Test Cookie Session")
        print("  7. Exit")
        print("-"*60)
        
        choice = input("👉 Enter choice (1-7): ").strip()
        
        if choice == "1":
            # Extract cookies
            print("\n" + "="*60)
            print("📝 LOGIN TO QUOTEX")
            print(f"📍 {QuotexCookieExtractor().login_url}")
            print("="*60)
            
            email = input("📧 Email: ").strip()
            password = input("🔑 Password: ").strip()
            
            if not email or not password:
                print("❌ Email and password required!")
                input("\nPress Enter to continue...")
                continue
            
            print("\n⏳ Connecting and logging in...")
            
            extractor = QuotexCookieExtractor()
            if extractor.login(email, password):
                extractor.display_cookies()
                extractor.save_cookies()
                
                # Try to get balance
                print("\n💰 Fetching balance...")
                balance = extractor.get_balance()
                if balance:
                    print(f"💰 Balance: {balance}")
                else:
                    print("⚠️ Could not retrieve balance")
            else:
                print("\n❌ Login failed. Please check:")
                print("  • Your email and password are correct")
                print("  • Your internet connection is working")
                print("  • The website is accessible")
            
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            # Inject cookies
            print("\n" + "="*60)
            print("💉 INJECTING SAVED COOKIES")
            print("="*60)
            
            injector = QuotexCookieInjector()
            if injector.inject_cookies():
                print("✅ Cookies injected successfully!")
                
                # Try to access trade page
                response = injector.get(f"{injector.base_url}/en/trade")
                if response.status_code == 200:
                    print("✅ Successfully accessed Quotex!")
                    
                    # Try to get balance
                    soup = BeautifulSoup(response.text, 'html.parser')
                    balance_elem = soup.select_one('.usermenu__info-balance')
                    if balance_elem:
                        print(f"💰 Balance: {balance_elem.text.strip()}")
                else:
                    print(f"⚠️ Access failed. Status: {response.status_code}")
            else:
                print("❌ Injection failed")
            
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            # View saved cookies
            print("\n" + "="*60)
            print("📋 SAVED COOKIES")
            print("="*60)
            
            try:
                with open("quotex_cookies.json", 'r') as f:
                    data = json.load(f)
                
                print(f"📅 Extracted: {data.get('timestamp', 'Unknown')}")
                print(f"📍 URL: {data.get('url', 'Unknown')}")
                print(f"📊 Count: {data.get('count', 0)}")
                print("-"*60)
                
                cookies = data.get('cookies', {})
                for name, value in cookies.items():
                    display = value[:50] + "..." if len(value) > 50 else value
                    print(f"  {name}: {display}")
                
            except FileNotFoundError:
                print("❌ No saved cookies found. Run extraction first.")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            # Decode JWT
            print("\n" + "="*60)
            print("🔐 DECODE JWT TOKEN")
            print("="*60)
            
            token = input("📝 Enter JWT token (or press Enter to use saved): ").strip()
            
            if not token:
                try:
                    with open("quotex_cookies.json", 'r') as f:
                        data = json.load(f)
                    cookies = data.get('cookies', {})
                    
                    # Find JWT tokens
                    jwt_tokens = {k: v for k, v in cookies.items() if v.count('.') == 2 and len(v) > 50}
                    
                    if jwt_tokens:
                        print("\n🔑 Found JWT tokens:")
                        token_names = list(jwt_tokens.keys())
                        for idx, name in enumerate(token_names, 1):
                            print(f"  {idx}. {name}")
                        
                        choice2 = input(f"\nSelect token (1-{len(token_names)}): ").strip()
                        try:
                            idx = int(choice2) - 1
                            token = list(jwt_tokens.values())[idx]
                        except:
                            print("❌ Invalid selection")
                            input("\nPress Enter to continue...")
                            continue
                    else:
                        print("❌ No JWT tokens found in saved cookies")
                        input("\nPress Enter to continue...")
                        continue
                except:
                    print("❌ No saved cookies found")
                    input("\nPress Enter to continue...")
                    continue
            
            # Decode
            extractor = QuotexCookieExtractor()
            decoded = extractor.decode_jwt(token)
            
            if decoded and isinstance(decoded, dict):
                print("\n" + "="*60)
                print("📋 DECODED JWT")
                print("="*60)
                print(json.dumps(decoded, indent=2))
                print("="*60)
            else:
                print(f"\n❌ Could not decode: {decoded}")
            
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # Clear cookies
            confirm = input("⚠️ Delete all saved cookies? (y/n): ").strip().lower()
            if confirm == 'y':
                try:
                    os.remove("quotex_cookies.json")
                    print("✅ Cookies cleared")
                except FileNotFoundError:
                    print("❌ No cookies file found")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("Cancelled")
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            # Test cookie session
            print("\n" + "="*60)
            print("🔍 TESTING COOKIE SESSION")
            print("="*60)
            
            try:
                with open("quotex_cookies.json", 'r') as f:
                    data = json.load(f)
                    cookies = data.get('cookies', {})
                
                if not cookies:
                    print("❌ No cookies found")
                    input("\nPress Enter to continue...")
                    continue
                
                session = requests.Session()
                for name, value in cookies.items():
                    session.cookies.set(name, value)
                
                response = session.get("https://market-qx.trade/en/trade")
                print(f"📡 Response: {response.status_code}")
                
                if 'balance' in response.text.lower() or 'trade' in response.url:
                    print("✅ Session is valid!")
                else:
                    print("❌ Session is invalid or expired")
                    
            except FileNotFoundError:
                print("❌ No saved cookies found")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == "7":
            print("\n👋 Goodbye!")
            sys.exit(0)
            
        else:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")

# ============================================================
# RUN THE APPLICATION
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please report this issue.")
        input("\nPress Enter to exit...")
