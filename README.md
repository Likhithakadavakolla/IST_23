# EduReach - Education for Rural People

EduReach is a comprehensive educational platform designed to provide quality education access to rural communities through innovative technology and comprehensive learning resources. The platform offers courses in Physics, Chemistry, and Mathematics for 9th and 10th grade students with multilingual support in English, Telugu, and Kannada.

## Features

### Core Features
- **User Authentication**: Secure login and registration system
- **Course Management**: Physics, Chemistry, and Mathematics courses with video content
- **Video Learning**: 10 educational videos per course embedded from YouTube
- **Assignment System**: Interactive assignments unlocked after course completion
- **Progress Tracking**: Detailed progress analytics with charts and graphs
- **Multilingual Support**: Content available in English, Telugu, and Kannada
- **Contact System**: Contact form with logging functionality
- **Responsive Design**: Mobile-friendly interface

### Technical Features
- **Backend**: Flask-based REST API
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Responsive HTML/CSS/JavaScript
- **Authentication**: Flask-Login with password hashing
- **Charts**: Chart.js for progress visualization
- **Animations**: Smooth CSS animations and transitions

## Project Structure

```
edureach-project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── README.md             # Project documentation
├── backend/              # Backend modules
│   ├── __init__.py
│   └── models.py        # Database models (unused - models in app.py)
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── dashboard.html   # User dashboard
│   ├── courses.html     # Courses page
│   ├── assignments.html # Assignments page
│   ├── progress.html    # Progress tracking page
│   ├── contact.html     # Contact page
│   └── auth/
│       ├── login.html   # Login page
│       └── register.html # Registration page
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   ├── js/
│   │   └── main.js      # Main JavaScript
│   └── images/          # Image assets
└── logs/                # Application logs
    └── contacts.log     # Contact form submissions
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd edureach-project
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the root directory (already exists):
```
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///edureach.db
FLASK_ENV=development
FLASK_DEBUG=True
```

### Step 5: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### For Students

1. **Registration**: Create a new account with name, email, class, and password
2. **Login**: Access your dashboard with email and password
3. **Browse Courses**: Explore Physics, Chemistry, and Mathematics courses
4. **Watch Videos**: View educational content for each subject
5. **Complete Assignments**: Take assessments after finishing courses
6. **Track Progress**: Monitor learning journey with detailed analytics
7. **Contact Support**: Reach out for help via contact form

### For Developers

#### Database Models
- **Student**: User accounts with authentication
- **Course**: Subject information and video URLs
- **Assignment**: Questions and assessment data
- **Progress**: Student learning progress tracking
- **ContactLog**: Contact form submissions

#### API Endpoints
- `GET /api/courses` - Get all courses
- `POST /api/submit_assignment` - Submit assignment answers
- `GET /api/progress` - Get student progress data
- `GET /api/translations/<language>` - Get UI translations

#### Multilingual Support
The application supports three languages:
- English (en)
- Telugu (te)
- Kannada (kn)

Language preference is saved in localStorage and persists across sessions.

## Technology Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Werkzeug**: Password hashing
- **Python-dotenv**: Environment variable management

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Responsive design with animations
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Progress visualization
- **Font Awesome**: Icon library

### Database
- **SQLite**: Lightweight database for development
- **MySQL**: Production database option

## Features in Detail

### Authentication System
- Secure password hashing with Werkzeug
- Session management with Flask-Login
- Registration validation and error handling

### Video Learning
- YouTube video integration
- Modal-based video player
- Progress tracking per video

### Assessment System
- Text-based questions and answers
- Automatic scoring system
- Results storage and retrieval

### Progress Analytics
- Course completion tracking
- Assignment score visualization
- Interactive charts and graphs
- Detailed progress history

### Multilingual Interface
- Dynamic language switching
- Persistent language preferences
- Support for right-to-left scripts

## Development

### Adding New Courses
1. Create course entry in database initialization
2. Add video URLs (comma-separated)
3. Update course icons in templates

### Adding New Languages
1. Add translations to `/api/translations/<language>` endpoint
2. Update language selector in base template
3. Test UI elements for proper translation

### Customizing Themes
- Modify `static/css/style.css`
- Update CSS custom properties for colors
- Adjust responsive breakpoints as needed

## Deployment

### Production Setup
1. Change `FLASK_ENV=production` in `.env`
2. Set strong `SECRET_KEY`
3. Configure production database
4. Set up reverse proxy (nginx)
5. Use WSGI server (gunicorn)

### Database Migration
For production, consider using MySQL:
```
DATABASE_URL=mysql://username:password@host:port/database
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support and inquiries:
- Email: contact@edureach.com
- GitHub: [Project Repository]
- LinkedIn: [Project Team]

## Acknowledgments

- Educational video content providers
- Open source community
- Rural education advocates
- Beta testers and feedback providers