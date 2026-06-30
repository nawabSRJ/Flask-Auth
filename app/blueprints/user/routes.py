from flask import Flask, Blueprint, render_template, redirect, url_for, session
from flask import request as req
from functools import wraps

user_bp = Blueprint('user', __name__)

# user store
users_db = {}   # dict of dictionaries, since email is unique, it will be our key

@user_bp.post('/signup')
def signup():
    name = req.form.get('name')
    email = req.form.get('email')
    age = req.form.get('age')
    course = req.form.get('course')
    gender = req.form.get('gender')
    password = req.form.get('password')
    confirm_password = req.form.get('confirm_password')
    
    # validation
    if int(age) < 5 or int(age) > 100:
        return render_template('signup.html', error='Age must be between 5 and 100')

    # if len(password) < 8:
    #     return render_template('signup.html', error='Password must be at least 8 characters long')

    if password != confirm_password:
        return render_template('signup.html', error='Passwords do NOT match')
    
    if email in users_db:
        return render_template('signup.html', error='Email already registered')
    
    # store the user
    users_db[email] = {
        "name": name,
        "email": email,
        "age": age,
        "course" : course,
        "gender" : gender,
        "password": password,
    }

    # redirect to login after successful signup
    return redirect(url_for('user.login'))


@user_bp.get('/login')
def login():
    return render_template('login.html')


@user_bp.post('/login')
def login_post():
    email = req.form.get('email')
    password = req.form.get('password')

    user = users_db.get(email)
    if not user:
        return render_template('login.html', error='User does not exist')

    if user['password'] != password:
        return render_template('login.html', error='Incorrect password')

    # successful login - create session
    session['user'] = {
        'name'  : user['name'],
        'email' : user['email'],
        'age'   : user['age'],
        'course': user['course'],
        'gender': user['gender']
    }

    return redirect(url_for('user.dashboard'))



# ---- define the protected route decorator ----
# todo : understand this below and specially @wraps                                                                                                                                                                                                                                                                                                                                                 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:                   # ← check session
            return redirect(url_for('user.login'))  # ← not logged in, kick out
        return f(*args, **kwargs)                   # ← logged in, proceed normally
    return decorated_function



@user_bp.get('/dashboard')
@login_required
def dashboard():
    user = session.get('user')  # read from session
    return render_template('dashboard.html', user=user)

@user_bp.post('/logout')
def logout():
    session.clear()     # destroy the entire session ~ clears the session dict
    return redirect(url_for('user.login'))