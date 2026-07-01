from flask import Flask, Blueprint, render_template, redirect, url_for, session, flash, current_app
from flask import request as req
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.db import get_db_connection
import uuid
import os

user_bp = Blueprint('user', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============= SHARED VALIDATION HELPER =============
def validate_user_fields(name, email, age, course, gender, phone):
    """
    Validates the fields common to both signup and profile update
    (name, email, age, course, gender, phone).
    Returns a tuple: (error_message_or_None, validated_age_or_None)
    """
    if not all([name, email, age, course, gender, phone]):
        return 'All fields are required', None

    try:
        age = int(age)
    except ValueError:
        return 'Age must be a number', None

    if age < 5 or age > 100:
        return 'Age must be between 5 and 100', None

    if not phone.isdigit() or len(phone) != 10:
        return 'Phone must be exactly 10 digits', None

    return None, age


@user_bp.get('/signup')
def signup_page():
    return render_template('signup.html')


@user_bp.post('/signup')
def signup():
    name             = req.form.get('name')
    email            = req.form.get('email')
    age              = req.form.get('age')
    course           = req.form.get('course')
    gender           = req.form.get('gender')
    phone            = req.form.get('phone')
    password         = req.form.get('password')
    confirm_password = req.form.get('confirm_password')

    error, age = validate_user_fields(name, email, age, course, gender, phone)
    if error:
        return render_template('signup.html', error=error)

    if not password or not confirm_password:
        return render_template('signup.html', error='Password is required')

    if len(password) < 8:
        return render_template('signup.html', error='Password must be at least 8 characters long')

    if password != confirm_password:
        return render_template('signup.html', error='Passwords do NOT match')

    # ============= HANDLE PHOTO UPLOAD =============
    photo_filename = None  # default if no file uploaded

    file = req.files.get('the_file')
    if file and file.filename != '':            # user actually selected a file
        if not allowed_file(file.filename):
            return render_template('signup.html', error='Only image files are allowed (png, jpg, jpeg, gif)')

        flash(f'Flash : Thanks, your file {file.filename} has been uploaded!')
        filename       = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        # current_app is a flask context variable that gives access to the app's config
        upload_folder  = current_app.config['UPLOAD_FOLDER']
        file.save(os.path.join(upload_folder, unique_filename))
        photo_filename = unique_filename         # save this to DB ~ basically saving the path only, not the photo itself

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s OR phone = %s",
                (email, phone)
            )
            existing = cursor.fetchone()
            if existing:
                return render_template('signup.html', error='Email or Phone already exists')

            hashed_password = generate_password_hash(password)
            cursor.execute(
                """INSERT INTO users (name, email, password, phone, age, gender, course, photo)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (name, email, hashed_password, phone, age, gender, course, photo_filename)
            )
    except Exception as e:
        return render_template('signup.html', error=f'Exception occurred : {e}')
    finally:
        conn.close()

    return redirect(url_for('user.login'))


@user_bp.get('/login')
def login():
    return render_template('login.html')


@user_bp.post('/login')
def login_post():
    email    = req.form.get('email')
    password = req.form.get('password')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

    except Exception as e:
        return render_template('login.html', error=f'Exception occurred : {e}')

    finally:
        conn.close()

    if not user:
        return render_template('login.html', error='User does not exist')

    if not check_password_hash(user['password'], password):
        return render_template('login.html', error='Incorrect password')

    session['user'] = {
        'name'  : user['name'],
        'email' : user['email'],
        'age'   : user['age'],
        'course': user['course'],
        'gender': user['gender'],
        'phone' : user['phone'],
        'photo' : user['photo'],   # ← include photo in session
    }

    return redirect(url_for('user.dashboard'))


# ---- define the protected route decorator ----
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function


@user_bp.get('/dashboard')
@login_required
def dashboard():
    user = session.get('user')
    return render_template('dashboard.html', user=user)


@user_bp.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))


# ============= USER UPDATION =============
@user_bp.post('/update_profile')
@login_required
def update_profile():
    current_email = session['user']['email']  # trusted, not from form

    name   = req.form.get('name')
    email  = req.form.get('email')
    age    = req.form.get('age')
    course = req.form.get('course')
    gender = req.form.get('gender')
    phone  = req.form.get('phone')

    user = session.get('user')  # fallback context for re-rendering dashboard

    error, age = validate_user_fields(name, email, age, course, gender, phone)
    if error:
        return render_template('dashboard.html', user=user, error=error)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE (email = %s OR phone = %s) AND email != %s",
                (email, phone, current_email)
            )
            existing = cursor.fetchone()
            if existing:
                return render_template('dashboard.html', user=user, error='Email or Phone already in use by another account')

            cursor.execute(
                """UPDATE users
                   SET name = %s, email = %s, phone = %s, age = %s, gender = %s, course = %s
                   WHERE email = %s""",
                (name, email, phone, age, gender, course, current_email)
            )
    except Exception as e:
        return render_template('dashboard.html', user=user, error=f'Exception occurred : {e}')
    finally:
        conn.close()

    # refresh session with updated values
    session['user'] = {
        'name'  : name,
        'email' : email,
        'age'   : age,
        'course': course,
        'gender': gender,
        'phone' : phone,
        'photo' : user['photo'],   # ← keep existing photo unchanged
    }

    return redirect(url_for('user.dashboard'))


# ============= USER DELETION =============
@user_bp.post('/delete')
@login_required                                # ← added login_required, was missing before
def delete_profile():
    current_email = session['user']['email']

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE email = %s", (current_email,))
    except Exception as e:
        user = session.get('user')
        return render_template('dashboard.html', user=user, error=f'Exception occurred : {e}')
    finally:
        conn.close()

    session.clear()
    return redirect(url_for('user.signup_page'))