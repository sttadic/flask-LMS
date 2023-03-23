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


GENRES = ['Autobiography', 'Biography', 'Business', 'Children', 'Drama', 'Fantasy', 'Fiction', 'Historical Fiction', 'Horror', 'Humor', 'Memoir', 'Mystery', 'Non-fiction', 'Poetry', 'Romance', 'Science Fiction', 'Self-help', 'Spiritual/Religious', 'Thriller', 'Travel']


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
            flash('Username and password fields are required!')
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
    '''Register new librarian'''

    # User reached route via GET
    if request.method == 'GET':
        return render_template('register.html')

    # User reached route via POST
    else:

        # Get name from user input
        name = request.form.get('name')

        # Ensure name is provided
        if not name:
            flash('Name field is required')
            return render_template('register.html')

        # Get username from user input
        user_name = request.form.get('username')
        
        # Check if username provided
        if not user_name:
            flash('Username field is required')
            return render_template('register.html')
        
        # Username already in database
        elif db.execute('SELECT * FROM staff WHERE username = ?', user_name):
            flash('Username already exists')
            return render_template('register.html')

        # Get password from user input
        password = request.form.get('password')

        # Check if password provided
        if not password:
            flash('Password field is required')
            return render_template('register.html')
        
        # Ensure password is at least 4 characters long
        if len(password) < 4:
            flash('Password must be at least four characters long')
            return render_template('register.html')
        
        # Ensure password and confirmation password match
        elif password != request.form.get('confirmation'):
            flash('Password and confirmation password do not match')
            return render_template('register.html')
        
        # Generate hash for password
        hash = generate_password_hash(password)

        # Store name, username and password hash into database
        db.execute('INSERT INTO staff (name, username, hash) VALUES (?, ?, ?)', name, user_name, hash)
        
        # Get staff_id from database
        id = db.execute('SELECT staff_id FROM staff WHERE username = ?', user_name)

        # Remember registered user
        session['user_id'] = id[0]['staff_id']

        # Redirect user to a home page
        return redirect('/')


@app.route('/')
@login_required
def index():
    '''Index page: show list of currently issued books'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    #

    # Render index.html
    return render_template('index.html', name=name)


@app.route('/catalogue')
@login_required
def catalogue():
    '''Books sorted alphabetically by title, author or genre. Current stock and search books feature'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Sort by title
    if request.args.get('sort') == 'title':
        
        # Redirect to catalogue route - default is sorted by title
        return redirect('/catalogue')
    
    # Sort by author
    elif request.args.get('sort') == 'author':
        
        # Query database for books and sort by author
        books = db.execute('SELECT * FROM books ORDER BY author ASC')
        return render_template('catalogue.html', books=books, name=name)
    
    # Sort by genre
    elif request.args.get('sort') == 'genre':
        
        # Query database for books and sort by genre
        books = db.execute('SELECT * FROM books ORDER BY genre ASC')
        return render_template('catalogue.html', books=books, name=name)
    
    # Search books query by user
    q = request.args.get('query')

    # Search query submitted
    if q:
        # Query database for title, author and id (id requires precise search query) based on the search input and render template with results
        books = db.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR id LIKE ?', '%' + q + '%', '%' + q + '%', q)
        return render_template('catalogue.html', name=name, books=books)
    
    # User reached route from navbar - query database for books and sort by title
    books = db.execute('SELECT * FROM books ORDER BY title ASC')
    return render_template('catalogue.html', books=books, name=name)


@app.route('/books', methods = ['GET', 'POST'])
@login_required
def books():
    '''Books management'''

    # Get user_id from session
    user_id =  session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Query database for books and sort by title
    books = db.execute('SELECT * FROM books ORDER BY title ASC')

    # User reached route via GET
    if request.method == 'GET':
        
        # Search books query by user
        q = request.args.get('query')

        # Search query submitted
        if q:
            # Query database for title, author and id (id requires precise search query) based on the search input and render template with results
            books = db.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR id LIKE ?', '%' + q + '%', '%' + q + '%', q)
            return render_template('books.html', name=name, books=books)
        
        # Render manage books template
        return render_template('books.html', books=books, name=name, genres=GENRES)       
    
    # User reached route via POST
    else:
        # Get the value of the button user clicked on
        button = request.form.get('button')
        
        # Remove button selected
        if button == 'remove':
            
            # Query database for the title of the book to be removed
            removed = db.execute('SELECT title FROM books WHERE id == ?', request.form.get('id'))[0]['title']

            # Delete book
            db.execute('DELETE FROM books WHERE id == ?', request.form.get('id'))            

            # Flash book is removed message
            flash(f'Book "{removed}" has been successfully removed!')

            # Redirect to books route with updated table
            return redirect('/books')
        
        # Update button selected on popup form
        elif button == 'update':

            # User input
            id = request.form.get('form_id')
            title = request.form.get('title') 
            author = request.form.get('author')
            genre = request.form.get('genre')
            year = request.form.get('year')

            # Ensure valid input for stock levels
            try:
                stock = int(request.form.get('stock'))
                if stock < 1:
                    flash('Invalid stock input')
                    return redirect('/books')
            except:
                flash('Invalid stock input')
                return redirect('/books')
            
            # Ensure all details are provided
            if not title or not author or not genre or not year:
                flash('All fields are required')
                return redirect('/books')

            # Update books table
            db.execute('UPDATE books SET title = ?, author = ?, genre = ?, year = ?, stock = ? WHERE id == ?', title, author, genre, year, stock, id)

            # Flash a message
            flash(f'Book ID:{id} details updated!')

            # Redirect to books route with updated table
            return redirect('/books')
        

