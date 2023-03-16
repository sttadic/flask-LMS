import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps


# Configure application
app = Flask(__name__)


# Configure session to use filesystem, not cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 library to use SQLite database
db = SQL("sqlite:///library.db")


# Ensure responses are not cached for privacy reasons
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Login required decorator, url: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=['GET', 'POST'])
def login():
    '''Librarian login'''

    # Clear any user_id
    session.clear()

    # User reached route via GET
    if request.method == 'GET':
        return render_template('login.html')
    
    # User reached route via POST
    else:
        # Ensure username and password are submitted
        if not request.form.get('username') or not request.form.get('password'):
            flash('Username and password are required fields!')
            return render_template('login.html')
        
        # Query database for username
        user_name = db.execute('SELECT * FROM staff WHERE username = ?', request.form.get('username'))

        # Ensure username exists and password is correct
        if len(user_name) != 1 or not check_password_hash(user_name[0]['hash'], request.form.get('password')):
            flash('Incorrect username and/or password!')
            return render_template('login.html')
        
        # Remember user that has logged in
        session['user_id'] = user_name[0]['staff_id']

        # Redirect user to a home page
        return redirect('/')
    

@app.route('/logout')
def logout():
    '''Librarian logout'''
    
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect('/login')


@app.route('/register', methods = ['GET', 'POST'])
def register():
    '''Register librarian'''

    # User reached route via GET
    if request.method == 'GET':
        return render_template('register.html')

    # User reached route via POST
    else:
        # Check if name provided
        if not request.form.get('name'):
            flash('Name is required field')
            return render_template('register.html')

        # Get username from user input
        user_name = request.form.get('username')
        
        # Check if username provided
        if not user_name:
            flash('Username is required field')
            return render_template('register.html')
        
        # Check if username already in database
        elif db.execute('SELECT * FROM staff WHERE username = ?', user_name):
            flash('That username already exists')
            return render_template('register.html')

        # Get password from user input
        password = request.form.get('password')

        # Check if password provided
        if not password:
            flash('Password is required field')
            return render_template('register.html')
        
        # Ensure password and confirmation password match
        elif password != request.form.get('confirmation'):
            flash('Password and confirmation password do not match')
            return render_template('register.html')
        
        # Generate hash for password
        hash = generate_password_hash(password)

        # Store name, username and password hash into database
        db.execute('INSERT INTO staff (name, username, hash) VALUES (?, ?, ?)', request.form.get('name'), user_name, hash)
        
        # Get staff_id from database
        id = db.execute('SELECT staff_id FROM staff WHERE username = ?', user_name)

        # Remember registered user
        session['user_id'] = id[0]['staff_id']

        # Redirect user to a home page
        return redirect('/')    


@app.route('/')
@login_required
def index():
    '''Index page: show list of issued books'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    #

    # Render index.html
    return render_template('index.html', name=name)


@app.route('/books')
@login_required
def books():
    '''Books sorted alphabetically by title, author or genre. Search and issue book options'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # User reached route via 'By Title' link
    if request.args.get('sort') == 'title':
        # Query database for books and sort by title
        books = db.execute('SELECT * FROM books ORDER BY title ASC')
        return render_template('books.html', books=books, name=name)
    
    # User reached route via 'By Author' link
    elif request.args.get('sort') == 'author':
        # Query database for books and sort by author
        books = db.execute('SELECT * FROM books ORDER BY author ASC')
        return render_template('books.html', books=books, name=name)
    
    # User reached route via 'By Genre' link
    elif request.args.get('sort') == 'genre':
        # Query database for books and sort by genre
        books = db.execute('SELECT * FROM books ORDER BY genre ASC')
        return render_template('books.html', books=books, name=name)
    
    # Search books title, author or id
    q = request.args.get('query')
    if q:
        # Query database for title, author and id (id requires precise search query) based on the search input and render template with results
        books = db.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR id LIKE ?', '%' + q + '%', '%' + q + '%', q)
        return render_template('books.html', name=name, books=books)


@app.route('/members', methods = ['GET', 'POST'])
@login_required
def members():
    '''Show list of all members with options to manage and add new ones'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # User reached route via GET
    if request.method == 'GET':      

        # Query database for members
        members = db.execute('SELECT * FROM members ORDER BY name ASC')  

        # Search members
        q = request.args.get('query')
        if q:
            # Query database for id and name of members based on the search input and render template with results
            members = db.execute('SELECT * FROM members WHERE member_id LIKE ? OR name LIKE ?', q, '%' + q + '%')
            return render_template('members.html', name=name, members=members)

    # User reached route via POST
    else:
        # Get the value of the button user clicked on
        button = request.form.get('button')
        
        # If user clicked on delete
        if button == 'delete':

            # Delete member
            db.execute('DELETE FROM members WHERE member_id == ?', request.form.get('id'))

            # Query database for members
            members = db.execute('SELECT * FROM members ORDER BY name ASC')
   
            # Render members.html
            return render_template('members.html', name=name, members=members)
        
        # If user clicked on edit
        elif button == 'edit':

            name = request.form.get('name')
            email = request.form.get('email')
            address = request.form.get('address')
            phone = request.form.get('phone')
            
            db.execute('UPDATE members SET name = ?, email = ?, address = ?, phone = ? WHERE member_id == ?', name, email, address, phone, request.form.get('id'))

            # Query database for members
            members = db.execute('SELECT * FROM members ORDER BY name ASC')
   
            # Render members.html
            return render_template('members.html', name=name, members=members)
    
    # Query database for members
    members = db.execute('SELECT * FROM members ORDER BY name ASC')
    
    # Render members.html
    return render_template('members.html', name=name, members=members)


@app.route('/new-member', methods = ['GET', 'POST'])
@login_required
def newMember():
    '''Add new members form'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # User reached route via GET
    if request.method == 'GET':
        return render_template('new-member.html', name=name)
    
    # User reached route via POST
    else:
        # Get data from user input
        member = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        phone = request.form.get('phone')
        
        # Ensure all details are provided
        if not member or not email or not address or not phone:
            flash('All fields are required')
            return render_template('new-member.html', name=name)

        # Insert new member details into members table
        db.execute('INSERT INTO members (name, email, address, phone) VALUES (?, ?, ?, ?)', member, email, address, phone)
        
        # Redirect to members route
        return redirect('/members')
    


# Main driver function
if __name__ == '__main__':
    app.run()