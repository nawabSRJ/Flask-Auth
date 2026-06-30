from flask import render_template, url_for
from app import create_app

app = create_app()

@app.route('/')
@app.route('/signup')
def home():
    return render_template('/signup.html')

@app.route('/login')
def login():
    return render_template('/login.html')

if __name__ == '__main__':
    app.run(debug=True)

