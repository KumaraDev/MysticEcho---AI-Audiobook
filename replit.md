# Mystic Echo - Audiobook Creation Platform

## Overview

Mystic Echo is an AI-powered audiobook creation platform built with Flask that allows users to transform manuscripts into professional audiobooks. The application provides rich text editing capabilities, AI-powered content enhancement, PDF import functionality, and cloud storage integration for managing audiobook projects.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular Flask architecture with clear separation of concerns:

- **Backend Framework**: Flask with SQLAlchemy ORM for database operations
- **Database**: SQLite with fallback to PostgreSQL via DATABASE_URL environment variable
- **Frontend**: Server-side rendered templates using Jinja2 with Bootstrap dark theme
- **Rich Text Editing**: TinyMCE integration for manuscript editing
- **AI Integration**: OpenAI API for content enhancement and suggestions
- **Cloud Storage**: Wasabi/S3 compatible storage for project backups
- **File Processing**: PyPDF2 for PDF text extraction

## Key Components

### Authentication System
- User registration and login with password hashing
- Session-based authentication with user context
- Login required decorators for protected routes

### Database Models
- **User**: Core user accounts with relationships to projects
- **Project**: Main entity storing audiobook manuscripts with metadata
- **ProjectVersion**: Version control for tracking content changes
- Uses SQLAlchemy with declarative base for ORM operations

### Route Blueprints
- **auth_bp**: Handles user authentication (login/register)
- **dashboard_bp**: Project management and overview dashboard
- **editor_bp**: Rich text editing interface for manuscripts
- **audio_bp**: Audio generation and audiobook creation workflow

### Service Layer
- **AI Service**: OpenAI integration for content improvement, expansion, and summarization
- **PDF Service**: Text extraction from uploaded PDF files with error handling
- **Storage Service**: Wasabi cloud storage for project backups and file management

### Frontend Architecture
- Dark theme Bootstrap UI with custom CSS enhancements
- Responsive design with mobile-friendly interface
- TinyMCE rich text editor with auto-save functionality
- Real-time word counting and project status updates

## Data Flow

1. **User Authentication**: Users register/login to access the platform
2. **Project Creation**: Users create new audiobook projects from dashboard
3. **Content Input**: Text can be entered manually or imported from PDF files
4. **AI Enhancement**: Content can be processed through OpenAI for improvements
5. **Auto-save**: Editor automatically saves content to prevent data loss
6. **Version Control**: Significant changes create new project versions
7. **Audio Generation**: Text-to-speech conversion using OpenAI API (ready for implementation)
8. **Chapter Management**: Automatic chapter detection and organization
9. **Audio Preview**: Listen to generated audiobook content
10. **Export & Download**: Package audiobook in various formats
11. **Cloud Backup**: Projects are backed up to Wasabi cloud storage
12. **Project Management**: Dashboard provides overview and project status tracking

## Audiobook Creation Workflow

The platform now includes a complete audiobook creation workflow that guides users through:

1. **✓ Write & Edit**: Complete manuscript with AI assistance and auto-save
2. **Generate Audio**: Convert text to professional speech using OpenAI TTS
3. **Organize Chapters**: Automatic chapter detection and management
4. **Preview & Review**: Listen to generated audio content
5. **Export & Download**: Get final audiobook in MP3 and other formats

Each step is accessible from the editor's "Next Steps" sidebar, providing a clear path from manuscript to finished audiobook.

## External Dependencies

### Required Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `OPENAI_API_KEY`: OpenAI API access for AI features
- `WASABI_ACCESS_KEY`: Cloud storage access credentials
- `WASABI_SECRET_KEY`: Cloud storage secret key
- `WASABI_BUCKET`: Storage bucket name
- `WASABI_REGION`: Storage region
- `WASABI_ENDPOINT`: Storage service endpoint

### Python Dependencies
- Flask and Flask-SQLAlchemy for web framework
- PyPDF2 for PDF text extraction
- OpenAI for AI content enhancement
- Boto3 for cloud storage integration
- Werkzeug for security utilities

### Frontend Dependencies
- Bootstrap (via CDN) for responsive UI components
- TinyMCE (via CDN) for rich text editing
- Feather Icons for consistent iconography

## Deployment Strategy

The application is designed for containerized deployment with:

- Environment-based configuration for different deployment stages
- SQLite for development, PostgreSQL for production
- Cloud storage integration for scalable file management
- Session-based authentication suitable for single-instance deployment
- Static file serving through Flask for simplicity
- Debug mode configurable via environment

### Key Architectural Decisions

1. **Flask over Django**: Chosen for simplicity and flexibility in a focused application
2. **SQLAlchemy ORM**: Provides database abstraction with migration capabilities
3. **Blueprint Architecture**: Modular route organization for maintainability
4. **Service Layer Pattern**: Separates business logic from route handlers
5. **Session-based Auth**: Simple authentication suitable for the application scale
6. **TinyMCE Integration**: Professional rich text editing without complex frontend framework
7. **Wasabi Storage**: Cost-effective S3-compatible cloud storage solution
8. **Template-based Frontend**: Server-side rendering for faster initial loads

The architecture prioritizes simplicity, maintainability, and clear separation of concerns while providing enterprise-grade features for audiobook manuscript management.