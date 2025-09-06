#!/usr/bin/env python3
"""
MysticEcho Application Startup Script
Run this script to start the MysticEcho audiobook creation platform.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check required environment variables
required_vars = ['SESSION_SECRET', 'REPL_ID']
missing_vars = []

for var in required_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    print("❌ Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n📝 Please create a .env file with the required variables.")
    print("   Copy .env.example to .env and fill in your values.")
    sys.exit(1)

# Check optional but recommended variables
optional_vars = ['OPENAI_API_KEY']
missing_optional = []

for var in optional_vars:
    if not os.environ.get(var):
        missing_optional.append(var)

if missing_optional:
    print("⚠️  Missing optional environment variables:")
    for var in missing_optional:
        print(f"   - {var}")
    print("\n📝 These are recommended for full functionality:")
    print("   - OPENAI_API_KEY: Required for AI features and text-to-speech")
    print("   - WASABI_*: Optional for cloud storage backups")
    print("   - SENDGRID_*: Optional for email notifications")
    print("\n🚀 Starting application anyway...")

# Import and run the application
try:
    from main import app
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))  # Use port 5001 by default
    
    print("🎧 Starting MysticEcho - AI Audiobook Creation Platform")
    print(f"🌐 Application will be available at: http://localhost:{port}")
    print("📚 Features: Rich text editing, AI assistance, TTS generation")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Run the application
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
    
except Exception as e:
    print(f"❌ Error starting application: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure you're in the project directory")
    print("2. Activate the virtual environment: source venv/bin/activate")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Check your .env file configuration")
    sys.exit(1)