@app.route('/new-book', methods = ['GET', 'POST'])
@login_required
def new_book():
    '''Add new book'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # User reached route via GET
    if request.method == 'GET':

        # Render new_book template
        return render_template('new-book.html', name=name, genres=GENRES)
    
    # User reached route via POST
    else:
        # User input
        title = request.form.get('title') 
        author = request.form.get('author')
        genre = request.form.get('genre')
        year = request.form.get('year')
        
        # Ensure all details are provided
        if not title or not author or not genre or not year:
            flash('All fields are required')
            return redirect('/new-book')

        # Ensure valid input for stock
        try:
            stock = int(request.form.get('stock'))
            if stock < 1:
                flash('Invalid stock input')
                return redirect('/new-book')
        except:
            flash('Invalid stock input')
            return redirect('/new-book')  

        # Insert new book details into books table
        db.execute('INSERT INTO books (title, author, genre, year, stock) VALUES (?, ?, ?, ?, ?)', title, author, genre, year, stock)
        
        # Flash book added message on redirect
        flash(f'A book "{title}" by "{author}" has been added.')
       
        # Redirect to manage books route
        return redirect('/books')


@app.route('/members', methods = ['GET', 'POST'])
@login_required
def members():
    '''Members management'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Query database for members ordered by name
    members = db.execute('SELECT * FROM members ORDER BY name ASC')  

    # User reached route via GET
    if request.method == 'GET':      

        # Search members query by user
        q = request.args.get('query')

        # Search query submitted
        if q:
            # Query database for id and name of members based on the search input and render template with results
            members = db.execute('SELECT * FROM members WHERE member_id LIKE ? OR name LIKE ?', q, '%' + q + '%')
            return render_template('members.html', name=name, members=members)
        
         # Render members.html
        return render_template('members.html', name=name, members=members)

    # User reached route via POST
    else:
        # Get the value of the button user clicked on
        button = request.form.get('button')
        
        # Remove button selected
        if button == 'remove':
            
            # Query database for a name of a member to be deleted
            removed = db.execute('SELECT name FROM members WHERE member_id == ?', request.form.get('id'))[0]['name']

            # Delete member
            db.execute('DELETE FROM members WHERE member_id == ?', request.form.get('id'))            

            # Flash a message that memeber is removed
            flash(f'Member {removed} has been removed.')

            # Redirect to members route with updated table
            return redirect('/members')
        
        # Update button selceted on a popup form
        elif button == 'update':

            # User input
            id = request.form.get("form_id")
            member = request.form.get('name')
            email = request.form.get('email')
            address = request.form.get('address')
            phone = request.form.get('phone')

            # Ensure all details provided
            if not member or not email or not address or not phone:
                flash('All fields are required')
                return render_template('members.html', name=name, members=members)

            # Update members table
            db.execute('UPDATE members SET name = ?, email = ?, address = ?, phone = ? WHERE member_id == ?', member, email, address, phone, id)
            
            flash(f'Member ID:{id} details updated!')
            
            # Redirect to members route with updated table
            return redirect('/members')
        
     
@app.route('/new-member', methods = ['GET', 'POST'])
@login_required
def new_member():
    '''Add new member'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # User reached route via GET
    if request.method == 'GET':
        return render_template('new-member.html', name=name)
    
    # User reached route via POST
    else:
        # User input
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
        
        # Flash member added message on redirect
        flash(f'A member {member} joins the library.')
       
        # Redirect to members route
        return redirect('/members')
    

@app.route('/checkout', methods = ['GET', 'POST'])
@login_required
def checkout():
    '''Lending books to members'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Query database for members ordered by name
    members = db.execute('SELECT * FROM members ORDER BY name ASC')  

    # User reached route via GET
    if request.method == 'GET':      

        # Search members query by user
        q = request.args.get('query')

        # Search query submitted
        if q:
            # Query database for id and name of members based on the search input and render template with results
            members = db.execute('SELECT * FROM members WHERE member_id LIKE ? OR name LIKE ?', q, '%' + q + '%')
            return render_template('checkout.html', name=name, members=members)
        
         # Render checkout template
        return render_template('checkout.html', name=name, members=members)
    
    # User reached route via POST
    else:
        return
        


# Main driver function
if __name__ == '__main__':
    app.run()