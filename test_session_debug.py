#!/usr/bin/env python3
"""
Test session and authentication debugging
"""

import requests
import sys
import os
from urllib.parse import urljoin
import re

def test_session_debug():
    base_url = "http://localhost:9001"
    session = requests.Session()
    
    print("🔍 SESSION DEBUG TEST")
    print("=" * 50)
    
    # Step 1: Get login page
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
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {
        'email': 'admin@mysticecho.com',
        'password': 'admin123',
        'remember': 'y',
        'csrf_token': csrf_token
    }
    
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location', 'N/A')}")
    
    # Check cookies
    print(f"   Cookies: {dict(session.cookies)}")
    
    # Step 3: Follow redirect
    if response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        if redirect_url.startswith('/'):
            redirect_url = urljoin(base_url, redirect_url)
        
        print(f"\n3. Following redirect to: {redirect_url}")
        redirect_response = session.get(redirect_url, allow_redirects=False)
        print(f"   Status: {redirect_response.status_code}")
        print(f"   Location: {redirect_response.headers.get('Location', 'N/A')}")
        
        # Check if we get redirected to login again
        if redirect_response.status_code == 302 and 'login' in redirect_response.headers.get('Location', ''):
            print("   ❌ REDIRECT LOOP: Being redirected back to login")
            print(f"   Redirect to: {redirect_response.headers.get('Location', '')}")
        elif redirect_response.status_code == 200:
            print("   ✅ Successfully reached destination")
        else:
            print(f"   ❓ Unexpected status: {redirect_response.status_code}")
    
    # Step 4: Test debug route with session
    print("\n4. Testing debug route with session...")
    debug_response = session.get(f"{base_url}/debug-auth")
    print(f"   Status: {debug_response.status_code}")
    
    if 'User authenticated: True' in debug_response.text:
        print("   ✅ User is authenticated in session")
    else:
        print("   ❌ User is NOT authenticated in session")
        # Check if there are any error messages
        if 'error' in debug_response.text.lower():
            print("   Error messages found in debug response")
    
    # Step 5: Test dashboard with session
    print("\n5. Testing dashboard with session...")
    dashboard_response = session.get(f"{base_url}/dashboard/")
    print(f"   Status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("   ✅ Dashboard accessible with session")
    elif dashboard_response.status_code == 302:
        print("   ❌ Dashboard redirecting (not authenticated)")
        print(f"   Redirect to: {dashboard_response.headers.get('Location', '')}")
    else:
        print(f"   ❓ Unexpected dashboard status: {dashboard_response.status_code}")

if __name__ == "__main__":
    test_session_debug()
