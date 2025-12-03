# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## EduReach - Educational Platform for Rural Communities

EduReach is a Flask-based educational platform providing multilingual (English, Telugu, Kannada) courses in Physics, Chemistry, and Mathematics for 9th and 10th grade students. It features video learning, interactive assignments, progress tracking, and user authentication.

## Development Commands

### Environment Setup
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```powershell
# Run in development mode (default)
python app.py

# The application will start on http://localhost:5000
```

### Database Operations
```powershell
# Database is auto-created on first run
# SQLite database file: edureach.db (git-ignored)

# To reset database (delete edureach.db and restart)
rm edureach.db
python app.py
```

### Development Testing
```powershell
# Test API endpoints
curl http://localhost:5000/api/courses
curl http://localhost:5000/api/translations/en

# Check logs
type logs\contacts.log
```

## Architecture Overview

### Core Architecture Pattern
- **Monolithic Flask Application**: Single `app.py` file contains all routes, models, and business logic
- **Template-based Frontend**: Jinja2 templates with responsive HTML/CSS/JavaScript
- **SQLite Database**: Local database with SQLAlchemy ORM
- **Session-based Authentication**: Flask-Login for user management

### Key Components

#### Database Models (defined in app.py)
- **Student**: User accounts with authentication and class level
- **Course**: Subject courses with embedded YouTube video URLs
- **Assignment**: Text-based assessments with pipe-separated questions
- **Progress**: Student learning progress and assignment scores
- **ContactLog**: Contact form submissions with file and database logging

#### Route Structure
- **Authentication Routes**: `/login`, `/register`, `/logout`
- **Core Pages**: `/`, `/dashboard`, `/courses`, `/assignments`, `/progress`, `/contact`
- **API Endpoints**: `/api/courses`, `/api/submit_assignment`, `/api/progress`, `/api/translations/<language>`

#### Frontend Architecture
- **Base Template System**: `templates/base.html` with language selector and navigation
- **Responsive Design**: Mobile-first CSS with smooth animations
- **Multilingual Support**: Dynamic language switching with localStorage persistence
- **Interactive Elements**: Modal video player, progress charts with Chart.js

### Data Flow Patterns

#### User Authentication Flow
1. Registration creates Student record with hashed password
2. Login validates credentials and creates Flask session
3. All protected routes require `@login_required` decorator
4. User context available via `current_user` (Flask-Login)

#### Course Progression System
1. Students access courses with embedded YouTube videos
2. Assignments unlock only after completing all courses
3. Progress tracking records course completion and assignment scores
4. Dashboard displays progress analytics with Chart.js visualizations

#### Multilingual Content Delivery
1. Language preference stored in browser localStorage
2. Translation API endpoint (`/api/translations/<language>`) provides UI text
3. JavaScript applies translations dynamically to elements with `data-translate` attributes
4. Supported languages: English (en), Telugu (te), Kannada (kn)

## File Structure

```
edureach-project/
├── app.py                 # Main Flask application (models, routes, config)
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (SECRET_KEY, DATABASE_URL)
├── backend/              # Unused module (models duplicated in app.py)
│   ├── models.py        # Database models (not imported)
│   └── __init__.py
├── templates/           # Jinja2 templates
│   ├── base.html       # Base template with navigation
│   ├── index.html      # Landing page
│   ├── dashboard.html  # User dashboard with progress
│   ├── courses.html    # Course listing with videos
│   ├── assignments.html # Assignment interface
│   ├── progress.html   # Progress analytics
│   ├── contact.html    # Contact form
│   └── auth/
│       ├── login.html  # Login form
│       └── register.html # Registration form
├── static/             # Static assets
│   ├── css/
│   │   └── style.css   # Main stylesheet with responsive design
│   ├── js/
│   │   └── main.js     # Frontend JavaScript (navigation, animations, i18n)
│   └── images/         # Image assets
└── logs/               # Application logs
    └── contacts.log    # Contact form submissions
```

## Development Guidelines

### Database Schema
- All models use auto-incrementing integer primary keys
- Foreign key relationships: Progress links to Student, Course, and Assignment
- String fields use appropriate lengths (email: 120, name: 100)
- DateTime fields use UTC timestamps with `datetime.utcnow`

### Video Content Management
- YouTube URLs stored as comma-separated strings in Course.video_urls
- Use `Course.get_video_list()` method to parse URLs into arrays
- Video URLs should be embed format: `https://www.youtube.com/embed/{video_id}`

### Assignment System
- Questions stored as pipe-separated strings in Assignment.questions
- Use `Assignment.get_questions_list()` method to parse questions
- Simple scoring: 10 points per answer (modify `submit_assignment` route for custom scoring)

### Frontend Development
- CSS uses custom properties for theming (see `:root` selectors in style.css)
- JavaScript uses modern ES6+ features (async/await, fetch API)
- Responsive breakpoints: mobile-first approach with media queries
- Animation classes: `.fade-in` with Intersection Observer for scroll animations

### Environment Configuration
- Development settings in `.env` file
- Production deployment requires changing FLASK_ENV=production
- Database configurable via DATABASE_URL environment variable
- Secret key should be changed for production deployment

### Logging and Contact Management
- Contact submissions logged to both file (`logs/contacts.log`) and database
- Log directory created automatically if missing
- UTF-8 encoding used for log files to support multilingual content

## Common Tasks

### Adding New Courses
1. Add course data to sample data initialization in `app.py` (around line 342)
2. Update course icons/images in templates if needed
3. Restart application to recreate database with new courses

### Adding New Languages
1. Add translation object to `/api/translations/<language>` route in `app.py`
2. Update language selector options in `templates/base.html`
3. Test all UI elements for proper translation coverage

### Customizing Scoring Logic
- Modify `submit_assignment` route in `app.py` (line 208)
- Update Progress model scoring calculations
- Adjust progress visualization in `templates/progress.html`

### Database Migration (Production)
- Current setup uses SQLite for development
- For production, update DATABASE_URL to MySQL/PostgreSQL
- Consider using Flask-Migrate for schema versioning

## API Reference

### Authentication Required Endpoints
- `GET /api/courses` - Returns course data with video URLs
- `POST /api/submit_assignment` - Submit assignment answers (JSON: {assignment_id, answers})
- `GET /api/progress` - Returns student progress data

### Public Endpoints
- `GET /api/translations/{language}` - Returns UI translations for specified language (en/te/kn)

## Known Architectural Considerations

### Code Organization
- Models are duplicated between `backend/models.py` and `app.py` - only `app.py` versions are used
- All business logic concentrated in single `app.py` file (consider modularization for larger teams)
- No test suite present - consider adding unit tests for models and routes

### Security
- Password hashing using Werkzeug (secure)
- CSRF protection not implemented (consider Flask-WTF forms)
- Input validation minimal (add validation for form submissions)

### Performance
- No caching implemented (consider Flask-Caching for course data)
- Database queries not optimized (consider eager loading for Progress relationships)
- Static assets served by Flask in development (use CDN/nginx for production)