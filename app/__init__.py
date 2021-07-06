import os
from flask import Flask, render_template, send_from_directory, request, flash
from flask_wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SubmitField, validators, ValidationError
from dotenv import load_dotenv
from . import db
#login and registartion end points
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

load_dotenv()
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
app.secret_key = 'development identification key'
db.init_app(app)

@app.route('/')
def index():
    return render_template('home.html', title="MLH Fellow", url=os.getenv("URL"))

@app.route('/projects')
def projects():
    return render_template('projects.html', title="Projects", url=os.getenv("URL"))

@app.route('/about')
def about():
    return render_template('about.html', title="About", url=os.getenv("URL"))

@app.route('/health')
def health():
    return render_template('health.html',  title="Health"), 200


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            return 'Form submitted.'
 
    elif request.method == 'GET':
        return render_template('contact.html', form=form)

 
class ContactForm(Form):
  name = TextField("Name",  [validators.Required("Please enter your name.")])
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address")])
  subject = TextField("Subject",  [validators.Required("Please enter a subject.")])
  message = TextAreaField("Message",  [validators.Required("Please enter a message.")])
  submit = SubmitField("Send")



@app.route('/register', methods=('GET', 'POST'))
def register():
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    ## TODO: Return a restister page
    #return "Register Page not yet implemented", 501
    return render_template('register.html')



#...

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            return "Login Successful", 200 
        else:
            return error, 418
    
    ## TODO: Return a login page
    #return "Login Page not yet implemented", 501
    return render_template('login.html')
