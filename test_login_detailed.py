#!/usr/bin/env python3
"""
Detailed login test to debug form submission issues
"""

import requests
import sys
import os
from urllib.parse import urljoin
import re

def test_login_detailed():
    base_url = "http://localhost:9001"
    session = requests.Session()
    
    print("🔍 DETAILED LOGIN TEST")
    print("=" * 50)
    
    # Step 1: Get login page and extract form data
    print("\n1. Getting login page...")
    response = session.get(f"{base_url}/login")
    print(f"   Status: {response.status_code}")
    
    # Extract CSRF token
    csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', response.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"   ✅ CSRF token: {csrf_token[:20]}...")
    else:
        print("   ❌ No CSRF token found")
        return
    
    # Extract form fields
    print("\n2. Analyzing form fields...")
    form_fields = re.findall(r'name="([^"]*)"', response.text)
    print(f"   Form fields found: {form_fields}")
    
    # Check for any error messages
    if 'error' in response.text.lower() or 'invalid' in response.text.lower():
        print("   ⚠️  Potential error messages in form")
    
    # Step 3: Test login with correct form data
    print("\n3. Testing login submission...")
    login_data = {
        'email': 'admin@mysticecho.com',
        'password': 'admin123',
        'remember': 'y',
        'csrf_token': csrf_token
    }
    
    print(f"   Sending data: {login_data}")
    
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print("   ✅ Login successful - redirecting")
        redirect_location = response.headers.get('Location', '')
        print(f"   Redirect to: {redirect_location}")
    elif response.status_code == 200:
        print("   ❌ Login failed - staying on login page")
        # Check for error messages
        if 'error' in response.text.lower():
            print("   Error messages found in response")
        if 'invalid' in response.text.lower():
            print("   Invalid credentials message found")
        if 'csrf' in response.text.lower():
            print("   CSRF error found")
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
    
    # Step 4: Check authentication state
    print("\n4. Checking authentication state...")
    debug_response = session.get(f"{base_url}/debug-auth")
    if 'User authenticated: True' in debug_response.text:
        print("   ✅ User is now authenticated")
    else:
        print("   ❌ User is still not authenticated")
    
    # Step 5: Test dashboard access
    print("\n5. Testing dashboard access...")
    dashboard_response = session.get(f"{base_url}/dashboard")
    print(f"   Dashboard status: {dashboard_response.status_code}")
    if dashboard_response.status_code == 200:
        print("   ✅ Dashboard accessible")
    elif dashboard_response.status_code == 302:
        print("   ❌ Dashboard redirecting (not authenticated)")
        print(f"   Redirect to: {dashboard_response.headers.get('Location', '')}")

if __name__ == "__main__":
    test_login_detailed()
