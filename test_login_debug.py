#!/usr/bin/env python3
"""
Debug Login Test
Tests the login process step by step
"""

import requests
import re

def test_login_debug():
    base_url = "http://localhost:9001"
    session = requests.Session()
    
    print("🔍 Debug Login Test")
    print("=" * 40)
    
    # Step 1: Get login page
    print("1. Getting login page...")
    response = session.get(f"{base_url}/login")
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Cannot access login page")
        return False
    
    # Step 2: Extract CSRF token
    print("2. Extracting CSRF token...")
    csrf_token = None
    if 'csrf_token' in response.text:
        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   CSRF token found: {csrf_token[:20]}...")
        else:
            print("   ❌ CSRF token not found in form")
    else:
        print("   ❌ No CSRF token field found")
    
    # Step 3: Prepare login data
    print("3. Preparing login data...")
    login_data = {
        'email': 'admin@mysticecho.com',
        'password': 'admin123',
        'remember': 'y'
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
        print("   ✅ CSRF token included")
    else:
        print("   ⚠️  No CSRF token included")
    
    # Step 4: Submit login
    print("4. Submitting login...")
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 302:
        redirect_location = response.headers.get('Location', '')
        print(f"   Redirect to: {redirect_location}")
        
        if '/dashboard' in redirect_location:
            print("   ✅ Redirecting to dashboard")
        else:
            print(f"   ❌ Not redirecting to dashboard: {redirect_location}")
    else:
        print(f"   ❌ Expected 302 redirect, got {response.status_code}")
        print(f"   Response content: {response.text[:200]}...")
    
    # Step 5: Test dashboard access
    print("5. Testing dashboard access...")
    response = session.get(f"{base_url}/dashboard")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Dashboard accessible")
        return True
    elif response.status_code == 302:
        redirect_location = response.headers.get('Location', '')
        print(f"   ❌ Redirected to: {redirect_location}")
        return False
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_login_debug()
    if success:
        print("\n🎉 Login debug test PASSED!")
    else:
        print("\n❌ Login debug test FAILED!")
