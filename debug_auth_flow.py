#!/usr/bin/env python3
"""
Deep authentication flow debug script
This will test the entire authentication process step by step
"""

import requests
import sys
import os
from urllib.parse import urljoin

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_flow():
    base_url = "http://localhost:9001"
    session = requests.Session()
    
    print("🔍 DEEP AUTHENTICATION FLOW DEBUG")
    print("=" * 50)
    
    # Step 1: Test home page
    print("\n1. Testing home page...")
    try:
        response = session.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print("   ✅ Home page loads successfully")
        else:
            print("   ❌ Home page failed")
            return
    except Exception as e:
        print(f"   ❌ Error accessing home page: {e}")
        return
    
    # Step 2: Test login page
    print("\n2. Testing login page...")
    try:
        response = session.get(f"{base_url}/login")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print("   ✅ Login page loads successfully")
            # Check for CSRF token
            if 'csrf_token' in response.text:
                print("   ✅ CSRF token found in response")
            else:
                print("   ❌ No CSRF token found")
        else:
            print("   ❌ Login page failed")
            return
    except Exception as e:
        print(f"   ❌ Error accessing login page: {e}")
        return
    
    # Step 3: Extract CSRF token
    print("\n3. Extracting CSRF token...")
    try:
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrf_token' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        if csrf_token:
            print(f"   ✅ CSRF token extracted: {csrf_token[:20]}...")
        else:
            print("   ❌ Could not extract CSRF token")
            return
    except Exception as e:
        print(f"   ❌ Error extracting CSRF token: {e}")
        return
    
    # Step 4: Test login with admin credentials
    print("\n4. Testing login with admin credentials...")
    try:
        login_data = {
            'email': 'admin@mysticecho.com',
            'password': 'admin123',
            'remember': 'y',
            'csrf_token': csrf_token
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"   ✅ Login successful - redirecting to: {redirect_location}")
            
            # Follow the redirect
            if redirect_location:
                if redirect_location.startswith('/'):
                    redirect_url = urljoin(base_url, redirect_location)
                else:
                    redirect_url = redirect_location
                
                print(f"\n5. Following redirect to: {redirect_url}")
                redirect_response = session.get(redirect_url, allow_redirects=False)
                print(f"   Status: {redirect_response.status_code}")
                print(f"   Headers: {dict(redirect_response.headers)}")
                
                if redirect_response.status_code == 302:
                    print("   ❌ REDIRECT LOOP DETECTED!")
                    print(f"   Redirecting to: {redirect_response.headers.get('Location', '')}")
                elif redirect_response.status_code == 200:
                    print("   ✅ Successfully reached dashboard")
                else:
                    print(f"   ❌ Unexpected status: {redirect_response.status_code}")
        else:
            print(f"   ❌ Login failed with status: {response.status_code}")
            print(f"   Response content: {response.text[:500]}")
    except Exception as e:
        print(f"   ❌ Error during login: {e}")
        return
    
    # Step 6: Test dashboard access directly
    print("\n6. Testing direct dashboard access...")
    try:
        response = session.get(f"{base_url}/dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Dashboard accessible")
        elif response.status_code == 302:
            print("   ❌ Dashboard redirecting (not authenticated)")
            print(f"   Redirecting to: {response.headers.get('Location', '')}")
        else:
            print(f"   ❌ Dashboard failed with status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error accessing dashboard: {e}")
    
    # Step 7: Check session data
    print("\n7. Checking session data...")
    try:
        # Try to access a protected endpoint to see what Flask-Security-Too thinks
        response = session.get(f"{base_url}/dashboard")
        if 'You must sign in to view this resource' in response.text:
            print("   ❌ Flask-Security-Too says user is not authenticated")
        elif 'dashboard' in response.text.lower():
            print("   ✅ Flask-Security-Too recognizes user as authenticated")
        else:
            print("   ❓ Unknown authentication state")
    except Exception as e:
        print(f"   ❌ Error checking session: {e}")

if __name__ == "__main__":
    test_auth_flow()
