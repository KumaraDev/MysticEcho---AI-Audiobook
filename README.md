# 🎧 MysticEcho - AI Audiobook Creation Platform

Transform your manuscripts into professional audiobooks with AI-powered assistance.

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Clone the repository
git clone https://github.com/KumaraDev/MysticEcho---AI-Audiobook.git
cd MysticEcho---AI-Audiobook

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure API Keys**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

### 3. **Required API Keys**

#### **🔑 Essential (Required)**
- **`SESSION_SECRET`**: Any random string for Flask sessions
- **`REPL_ID`**: Your Replit ID for authentication
- **`OPENAI_API_KEY`**: OpenAI API key for AI features and TTS

#### **🔑 Optional (Recommended)**
- **`WASABI_*`**: Cloud storage for project backups
- **`SENDGRID_*`**: Email notifications

### 4. **Run the Application**
```bash
# Method 1: Using the startup script
python run.py

# Method 2: Direct Flask command
python main.py

# Method 3: Using gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 5. **Access the Application**
Open your browser and go to: **http://localhost:5000**

## 🔧 API Key Setup Guide

### **OpenAI API Key** (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up/Login to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

### **Replit ID** (Required)
1. Go to [Replit](https://replit.com/)
2. Create a new Repl or use existing one
3. Copy your Repl ID from the URL or settings
4. Add to `.env`:
   ```
   REPL_ID=your-repl-id-here
   ```

### **Wasabi Storage** (Optional)
1. Sign up at [Wasabi](https://wasabi.com/)
2. Create a bucket
3. Generate access keys
4. Add to `.env`:
   ```
   WASABI_ACCESS_KEY=your-access-key
   WASABI_SECRET_KEY=your-secret-key
   WASABI_BUCKET=your-bucket-name
   ```

### **SendGrid Email** (Optional)
1. Sign up at [SendGrid](https://sendgrid.com/)
2. Create an API key
3. Verify sender email
4. Add to `.env`:
   ```
   SENDGRID_API_KEY=your-sendgrid-key
   SENDGRID_SENDER_EMAIL=your-verified-email@domain.com
   ```

## 📁 Project Structure

```
MysticEcho/
├── app.py                 # Flask app configuration
├── main.py               # Application entry point
├── models.py             # Database models
├── replit_auth.py        # Authentication system
├── routes/               # Route blueprints
│   ├── dashboard.py      # Project management
│   ├── editor.py         # Rich text editor
│   └── audio.py          # TTS and audio generation
├── services/             # Business logic
│   ├── ai_service.py     # OpenAI integration
│   ├── tts_service.py    # Text-to-speech
│   ├── storage_service.py # Cloud storage
│   └── pdf_service.py    # PDF processing
├── templates/            # HTML templates
├── static/              # CSS/JS assets
├── venv/                # Virtual environment
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── run.py              # Startup script
```

## 🎯 Features

### **📝 Rich Text Editing**
- TinyMCE integration
- Auto-save functionality
- Chapter management
- Version control

### **🤖 AI-Powered Assistance**
- Content improvement suggestions
- Text expansion and summarization
- Audiobook readiness analysis

### **🎙️ Text-to-Speech**
- OpenAI TTS integration
- 6 voice options (Alloy, Echo, Fable, Onyx, Nova, Shimmer)
- Audio preview and download

### **📊 Project Management**
- Dashboard overview
- Project status tracking
- Cloud backup integration

### **📄 PDF Import**
- Upload and extract text from PDFs
- Automatic content integration

## 🛠️ Development

### **Running in Development Mode**
```bash
source venv/bin/activate
python run.py
```

### **Running in Production**
```bash
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### **Database Management**
The application uses SQLite by default. For production, configure PostgreSQL:
```bash
DATABASE_URL=postgresql://user:password@localhost/mystic_echo
```

## 🐛 Troubleshooting

### **Common Issues**

1. **"No module named 'flask'"**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **"REPL_ID environment variable must be set"**
   - Add `REPL_ID=your-repl-id` to `.env` file

3. **"OPENAI_API_KEY not found"**
   - Add your OpenAI API key to `.env` file

4. **Database errors**
   - Check `DATABASE_URL` in `.env` file
   - Ensure database file permissions

### **Logs and Debugging**
- Check console output for error messages
- Enable debug mode in `run.py` (already enabled)
- Check Flask logs for detailed error information

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review the error messages in the console
- Ensure all required API keys are configured

## 🎉 Ready to Create Audiobooks!

Once you've configured your API keys and started the application, you can:
1. Create new audiobook projects
2. Write and edit your manuscripts
3. Use AI to improve your content
4. Generate professional audio with TTS
5. Export your finished audiobooks

Happy creating! 🎧✨
