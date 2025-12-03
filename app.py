from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import logging
import smtplib
import ssl
from email.message import EmailMessage
import secrets
from dotenv import load_dotenv
import pathlib

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
# Build an absolute path to instance/edureach.db so SQLite can always open it
db_path = pathlib.Path(__file__).parent / "instance" / "edureach.db"
default_db_uri = f"sqlite:///{db_path.as_posix()}"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Outgoing email (configure via environment variables)
app.config['MAIL_MODE'] = os.getenv('MAIL_MODE', '').lower()  # 'smtp' or 'file' (dev)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', '')             # e.g. smtp.gmail.com
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))         # 587 TLS, 465 SSL
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')         # your SMTP username
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')         # your SMTP password or app password
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ('1', 'true', 'yes')
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() in ('1', 'true', 'yes')
app.config['MAIL_FROM'] = os.getenv('MAIL_FROM', os.getenv('MAIL_USERNAME', 'no-reply@edureach.local'))
# Mirror emails to local outbox even when using SMTP (development convenience)
app.config['MAIL_MIRROR_FILE'] = os.getenv('MAIL_MIRROR_FILE', 'false').lower() in ('1', 'true', 'yes')
# Optional: base URL to use when building absolute links in emails (for LAN/mobile testing)
# Example: http://192.168.1.50:5000
app.config['EXTERNAL_BASE_URL'] = os.getenv('EXTERNAL_BASE_URL', '').strip()

# Uploads configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join('instance', 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_MB', '50')) * 1024 * 1024  # MB -> bytes
_DEFAULT_ALLOWED = 'pdf,doc,docx,png,jpg,jpeg,gif,mp4,avi,txt,csv'
app.config['ALLOWED_EXTENSIONS'] = {e.strip().lower() for e in os.getenv('ALLOWED_EXTENSIONS', _DEFAULT_ALLOWED).split(',') if e.strip()}

# Initialize extensions
# Ensure upload directory exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception:
    pass

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define models inline to avoid import issues
from flask_login import UserMixin
from datetime import datetime

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_level = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    progress = db.relationship('Progress', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.email}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Course title (e.g., topic name)
    class_level = db.Column(db.String(20), nullable=False)  # 9th or 10th
    subject = db.Column(db.String(50), nullable=False, default='')  # Physics, Chemistry, Mathematics
    description = db.Column(db.Text)
    video_data = db.Column(db.Text)  # JSON string containing video info with titles and descriptions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    progress = db.relationship('Progress', backref='course', lazy=True)
    assignments = db.relationship('Assignment', backref='course', lazy=True)
    
    def __repr__(self):
        return f'<Course {self.name} - {self.class_level} - {self.subject}>'
    
    def get_videos(self):
        import json
        if self.video_data:
            try:
                return json.loads(self.video_data)
            except:
                return []
        return []

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    questions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    progress = db.relationship('Progress', backref='assignment', lazy=True)
    
    def __repr__(self):
        return f'<Assignment {self.title} (Course {self.course_id})>'
    
    def get_questions_list(self):
        if self.questions:
            return self.questions.split('|')
        return []

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=True)
    video_progress = db.Column(db.Text)  # JSON string tracking which videos are completed
    score = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Progress {self.student_id} - Course {self.course_id}>'

class ContactLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactLog {self.name} - {self.email}>'

class PendingOTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    otp_hash = db.Column(db.String(200), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('Student', backref='pending_otps')

    def __repr__(self):
        return f'<PendingOTP user={self.user_id} expires={self.expires_at.isoformat()}>'

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

# Ensure new tables are created (e.g., PendingOTP)
with app.app_context():
    try:
        db.create_all()
    except Exception as _e:
        app.logger.warning(f"db.create_all() failed: {_e}")
    # Lightweight schema migration for new columns on existing tables (SQLite-only safe ops)
    try:
        from sqlalchemy import text
        # Check columns on student table and add missing ones (SQLite-safe)
        res = db.session.execute(text("PRAGMA table_info(student)")).fetchall()
        cols = {r[1].lower() for r in res}
        if 'email_verified' not in cols:
            db.session.execute(text("ALTER TABLE student ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT 0"))
            db.session.commit()
        if 'is_admin' not in cols:
            db.session.execute(text("ALTER TABLE student ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
            db.session.commit()
    except Exception as _e:
        app.logger.warning(f"Schema check/migrate failed or not needed: {_e}")

# Email utility

def send_email(to_email: str, subject: str, body: str) -> bool:
    mail_mode = (app.config.get('MAIL_MODE') or '').lower()
    mail_from = app.config.get('MAIL_FROM')
    mirror_file = bool(app.config.get('MAIL_MIRROR_FILE'))

    def _write_eml():
        try:
            out_dir = os.path.join(app.instance_path, 'outbox')
            os.makedirs(out_dir, exist_ok=True)
            filename = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{secrets.token_hex(4)}.eml"
            path = os.path.join(out_dir, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"From: {mail_from}\n")
                f.write(f"To: {to_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write("Content-Type: text/plain; charset=UTF-8\n\n")
                f.write(body)
            app.logger.info(f"Email written to {path}")
            return True
        except Exception as e:
            app.logger.error(f"Failed to write email file: {e}")
            return False

    # Development mode: only write to file
    if mail_mode == 'file':
        return _write_eml()

    # Default: SMTP mode (optionally mirror to file)
    if mirror_file:
        _write_eml()

    server = app.config.get('MAIL_SERVER')
    username = app.config.get('MAIL_USERNAME')
    password = app.config.get('MAIL_PASSWORD')
    port = app.config.get('MAIL_PORT')
    use_tls = app.config.get('MAIL_USE_TLS')
    use_ssl = app.config.get('MAIL_USE_SSL')

    if not (server and username and password and mail_from):
        app.logger.warning('Email not sent: MAIL_* env vars not fully configured')
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = to_email
    msg.set_content(body)

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(server, port, context=context) as smtp:
                smtp.login(username, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(server, port) as smtp:
                if use_tls:
                    context = ssl.create_default_context()
                    smtp.starttls(context=context)
                smtp.login(username, password)
                smtp.send_message(msg)
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email to {to_email}: {e}")
        return False

# Token utilities for email verification
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

def _get_serializer():
    key = app.config['SECRET_KEY']
    return URLSafeTimedSerializer(key, salt='edureach-email-verify')

# Helper for building absolute URLs in emails that work across devices/LAN
from typing import Any

def build_abs_url(endpoint: str, **values: Any) -> str:
    base = (app.config.get('EXTERNAL_BASE_URL') or '').strip()
    if base:
        # Build a relative path then prepend the configured base
        path = url_for(endpoint, _external=False, **values)
        return base.rstrip('/') + path
    # Fallback to Flask's external URL using current request host
    return url_for(endpoint, _external=True, **values)

# Routes
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not getattr(current_user, 'is_admin', False):
            flash('Admin access required')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return _wrapped

@app.route('/')
def home():
    return render_template('index.html')

# Dev helper gate: only allow localhost or when app.debug is True

def _dev_allowed():
    try:
        ra = request.remote_addr or ''
    except Exception:
        ra = ''
    return app.debug or ra in ('127.0.0.1', '::1')

# Helper: send verification email for a student
from urllib.parse import urljoin

def _send_verification_email(student) -> bool:
    try:
        token = _get_serializer().dumps(student.email)
        # Build absolute URL: if behind reverse proxy, adjust as needed
        verify_link = build_abs_url('verify_email', token=token)
        body = (
            "YOUR REGISTRATION IS SUCCESSFUL, WELCOME TO EDUREACH\n\n"
            f"Hello {student.name},\n\n"
            f"Please verify your email to activate your account: {verify_link}\n\n"
            "If you did not sign up, please ignore this message.\n\n- EduReach"
        )
        return bool(send_email(student.email, 'Verify your EduReach email', body))
    except Exception as e:
        app.logger.error(f"Failed to compose/send verification email: {e}")
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        role = (data.get('role') or 'student').strip().lower()
        
        student = Student.query.filter_by(email=email).first()
        
        if student and check_password_hash(student.password_hash, password):
            # Enforce role selection for clarity
            if role == 'admin' and not getattr(student, 'is_admin', False):
                msg = 'This account is not an admin. Use "Login as Student".'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg})
                flash(msg)
                return render_template('auth/login.html')
            if role != 'admin' and getattr(student, 'is_admin', False):
                msg = 'This is an admin account. Use "Login as Admin".'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg})
                flash(msg)
                return render_template('auth/login.html')

            if not getattr(student, 'email_verified', False):
                msg = 'Email not verified. Please check your inbox for the verification link.'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg})
                flash(msg)
                return render_template('auth/login.html')
            # Step 1 passed: password verified and email verified. Generate and send OTP, require verification.
            otp_value = f"{secrets.randbelow(1000000):06d}"
            from werkzeug.security import generate_password_hash as _gph
            otp_hash = _gph(otp_value)
            PendingOTP.query.filter_by(user_id=student.id).delete()
            db.session.add(PendingOTP(user_id=student.id, otp_hash=otp_hash, expires_at=datetime.utcnow() + timedelta(minutes=5)))
            db.session.commit()
            session['pending_user_id'] = student.id
            send_email(
                to_email=student.email,
                subject='Your EduReach login OTP',
                body=f"Hello {student.name},\n\nYour one-time password (OTP) is: {otp_value}\nIt will expire in 5 minutes.\n\nIf you didn't attempt to login, please ignore this email.\n\n- EduReach"
            )
            if request.is_json:
                return jsonify({'success': True, 'otp_required': True, 'message': 'OTP sent to your email'})
            return redirect(url_for('verify_otp'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid email or password'})
            flash('Invalid email or password')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        name = data.get('name')
        email = data.get('email')
        class_level = data.get('class')
        password = data.get('password')
        
        # Check if student already exists
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email already registered'})
            flash('Email already registered')
            return render_template('auth/register.html')
        
# Create new student (unverified)
        student = Student(
            name=name,
            email=email,
            class_level=class_level,
            password_hash=generate_password_hash(password),
            email_verified=False
        )
        
        db.session.add(student)
        db.session.commit()

        # Send verification email (best-effort)
        _send_verification_email(student)
        
        msg = 'Registration successful! We sent a verification link to your email. Please verify, then login.'
        if request.is_json:
            return jsonify({'success': True, 'message': msg})
        flash(msg)
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    # Clean pending OTP for safety (if any)
    session.pop('pending_user_id', None)
    logout_user()
    return redirect(url_for('home'))

@app.route('/verify-email')
def verify_email():
    token = request.args.get('token', '')
    if not token:
        flash('Invalid verification link')
        return redirect(url_for('login'))
    try:
        email = _get_serializer().loads(token, max_age=60*60*24*3)  # 3 days
    except SignatureExpired:
        flash('Verification link expired. Please register again or request a new link.')
        return redirect(url_for('login'))
    except BadSignature:
        flash('Invalid verification token')
        return redirect(url_for('login'))

    student = Student.query.filter_by(email=email).first()
    if not student:
        flash('Account not found')
        return redirect(url_for('login'))
    if getattr(student, 'email_verified', False):
        flash('Email already verified. Please login.')
        return redirect(url_for('login'))

    student.email_verified = True
    db.session.add(student)
    db.session.commit()

    # Optional: send a welcome confirmation upon successful verification
    try:
        send_email(
            to_email=student.email,
            subject='Welcome to EduReach',
            body=f"YOUR REGISTRATION IS SUCCESSFUL, WELCOME TO EDUREACH\n\nHello {student.name},\n\nYour email has been verified successfully. You can now login to EduReach.\n\n- EduReach"
        )
    except Exception as e:
        app.logger.warning(f"Welcome email after verification failed: {e}")

    flash('Email verified successfully. Please login.')
    return redirect(url_for('login'))

@app.route('/auth/resend-verification', methods=['POST'])
def auth_resend_verification():
    data = request.get_json(force=True)
    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    student = Student.query.filter_by(email=email).first()
    if not student:
        return jsonify({'success': False, 'message': 'Account not found'}), 404
    if getattr(student, 'email_verified', False):
        return jsonify({'success': False, 'message': 'Email already verified'}), 400
    sent = _send_verification_email(student)
    return jsonify({'success': bool(sent), 'message': 'Verification email resent' if sent else 'Failed to resend email'})

@app.route('/auth/resend-otp', methods=['POST'])
def auth_resend_otp():
    # Use pending_user_id from session to avoid abuse
    pending_user_id = session.get('pending_user_id')
    if not pending_user_id:
        return jsonify({'success': False, 'message': 'No pending login session'}), 400
    student = Student.query.get(pending_user_id)
    if not student:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if not getattr(student, 'email_verified', False):
        return jsonify({'success': False, 'message': 'Email not verified'}), 400
    # Cooldown (optional): at most once every 30s
    from time import time as _time
    last = session.get('last_otp_sent_ts', 0)
    now = int(_time())
    if now - last < 30:
        return jsonify({'success': False, 'message': 'Please wait before requesting another OTP'}), 429
    # Generate and send OTP
    otp_value = f"{secrets.randbelow(1000000):06d}"
    from werkzeug.security import generate_password_hash as _gph
    otp_hash = _gph(otp_value)
    PendingOTP.query.filter_by(user_id=student.id).delete()
    db.session.add(PendingOTP(user_id=student.id, otp_hash=otp_hash, expires_at=datetime.utcnow() + timedelta(minutes=5)))
    db.session.commit()
    session['last_otp_sent_ts'] = now
    send_email(student.email, 'Your EduReach login OTP', f"Hello {student.name},\n\nYour one-time password (OTP) is: {otp_value}\nIt will expire in 5 minutes.\n\n- EduReach")
    return jsonify({'success': True, 'message': 'OTP resent'})

@app.route('/dev/verification-link')
def dev_verification_link():
    if not _dev_allowed():
        return jsonify({'success': False, 'message': 'Not allowed'}), 403
    email = (request.args.get('email') or '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    student = Student.query.filter_by(email=email).first()
    if not student:
        return jsonify({'success': False, 'message': 'Account not found'}), 404
    token = _get_serializer().dumps(student.email)
    link = build_abs_url('verify_email', token=token)
    return jsonify({'success': True, 'email': email, 'verification_link': link})

@app.route('/dev/send-otp', methods=['POST'])
def dev_send_otp():
    if not _dev_allowed():
        return jsonify({'success': False, 'message': 'Not allowed'}), 403
    data = request.get_json(force=True)
    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    student = Student.query.filter_by(email=email).first()
    if not student:
        return jsonify({'success': False, 'message': 'Account not found'}), 404
    if not getattr(student, 'email_verified', False):
        return jsonify({'success': False, 'message': 'Email not verified'}), 400
    otp_value = f"{secrets.randbelow(1000000):06d}"
    from werkzeug.security import generate_password_hash as _gph
    otp_hash = _gph(otp_value)
    PendingOTP.query.filter_by(user_id=student.id).delete()
    db.session.add(PendingOTP(user_id=student.id, otp_hash=otp_hash, expires_at=datetime.utcnow() + timedelta(minutes=5)))
    db.session.commit()
    send_email(student.email, 'Your EduReach login OTP', f"Hello {student.name},\n\nYour one-time password (OTP) is: {otp_value}\nIt will expire in 5 minutes.\n\n- EduReach")
    return jsonify({'success': True, 'message': 'OTP sent'})

@app.route('/dev/current-otp')
def dev_current_otp():
    if not _dev_allowed():
        return jsonify({'success': False, 'message': 'Not allowed'}), 403
    pending_user_id = session.get('pending_user_id')
    if not pending_user_id:
        return jsonify({'success': False, 'message': 'No pending OTP session'})
    
    # Get the most recent email file
    import os
    outbox_dir = os.path.join(app.instance_path, 'outbox')
    try:
        files = [f for f in os.listdir(outbox_dir) if f.endswith('.eml')]
        if not files:
            return jsonify({'success': False, 'message': 'No email files found'})
        
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(outbox_dir, f)))
        with open(os.path.join(outbox_dir, latest_file), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract OTP from email content
        import re
        otp_match = re.search(r'Your one-time password \(OTP\) is: (\d{6})', content)
        if otp_match:
            otp_code = otp_match.group(1)
            return jsonify({'success': True, 'otp': otp_code, 'file': latest_file})
        else:
            return jsonify({'success': False, 'message': 'OTP not found in email'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        code = (data.get('otp') or '').strip()
        pending_user_id = session.get('pending_user_id')
        if not pending_user_id:
            if request.is_json:
                return jsonify({'success': False, 'message': 'No pending OTP session'}), 400
            flash('No pending OTP session')
            return redirect(url_for('login'))
        # Fetch pending OTP record
        pending = PendingOTP.query.filter_by(user_id=pending_user_id).first()
        if not pending:
            if request.is_json:
                return jsonify({'success': False, 'message': 'OTP expired or not found'}), 400
            flash('OTP expired or not found')
            return redirect(url_for('login'))
        # Validate expiry
        if datetime.utcnow() > pending.expires_at:
            db.session.delete(pending)
            db.session.commit()
            if request.is_json:
                return jsonify({'success': False, 'message': 'OTP expired'}), 400
            flash('OTP expired')
            return redirect(url_for('login'))
        # Validate code
        from werkzeug.security import check_password_hash as _cph
        app.logger.info(f"OTP Verification - Received code: '{code}', Length: {len(code) if code else 0}")
        app.logger.info(f"OTP Verification - User ID: {pending_user_id}, Expires: {pending.expires_at}")
        if not code or not _cph(pending.otp_hash, code):
            app.logger.warning(f"OTP Verification FAILED for user {pending_user_id}")
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
            flash('Invalid OTP')
            return render_template('auth/verify_otp.html')
        # Success: login user
        user = Student.query.get(pending_user_id)
        db.session.delete(pending)
        db.session.commit()
        session.pop('pending_user_id', None)
        if user:
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'message': 'Login successful', 'is_admin': bool(getattr(user, 'is_admin', False))})
            if getattr(user, 'is_admin', False):
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            flash('User not found')
            return redirect(url_for('login'))
    # GET -> render OTP page
    return render_template('auth/verify_otp.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # If admin accidentally visits student dashboard, send to admin dashboard
    if getattr(current_user, 'is_admin', False):
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html')

@app.route('/courses')
@login_required
def courses():
    # Get all courses grouped by class and subject
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/api/courses')
@login_required
def api_courses():
    # Get all courses
    courses = Course.query.all()
    
    # Check for filter parameters in the query string
    class_filter = request.args.get('class')
    subject_filter = request.args.get('subject')
    
    # Apply filters if provided
    if class_filter:
        courses = [c for c in courses if c.class_level == class_filter]
    if subject_filter:
        courses = [c for c in courses if (c.subject or '').lower() == subject_filter.lower()]
    
    # Organize courses by class and subject
    result = []
    for course in courses:
        course_data = {
            'id': course.id,
            'name': course.name,
            'class_level': course.class_level,
            'subject': course.subject,
            'description': course.description,
            'videos': course.get_videos()
        }
        result.append(course_data)
    
    return jsonify(result)

@app.route('/assignments')
@login_required
def assignments():
    # Show assignments without referencing courses
    assignments = Assignment.query.all()
    return render_template('assignments.html', assignments=assignments)

@app.route('/api/assignments')
@login_required
def api_assignments():
    assignments = Assignment.query.all()
    return jsonify([{
        'id': a.id,
        'course_id': a.course_id,
        'title': a.title,
        'description': a.description
    } for a in assignments])

@app.route('/api/assignment/<int:assignment_id>/questions')
@login_required
def api_assignment_questions(assignment_id):
    import json as _json
    a = Assignment.query.get(assignment_id)
    if not a:
        return jsonify({'success': False, 'message': 'Assignment not found'}), 404
    try:
        parsed = _json.loads(a.questions) if a.questions else []
        if not isinstance(parsed, list):
            parsed = []
    except Exception:
        parsed = []
    return jsonify({'success': True, 'questions': parsed})

@app.route('/api/submit_assignment', methods=['POST'])
@login_required
def submit_assignment():
    import json as _json
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    answers = data.get('answers') or []

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'success': False, 'message': 'Assignment not found'})

    # Determine scoring strategy: MCQ JSON vs free-text
    score = 0
    try:
        parsed = _json.loads(assignment.questions) if assignment.questions else None
    except Exception:
        parsed = None

    correct = None
    total = None
    if isinstance(parsed, list) and all(isinstance(x, dict) for x in parsed):
        # MCQ: compare letter keys
        total = len(parsed)
        correct = 0
        for i, q in enumerate(parsed):
            ans_letter = (answers[i] if i < len(answers) else '').strip().lower()
            if ans_letter and q.get('answer', '').strip().lower() == ans_letter:
                correct += 1
        score = int(round((correct / total) * 100)) if total else 0
    else:
        # Free-text fallback: keep previous simple scoring (presence-based)
        score = len(answers) * 10

    # Store progress (keep score as percentage for backward compatibility)
    progress = Progress.query.filter_by(
        student_id=current_user.id,
        assignment_id=assignment_id
    ).first()

    if not progress:
        progress = Progress(
            student_id=current_user.id,
            assignment_id=assignment_id
        )

    progress.score = score
    progress.completed = True
    progress.completed_at = datetime.utcnow()

    db.session.add(progress)
    db.session.commit()

    resp = {'success': True, 'score': progress.score}
    if correct is not None and total is not None:
        resp.update({'correct': correct, 'total': total})
    return jsonify(resp)

@app.route('/progress')
@login_required
def progress():
    student_progress = Progress.query.filter_by(student_id=current_user.id).all()
    return render_template('progress.html', progress_data=student_progress)

@app.route('/api/progress')
@login_required
def api_progress():
    student_progress = Progress.query.filter_by(student_id=current_user.id).all()
    import json as _json
    return jsonify([{
        'course_id': p.course_id,
        'assignment_id': p.assignment_id,
        'score': p.score,
        'completed': p.completed,
        'completed_at': p.completed_at.isoformat() if p.completed_at else None,
        'video_progress': (
            _json.loads(p.video_progress).get('completed', []) if p.video_progress else []
        )
    } for p in student_progress])

@app.route('/api/progress/course/<int:course_id>')
@login_required
def api_progress_course(course_id):
    import json as _json
    p = Progress.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if not p:
        return jsonify({'course_id': course_id, 'video_progress': [], 'completed': False})
    return jsonify({
        'course_id': course_id,
        'video_progress': _json.loads(p.video_progress).get('completed', []) if p.video_progress else [],
        'completed': p.completed,
        'completed_at': p.completed_at.isoformat() if p.completed_at else None
    })

@app.route('/api/debug/db')
@login_required
def api_debug_db():
    try:
        return jsonify({
            'db_uri': app.config.get('SQLALCHEMY_DATABASE_URI'),
            'assignments': Assignment.query.count(),
            'courses': Course.query.count(),
            'students': Student.query.count()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/video_complete', methods=['POST'])
@login_required
def api_progress_video_complete():
    import json as _json
    data = request.get_json(force=True)
    course_id = data.get('course_id')
    video_index = data.get('video_index')

    if course_id is None or video_index is None:
        return jsonify({'success': False, 'message': 'course_id and video_index are required'}), 400

    course = Course.query.get(course_id)
    if not course:
        return jsonify({'success': False, 'message': 'Course not found'}), 404

    videos = course.get_videos()
    if not isinstance(video_index, int) or video_index < 0 or video_index >= len(videos):
        return jsonify({'success': False, 'message': 'Invalid video_index'}), 400

    progress = Progress.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if not progress:
        progress = Progress(student_id=current_user.id, course_id=course_id)

    # Update video progress list
    current = []
    if progress.video_progress:
        try:
            current = _json.loads(progress.video_progress).get('completed', [])
        except Exception:
            current = []
    if video_index not in current:
        current.append(video_index)

    # Determine course completion
    course_completed = len(set(current)) >= len(videos) and len(videos) > 0
    progress.video_progress = _json.dumps({'completed': sorted(set(current))})
    progress.completed = course_completed
    if course_completed:
        progress.completed_at = datetime.utcnow()

    db.session.add(progress)
    db.session.commit()

    return jsonify({
        'success': True,
        'course_id': course_id,
        'completed_indices': sorted(set(current)),
        'total_videos': len(videos),
        'course_completed': course_completed
    })

# --- Admin routes ---
@app.route('/admin')
@admin_required
def admin_index():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Admin uploads
from werkzeug.utils import secure_filename

def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in app.config.get('ALLOWED_EXTENSIONS', set())

@app.route('/admin/uploads', methods=['GET', 'POST'])
@admin_required
def admin_uploads():
    upload_dir = app.config['UPLOAD_FOLDER']
    if request.method == 'POST':
        f = request.files.get('file')
        if not f or not f.filename:
            flash('No file selected')
            return redirect(url_for('admin_uploads'))
        if not _allowed_file(f.filename):
            flash('File type not allowed')
            return redirect(url_for('admin_uploads'))
        fn = secure_filename(f.filename)
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, fn)
        f.save(save_path)
        flash('File uploaded successfully')
        return redirect(url_for('admin_uploads'))
    # List files
    try:
        items = []
        for name in os.listdir(upload_dir):
            p = os.path.join(upload_dir, name)
            if os.path.isfile(p):
                items.append({'name': name, 'size': os.path.getsize(p), 'mtime': os.path.getmtime(p)})
        items.sort(key=lambda x: x['mtime'], reverse=True)
    except Exception:
        items = []
    # also load courses for the upload-video form
    try:
        course_list = Course.query.all()
    except Exception:
        course_list = []
    return render_template('admin/uploads.html', files=items, courses=course_list, allowed_ext=app.config.get('ALLOWED_EXTENSIONS', set()))

@app.route('/admin/uploads/courses', methods=['POST'])
@admin_required
def admin_upload_courses():
    import csv
    f = request.files.get('file')
    if not f or not f.filename:
        flash('Upload a CSV file with course data')
        return redirect(url_for('admin_uploads'))
    if not f.filename.lower().endswith('.csv'):
        flash('Please upload a .csv file')
        return redirect(url_for('admin_uploads'))
    try:
        text = f.read().decode('utf-8-sig')
        reader = csv.DictReader(text.splitlines())
        created = 0
        updated = 0
        for row in reader:
            name = (row.get('name') or '').strip()
            class_level = (row.get('class_level') or '').strip()
            subject = (row.get('subject') or '').strip()
            description = (row.get('description') or '').strip()
            if not name or not class_level:
                continue
            existing = Course.query.filter_by(name=name, class_level=class_level, subject=subject).first()
            if existing:
                existing.description = description or existing.description
                db.session.add(existing)
                updated += 1
            else:
                db.session.add(Course(name=name, class_level=class_level, subject=subject, description=description))
                created += 1
        db.session.commit()
        flash(f'Courses processed. Created: {created}, Updated: {updated}')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to import courses: {e}')
    return redirect(url_for('admin_uploads'))

@app.route('/admin/uploads/videos', methods=['POST'])
@admin_required
def admin_upload_videos():
    import json as _json
    course_id = request.form.get('course_id')
    videos_json = request.form.get('videos_json', '')
    if not course_id or not videos_json.strip():
        flash('Select a course and paste videos JSON')
        return redirect(url_for('admin_uploads'))
    course = Course.query.get(int(course_id))
    if not course:
        flash('Course not found')
        return redirect(url_for('admin_uploads'))
    try:
        data = _json.loads(videos_json)
        if not isinstance(data, list):
            raise ValueError('JSON must be a list of objects with title/url')
        # Basic normalize: keep only known fields
        norm = []
        for item in data:
            if not isinstance(item, dict):
                continue
            t = (item.get('title') or '').strip()
            u = (item.get('url') or '').strip()
            d = (item.get('description') or '').strip()
            if not (t and u):
                continue
            entry = {'title': t, 'url': u, 'description': d}
            # Optional i18n for per-language titles
            i18n = item.get('title_i18n') or item.get('i18n') or {}
            if isinstance(i18n, dict):
                entry['title_i18n'] = {k.strip(): (v or '').strip() for k,v in i18n.items() if isinstance(k, str)}
            # Optional search_url passthrough (when no direct video link)
            if (item.get('search_url') or '').strip():
                entry['search_url'] = (item.get('search_url') or '').strip()
            norm.append(entry)
        if not norm:
            flash('No valid video entries found')
            return redirect(url_for('admin_uploads'))
        import json as _json2
        course.video_data = _json2.dumps(norm, ensure_ascii=False)
        db.session.add(course)
        db.session.commit()
        flash(f'Attached {len(norm)} videos to "{course.name}"')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to attach videos: {e}')
    return redirect(url_for('admin_uploads'))

@app.route('/admin/uploads/download/<path:filename>')
@admin_required
def admin_upload_download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        
        # Log contact to file
        log_dir = os.path.join(app.root_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'contacts.log')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.utcnow().isoformat()} - {name} ({email}): {message}\n")
        
        # Also store in database
        contact_log = ContactLog(name=name, email=email, message=message)
        db.session.add(contact_log)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Message sent successfully'})
        flash('Message sent successfully!')
    
    return render_template('contact.html')

@app.route('/api/translations/<language>')
def get_translations(language):
    """Get translations for specified language"""
    translations = {
        'en': {
            'title': 'EduReach',
            'tagline': 'Education for Rural People',
            'home': 'Home',
            'login': 'Login',
            'courses': 'Courses',
            'assignments': 'Assignments',
            'progress': 'Progress',
            'contact': 'Contact',
            'about_text': 'EduReach is dedicated to providing quality education access to rural communities through innovative technology and comprehensive learning resources.',
            'physics': 'Physics',
            'chemistry': 'Chemistry',
            'mathematics': 'Mathematics',
            'assignments_subtitle': 'Test your knowledge and track your progress',
            'ninth_class_label': '9th Class:',
            'tenth_class_label': '10th Class:',
            'clear_filters': 'Clear Filters',
            'no_match_title': 'No matching assignments',
            'no_match_desc': 'Try clearing filters or selecting a different subject.',
            'submit_assignment': 'Submit Assignment',
            'assignment_completed': 'Assignment Completed!',
            'your_score': 'Your Score:',
            'question_label': 'Question',
            'enter_answer_placeholder': 'Enter your answer here...'
        },
        'te': {
            'title': 'ఎడ్యుఆర్చ్',
            'tagline': 'గ్రామీణ ప్రజలకు విద్య',
            'home': 'హోమ్',
            'login': 'లాగిన్',
            'courses': 'కోర్సులు',
            'assignments': 'అసైన్‌మెంట్స్',
            'progress': 'పురోగతి',
            'contact': 'సంప్రదించండి',
            'about_text': 'ఎడ్యుఆర్చ్ ఆవిష్కర సాంకేతికత మరియు సమగ్ర అభ్యాస వనరుల ద్వారా గ్రామీణ సమాజాలకు గుణమైన విద్య అందించడానికి అంకితం చేయబడింది.',
            'physics': 'భౌతిక శాస్త్రం',
            'chemistry': 'రసాయన శాస్త్రం',
            'mathematics': 'గణితం',
            'assignments_subtitle': 'మీ జ్ఞానాన్ని పరీక్షించండి మరియు మీ పురోగతిని ట్రాక్ చేయండి',
            'ninth_class_label': '9వ తరగతి:',
            'tenth_class_label': '10వ తరగతి:',
            'clear_filters': 'ఫిల్టర్‌లు క్లియర్ చేయండి',
            'no_match_title': 'పోలిన అసైన్‌మెంట్లు లేవు',
            'no_match_desc': 'ఫిల్టర్‌లను క్లియర్ చేయండి లేదా వేరే అంశాన్ని ఎంచుకోండి.',
            'submit_assignment': 'అసైన్‌మెంట్ పంపించండి',
            'assignment_completed': 'అసైన్‌మెంట్ పూర్తయింది!',
            'your_score': 'మీ స్కోరు:',
            'question_label': 'ప్రశ్న',
            'enter_answer_placeholder': 'మీ సమాధానాన్ని ఇక్కడ నమోదు చేయండి...'
        },
        'kn': {
            'title': 'ಎಡ್ಯುರೀಚ್',
            'tagline': 'ಗ್ರಾಮೀಣ ಜನರಿಗೆ ಶಿಕ್ಷಣ',
            'home': 'ಮುಖ್ಯಪುಟ',
            'login': 'ಲಾಗಿನ್',
            'courses': 'ಕೋರ್ಸ್‌ಗಳು',
            'assignments': 'ಕಾರ್ಯಯೋಜನೆಗಳು',
            'progress': 'ಪ್ರಗತಿ',
            'contact': 'ಸಂಪರ್ಕಿಸಿ',
            'about_text': 'ಎಡ್ಯುರೀಚ್ ನವೀನ ತಂತ್ರಜ್ಞಾನ ಮತ್ತು ಸಮಗ್ರ ಕಲಿಕಾ ಸಂಪನ್ಮೂಲಗಳ ಮೂಲಕ ಗ್ರಾಮೀಣ ಸಮುದಾಯಗಳಿಗೆ ಗುಣಮಟ್ಟದ ಶಿಕ್ಷಣ ಪ್ರವೇಶವನ್ನು ಒದಗಿಸಲು ಸಮರ್ಪಿಸಲಾಗಿದೆ.',
            'physics': 'ಭೌತಶಾಸ್ತ್ರ',
            'chemistry': 'ರಸಾಯನಶಾಸ್ತ್ರ',
            'mathematics': 'ಗಣಿತ',
            'assignments_subtitle': 'ನಿಮ್ಮ ಜ್ಞಾನವನ್ನು ಪರೀಕ್ಷಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಪ್ರಗತಿಯನ್ನು ಕಣ್ಗಾಲಿಡಿ',
            'ninth_class_label': '9ನೇ ತರಗತಿ:',
            'tenth_class_label': '10ನೇ ತರಗತಿ:',
            'clear_filters': 'ಫಿಲ್ಟರ್‌ಗಳನ್ನು ತೆರವುಗೊಳಿಸಿ',
            'no_match_title': 'ಹೊಂದುವ ಕಾರ್ಯಯೋಜನೆಗಳಿಲ್ಲ',
            'no_match_desc': 'ಫಿಲ್ಟರ್ ತೆರವು ಮಾಡಿ ಅಥವಾ ಬೇರೆ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ.',
            'submit_assignment': 'ಕಾರ್ಯಯೋಜನೆ ಸಲ್ಲಿಸಿ',
            'assignment_completed': 'ಕಾರ್ಯಯೋಜನೆ ಪೂರ್ಣಗೊಂಡಿದೆ!',
            'your_score': 'ನಿಮ್ಮ ಅಂಕ:',
            'question_label': 'ಪ್ರಶ್ನೆ',
            'enter_answer_placeholder': 'ನಿಮ್ಮ ಉತ್ತರವನ್ನು ಇಲ್ಲಿ ನಮೂದಿಸಿ...'
        }
    }
    
    return jsonify(translations.get(language, translations['en']))

# Debug-only seeding endpoint for 9th class assignments (Chemistry & Mathematics)
@app.route('/admin/seed/assignments_9th', methods=['POST', 'GET'])
@login_required
def admin_seed_assignments_9th():
    if not app.debug:
        return jsonify({'success': False, 'message': 'Seeding disabled in production'}), 403
    import json as _json
    # Define MCQs (ASCII-safe)
    CHEMISTRY_9TH = [
        {"q": "Matter is made up of:", "options": {"a": "Molecules", "b": "Atoms", "c": "Both atoms and molecules", "d": "Compounds"}, "answer": "c"},
        {"q": "The process of conversion of solid directly into gas is called:", "options": {"a": "Condensation", "b": "Evaporation", "c": "Sublimation", "d": "Fusion"}, "answer": "c"},
        {"q": "Which of the following is a mixture?", "options": {"a": "Water", "b": "Air", "c": "Sodium chloride", "d": "Carbon dioxide"}, "answer": "b"},
        {"q": "Table salt (NaCl) is a:", "options": {"a": "Element", "b": "Mixture", "c": "Compound", "d": "Alloy"}, "answer": "c"},
        {"q": "Proton was discovered by:", "options": {"a": "J.J. Thomson", "b": "Rutherford", "c": "Goldstein", "d": "Chadwick"}, "answer": "c"},
        {"q": "Neutron has:", "options": {"a": "Positive charge", "b": "Negative charge", "c": "No charge", "d": "Double charge"}, "answer": "c"},
        {"q": "Burning of magnesium ribbon is an example of:", "options": {"a": "Combination reaction", "b": "Decomposition", "c": "Neutralization", "d": "Displacement"}, "answer": "a"},
        {"q": "2KClO3 -> 2KCl + 3O2 is an example of:", "options": {"a": "Combination", "b": "Decomposition", "c": "Redox", "d": "Neutralization"}, "answer": "b"},
        {"q": "Modern periodic table is arranged in order of:", "options": {"a": "Atomic mass", "b": "Atomic number", "c": "Valency", "d": "Mass number"}, "answer": "b"},
        {"q": "Who is known as the father of the periodic table?", "options": {"a": "Mendeleev", "b": "Dalton", "c": "Thomson", "d": "Rutherford"}, "answer": "a"},
        {"q": "Litmus turns red in:", "options": {"a": "Base", "b": "Acid", "c": "Neutral solution", "d": "Salt solution"}, "answer": "b"},
        {"q": "NaOH is a:", "options": {"a": "Acid", "b": "Base", "c": "Salt", "d": "Oxide"}, "answer": "b"},
        {"q": "Which is a good conductor of electricity?", "options": {"a": "Sulphur", "b": "Carbon", "c": "Copper", "d": "Phosphorus"}, "answer": "c"},
        {"q": "Non-metals are generally:", "options": {"a": "Ductile", "b": "Good conductors", "c": "Brittle", "d": "Lustrous"}, "answer": "c"},
        {"q": "The general formula of alkanes is:", "options": {"a": "CnH2n", "b": "CnH2n+2", "c": "CnH2n-2", "d": "CnH2nO2"}, "answer": "b"},
        {"q": "Diamond and graphite are:", "options": {"a": "Isotopes", "b": "Isomers", "c": "Allotropes", "d": "Compounds"}, "answer": "c"},
        {"q": "Hardness of water is due to the presence of:", "options": {"a": "Na+", "b": "Ca2+ and Mg2+", "c": "K+", "d": "Cl-"}, "answer": "b"},
        {"q": "Pure water is a:", "options": {"a": "Compound", "b": "Mixture", "c": "Element", "d": "Suspension"}, "answer": "a"},
        {"q": "Major component of air is:", "options": {"a": "Oxygen", "b": "Nitrogen", "c": "Carbon dioxide", "d": "Argon"}, "answer": "b"},
        {"q": "Which gas is responsible for greenhouse effect?", "options": {"a": "Oxygen", "b": "Carbon dioxide", "c": "Nitrogen", "d": "Argon"}, "answer": "b"},
        {"q": "Which of the following is a physical change?", "options": {"a": "Burning of wood", "b": "Rusting of iron", "c": "Melting of ice", "d": "Digestion"}, "answer": "c"},
        {"q": "Smallest particle of an element is:", "options": {"a": "Atom", "b": "Molecule", "c": "Compound", "d": "Mixture"}, "answer": "a"},
        {"q": "Law of conservation of mass was given by:", "options": {"a": "Dalton", "b": "Lavoisier", "c": "Rutherford", "d": "Boyle"}, "answer": "b"},
        {"q": "The most reactive group of non-metals is:", "options": {"a": "Group 14", "b": "Group 17 (Halogens)", "c": "Group 18 (Noble gases)", "d": "Group 1"}, "answer": "b"},
        {"q": "Which acid is found in vinegar?", "options": {"a": "Citric acid", "b": "Hydrochloric acid", "c": "Acetic acid", "d": "Sulphuric acid"}, "answer": "c"},
        {"q": "Which metal is liquid at room temperature?", "options": {"a": "Mercury", "b": "Sodium", "c": "Potassium", "d": "Calcium"}, "answer": "a"},
        {"q": "The simplest hydrocarbon is:", "options": {"a": "Methane", "b": "Ethane", "c": "Propane", "d": "Butane"}, "answer": "a"},
        {"q": "Which process is used to remove temporary hardness of water?", "options": {"a": "Boiling", "b": "Sedimentation", "c": "Filtration", "d": "Distillation"}, "answer": "a"},
        {"q": "Oxygen gas is produced in plants during:", "options": {"a": "Respiration", "b": "Photosynthesis", "c": "Transpiration", "d": "Absorption"}, "answer": "b"},
        {"q": "Which noble gas is used in electric bulbs?", "options": {"a": "Helium", "b": "Neon", "c": "Argon", "d": "Krypton"}, "answer": "c"}
    ]
    MATHEMATICS_9TH = [
        {"q": "pi is:", "options": {"a": "Rational", "b": "Irrational", "c": "Integer", "d": "Natural number"}, "answer": "b"},
        {"q": "Every rational number is:", "options": {"a": "Integer", "b": "Real number", "c": "Irrational number", "d": "Complex number"}, "answer": "b"},
        {"q": "A polynomial of degree 1 is called:", "options": {"a": "Linear", "b": "Quadratic", "c": "Cubic", "d": "Constant"}, "answer": "a"},
        {"q": "(x - 2) is a factor of x^2 - 4x + k, find k.", "options": {"a": "4", "b": "2", "c": "0", "d": "-4"}, "answer": "a"},
        {"q": "The graph of a linear equation in two variables is a:", "options": {"a": "Point", "b": "Line", "c": "Curve", "d": "Circle"}, "answer": "b"},
        {"q": "The solution of 2x + 3 = 7 is:", "options": {"a": "1", "b": "2", "c": "-2", "d": "3"}, "answer": "b"},
        {"q": "The x-coordinate is also called:", "options": {"a": "Ordinate", "b": "Abscissa", "c": "Origin", "d": "Axis"}, "answer": "b"},
        {"q": "The point (0, 5) lies on:", "options": {"a": "X-axis", "b": "Y-axis", "c": "Origin", "d": "None"}, "answer": "b"},
        {"q": "Probability of getting a head in one coin toss is:", "options": {"a": "1", "b": "1/2", "c": "1/4", "d": "2"}, "answer": "b"},
        {"q": "Probability of getting number > 6 in a dice throw is:", "options": {"a": "1/6", "b": "0", "c": "6/6", "d": "1/2"}, "answer": "b"},
        {"q": "Mean of 2, 4, 6, 8 is:", "options": {"a": "4", "b": "5", "c": "6", "d": "10"}, "answer": "b"},
        {"q": "In a data set, the most frequent observation is called:", "options": {"a": "Median", "b": "Mean", "c": "Mode", "d": "Range"}, "answer": "c"},
        {"q": "Volume of a cube of side a is:", "options": {"a": "a^2", "b": "2a^3", "c": "a^3", "d": "6a^2"}, "answer": "c"},
        {"q": "Surface area of a sphere of radius r is:", "options": {"a": "2pi r^2", "b": "3pi r^2", "c": "4pi r^2", "d": "pi r^2"}, "answer": "c"},
        {"q": "In a right triangle, the square of hypotenuse = sum of squares of other sides. This is:", "options": {"a": "Thales Theorem", "b": "Pythagoras Theorem", "c": "Converse of midpoint theorem", "d": "None"}, "answer": "b"},
        {"q": "Sum of angles of a triangle is:", "options": {"a": "90 degrees", "b": "180 degrees", "c": "270 degrees", "d": "360 degrees"}, "answer": "b"},
        {"q": "Angle subtended by a diameter of a circle at the circumference is:", "options": {"a": "60 degrees", "b": "90 degrees", "c": "120 degrees", "d": "180 degrees"}, "answer": "b"},
        {"q": "The tangent to a circle is always ______ to the radius at point of contact.", "options": {"a": "Parallel", "b": "Perpendicular", "c": "Equal", "d": "Tangent"}, "answer": "b"},
        {"q": "Perpendicular bisector of a line divides it into:", "options": {"a": "Unequal parts", "b": "Two equal parts", "c": "Three equal parts", "d": "None"}, "answer": "b"},
        {"q": "The instrument used for construction of arcs is:", "options": {"a": "Ruler", "b": "Compass", "c": "Protractor", "d": "Divider"}, "answer": "b"},
        {"q": "sqrt(2) is:", "options": {"a": "Rational", "b": "Irrational", "c": "Integer", "d": "Whole number"}, "answer": "b"},
        {"q": "The degree of polynomial 7x^3 - 2x^2 + 5 is:", "options": {"a": "1", "b": "2", "c": "3", "d": "0"}, "answer": "c"},
        {"q": "A line parallel to x-axis has slope:", "options": {"a": "0", "b": "1", "c": "infinity", "d": "-1"}, "answer": "a"},
        {"q": "Probability of an impossible event is:", "options": {"a": "1", "b": "0", "c": "1/2", "d": "None"}, "answer": "b"},
        {"q": "Median of 3, 5, 7 is:", "options": {"a": "3", "b": "5", "c": "7", "d": "6"}, "answer": "b"},
        {"q": "Volume of cylinder = ?", "options": {"a": "pi r^2 h", "b": "2 pi r h", "c": "4/3 pi r^3", "d": "pi r h^2"}, "answer": "a"},
        {"q": "In an equilateral triangle, each angle = ?", "options": {"a": "45 degrees", "b": "60 degrees", "c": "90 degrees", "d": "120 degrees"}, "answer": "b"},
        {"q": "The longest chord of a circle is:", "options": {"a": "Radius", "b": "Diameter", "c": "Tangent", "d": "Sector"}, "answer": "b"},
        {"q": "The bisectors of angles of a triangle meet at:", "options": {"a": "Centroid", "b": "Incenter", "c": "Circumcenter", "d": "Orthocenter"}, "answer": "b"},
        {"q": "Angle at the center is ______ the angle at the circumference.", "options": {"a": "Equal to", "b": "Half", "c": "Double", "d": "None"}, "answer": "c"}
    ]
    def _find_course(class_level: str, subject: str):
        return Course.query.filter_by(class_level=class_level, subject=subject).first()
    def _upsert_assignment(title: str, description: str, course, questions_list):
        a = Assignment.query.filter_by(title=title).first()
        questions_json = _json.dumps(questions_list, ensure_ascii=False)
        if a:
            a.description = description
            a.course_id = course.id if course else None
            a.questions = questions_json
            db.session.add(a)
            return a
        a = Assignment(title=title, description=description, course_id=(course.id if course else None), questions=questions_json)
        db.session.add(a)
        return a
    chem_course = _find_course('9th', 'Chemistry')
    math_course = _find_course('9th', 'Mathematics')
    _upsert_assignment('9th Class Chemistry – 30 MCQs', 'Comprehensive 30 MCQs across 9th Class Chemistry syllabus.', chem_course, CHEMISTRY_9TH)
    _upsert_assignment('9th Class Mathematics – 30 MCQs', 'Comprehensive 30 MCQs across 9th Class Mathematics syllabus.', math_course, MATHEMATICS_9TH)
    db.session.commit()
    return jsonify({'success': True, 'seeded': ['9th Class Chemistry – 30 MCQs', '9th Class Mathematics – 30 MCQs']})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed admin user if ADMIN_EMAIL and ADMIN_PASSWORD provided
        admin_email = os.getenv('ADMIN_EMAIL', '').strip()
        admin_password = os.getenv('ADMIN_PASSWORD', '').strip()
        if admin_email and admin_password:
            existing = Student.query.filter_by(email=admin_email).first()
            if not existing:
                try:
                    db.session.add(Student(
                        name='Administrator',
                        email=admin_email,
                        class_level='admin',
                        password_hash=generate_password_hash(admin_password),
                        email_verified=True,
                        is_admin=True
                    ))
                    db.session.commit()
                    app.logger.info(f"Seeded admin account: {admin_email}")
                except Exception as e:
                    app.logger.error(f"Failed to seed admin user: {e}")
            else:
                # Ensure existing account marked as admin (do not change password here)
                if not getattr(existing, 'is_admin', False):
                    existing.is_admin = True
                    existing.email_verified = True
                    db.session.add(existing)
                    db.session.commit()
        else:
            app.logger.info('ADMIN_EMAIL/ADMIN_PASSWORD not set; skipping admin seeding')
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    app.run(host=host, port=port, debug=True)
