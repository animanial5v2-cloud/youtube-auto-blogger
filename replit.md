# AI Blogging Studio

## Overview

AI Blogging Studio is a comprehensive web application that automates blog content creation and publishing. The system leverages Google's Gemini AI models to generate blog posts from various sources including YouTube videos, uploaded files, or user-provided topics. It integrates with Google Blogger for automated publishing and supports multiple content generation workflows with customizable settings for tone, audience, and visual content.

## User Preferences

Preferred communication style: Simple, everyday language.

## Commercial Goals

The user plans to sell this AI Auto-Blogging Studio on Kmong (Korean freelance platform). Key requirements:
- Deployment-ready Flask application with PostgreSQL database
- Multi-platform publishing support (Blogger, WordPress, Tistory manual, Naver Blog)
- Professional presentation for potential buyers
- Clear documentation for setup and usage
- Scalable architecture for multiple users
- Transparent handling of API limitations (e.g., Tistory API discontinuation)

### Desktop Version Completed (August 2025)
- Successfully created standalone Windows EXE application (AI_Blogging_Studio_DEPLOY.exe)
- Professional Korean interface with dark theme optimized for Kmong marketplace
- Offline-capable launcher that connects to permanent deployment URL
- 8-10MB single file with no installation required
- Immediate execution (3-5 seconds startup)
- Built-in usage guide and customer support information
- Ready for commercial distribution on Kmong platform
- Final dark theme version completed and tested
- Updated with permanent Replit Deploy URL (https://share-site-forge-animanial5v2.replit.app)
- Full source code backup and platform migration capabilities documented

## System Architecture

### Backend Architecture
The application uses a Flask-based backend with SQLAlchemy for database operations. The architecture follows a service-oriented pattern with dedicated service classes for different integrations:

- **Flask Web Framework**: Serves as the main application server with RESTful API endpoints
- **SQLAlchemy ORM**: Provides database abstraction with declarative models
- **Service Layer Pattern**: Separate service classes handle external API integrations (YouTube, Gemini, Blogger)
- **Session-based User Management**: Uses Flask sessions with UUID-based user identification

### Database Design
The system uses PostgreSQL with three main entities:

- **User Model**: Stores user information, Google authentication data, and JSON-based settings
- **BlogPost Model**: Contains comprehensive post metadata including source information, AI model settings, and publishing status
- **PostQueue Model**: Manages automated posting workflows and scheduling

Key design decisions include using UUID primary keys for distributed scalability and JSON columns for flexible user settings storage.

### Frontend Architecture
The frontend is a single-page application built with vanilla JavaScript:

- **Component-based UI**: Modular sidebar sections with collapsible panels
- **State Management**: Global JavaScript object manages application state including authentication, content generation, and posting history
- **Event-driven Architecture**: DOM event handlers coordinate user interactions with backend services
- **Responsive Design**: CSS Grid and Flexbox layout with dark/light theme support

### AI Content Generation Pipeline
The content generation workflow supports multiple input sources:

- **YouTube Integration**: Extracts transcripts and generates blog content from video URLs
- **File Upload Processing**: Handles various file formats for content extraction
- **Topic-based Generation**: Creates content from user-provided text topics
- **Multi-modal AI**: Leverages Gemini's capabilities for text and image understanding

### Authentication & Authorization
The system implements Google OAuth 2.0 integration:

- **Google Identity Services**: Uses the newer GIS library for token-based authentication
- **Blogger API Access**: Manages OAuth scopes for blog publishing permissions
- **Session Management**: Maintains user state across requests with secure session handling

## External Dependencies

### AI Services
- **Google Gemini API**: Primary content generation service supporting multiple model versions (1.5 Pro, 2.0 Flash, 2.5 Pro series)
- **YouTube Data API**: Video metadata and transcript extraction
- **Google Cloud Platform**: Image generation capabilities for AI-powered visuals

### Publishing Platform
- **Google Blogger API**: Automated blog post publishing with draft/live status management
- **WordPress.com API**: REST API integration for WordPress.com sites
- **Tistory**: Manual publishing workflow (API discontinued since 2021)
- **Naver Blog API**: Integration with Naver's blog publishing system
- **OAuth 2.0 Authentication**: Google Identity Services for secure API access

### Media & Content Services
- **Pexels API**: Stock image sourcing with keyword-based search
- **YouTube Transcript API**: Multi-language transcript extraction from videos
- **Play-dl Library**: Alternative YouTube content processing

### Infrastructure
- **PostgreSQL Database**: Primary data storage with connection pooling
- **Express.js Backend**: Alternative Node.js server implementation for specific endpoints
- **Multer**: File upload handling with temporary storage management
- **ProxyFix Middleware**: Production deployment support for reverse proxy configurations

### Development Tools
- **Flask-SQLAlchemy**: Database ORM with declarative base models
- **Werkzeug**: WSGI utilities and development server capabilities
- **CORS Support**: Cross-origin request handling for API endpoints