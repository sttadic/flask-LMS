import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash, jsonify
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


GENRES = ['Art', 'Autobiography', 'Biography', 'Business', 'Children', 'Comics', 'Cookbooks', 'Drama', 'Fantasy', 'Fiction', 'Graphic Novel', 'Historical Fiction', 'History', 'Horror', 'Humor', 'Memoir', 'Music', 'Mystery', 'Non-fiction', 'Other', 'Poetry', 'Psychology', 'Romance', 'Science', 'Science Fiction', 'Self-help', 'Spiritual/Religious', 'Sports', 'Thriller', 'Travel']


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
        user_name = db.execute('SELECT * FROM staff WHERE username = ? AND deleted = ?', request.form.get('username'), 0)

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


@app.route('/', methods = ['GET', 'POST'])
@login_required
def index():
    '''Index page: show list of currently issued books. Return functionality'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']
    
    # Query database for transactions, books & members (members sorted by transaction date, so the member with the oldest transaction, book first due for return, would show on top of the table)
    transactions = db.execute('SELECT * FROM transactions WHERE type = ?', 'borrow')
    members = db.execute('SELECT * FROM members JOIN transactions ON members.member_id = transactions.borrower_id WHERE type = ? GROUP BY members.name ORDER BY transactions.time ASC', 'borrow')
    books = db.execute('SELECT * FROM books')

    # User reached route via GET
    if request.method == 'GET':
        member_due = []

        # User query
        q = request.args.get('query')

        # Iterate over members dict
        for member in members:
            # Append member to the member_due list if one has any number of borrowed books
            if member['borrowed'] > 0:
                member_due.append(member)

        # Query exists
        if q:
            # Query database for a member whose id is equal to query and has any number of borrowed books
            mem_search = db.execute('SELECT * FROM members WHERE member_id = ? AND borrowed > ?', q, 0)
            return render_template('index.html', name=name, members=mem_search)
            
        # Render index.html
        return render_template('index.html', name=name, members=member_due)

    # User reached route via POST
    else:
         
        # Check request header and send whole list of books and transactions as json response
        if request.headers['Content-Type'] == 'application/x-www-form-urlencoded; charset=UTF-8':
            return jsonify(books, transactions)
        
        # User selection
        book_id = request.form.get('id')
        book_ids = request.form.getlist('all_ids')
        member_id = request.form.get('memberId')

        if book_id:

            # Query database for number of books borrowed by a particular member
            borrowed = db.execute('SELECT borrowed FROM members WHERE member_id = ?', member_id)[0]['borrowed']

            # Query database for book availability
            available = db.execute('SELECT available FROM books WHERE id = ?', book_id)[0]['available']

            # Update transaction type from borrow to borrowed (so fronted script can filter out books that are not in the possesion of a member anymore, and table can be used for transactions history)
            db.execute('UPDATE transactions SET type = ? WHERE borrower_id = ? AND book_id = ?', 'borrowed', member_id, book_id)

            # Insert new data into transactions table
            db.execute('INSERT INTO transactions (borrower_id, book_id, type, employee_id) VALUES (?, ?, ?, ?)', member_id, book_id, 'returned', user_id)

            # Update book availability
            db.execute('UPDATE books SET available = ? WHERE id = ?', available + 1, book_id)

            # Update number of books borrowed by a member
            db.execute('UPDATE members SET borrowed = ? WHERE member_id = ?', borrowed - 1, member_id)

            flash('Book returned')
            
            return redirect('/')
        
        if book_ids:
            # Iterate over list of book ids
            for book_id in book_ids:

                # Query database for number of books borrowed by a particular member
                borrowed = db.execute('SELECT borrowed FROM members WHERE member_id = ?', member_id)[0]['borrowed']

                # Query database for book availability
                available = db.execute('SELECT available FROM books WHERE id = ?', book_id)[0]['available']

                # Update transaction type from borrow to borrowed (so fronted script can filter out books that are not in the possesion of a member anymore, and table can be used for transactions history)
                db.execute('UPDATE transactions SET type = ? WHERE borrower_id = ? AND book_id = ?', 'borrowed', member_id, book_id)

                # Insert new data into transactions table
                db.execute('INSERT INTO transactions (borrower_id, book_id, type, employee_id) VALUES (?, ?, ?, ?)', member_id, book_id, 'returned', user_id)

                # Update book availability
                db.execute('UPDATE books SET available = ? WHERE id = ?', available + 1, book_id)

                # Update number of books borrowed by a member
                db.execute('UPDATE members SET borrowed = ? WHERE member_id = ?', borrowed - 1, member_id)

            flash('All books returned')
            
            return redirect('/')


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
        books = db.execute('SELECT * FROM books WHERE deleted = ? ORDER BY author ASC', 0)
        return render_template('catalogue.html', books=books, name=name)
    
    # Sort by genre
    elif request.args.get('sort') == 'genre':
        
        # Query database for books and sort by genre
        books = db.execute('SELECT * FROM books WHERE deleted = ? ORDER BY genre ASC', 0)
        return render_template('catalogue.html', books=books, name=name)
    
    # User reached route from navbar - query database for books and sort by title
    books = db.execute('SELECT * FROM books WHERE deleted = ? ORDER BY title ASC', 0)
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
    books = db.execute('SELECT * FROM books WHERE deleted = ? ORDER BY title ASC', 0)    

    # User reached route via GET
    if request.method == 'GET':
        
        # Search books query and selected field
        query = request.args.get('query')
        field = request.args.get('field')

        # Query exists and search by field is 'id', return exact match as JSON response
        if query and field == 'id':
            match = db.execute('SELECT * FROM books WHERE deleted = ? AND id = ?', 0, query)
            return jsonify(match)
        
        # Any other search field selected
        elif query and field != 'id':
            # Populate matches list and return JSON response with matching items
            matches = [book for book in books if query.lower() in str(book[field]).lower()]
            return jsonify(matches)  
        
        # Render books template 
        return render_template('books.html', books=books, name=name, genres=GENRES)
    
    # User reached route via POST
    else:
        # Get the value of the button user clicked on
        button = request.form.get('button')
        
        # Remove button selected
        if button == 'remove':
            
            # Query database for the title of the book to be removed
            removed = db.execute('SELECT title FROM books WHERE id = ?', request.form.get('id'))[0]['title']

            # Delete book (tag as deleted)
            db.execute('UPDATE books SET deleted = ? WHERE id = ?', 1, request.form.get('id'))            

            # Flash book removed message
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
            db.execute('UPDATE books SET title = ?, author = ?, genre = ?, year = ?, stock = ? WHERE id = ?', title, author, genre, year, stock, id)

            # Flash a message
            flash(f'Book ID:{id} details updated!')

            # Redirect to books route and show updated table
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
        db.execute('INSERT INTO books (title, author, genre, year, stock, available) VALUES (?, ?, ?, ?, ?, ?)', title, author, genre, year, stock, stock)
        
        # Flash book added message on redirect
        flash(f'A book "{title}" by "{author}" has been added.')
       
        # Redirect to manage books route
        return redirect('/catalogue')


@app.route('/members', methods = ['GET', 'POST'])
@login_required
def members():
    '''Members management'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Query database for members ordered by name
    members = db.execute('SELECT * FROM members WHERE deleted = ? ORDER BY name ASC', 0)  

    # User reached route via GET
    if request.method == 'GET':

        # Search members query and selected field
        query = request.args.get('query')
        field = request.args.get('field')

        # Query exists and search by field is 'id', return exact match as JSON response
        if query and field == 'member_id':
            match = db.execute('SELECT * FROM members WHERE deleted = ? AND member_id = ?', 0, query)
            return jsonify(match)
        
        # Any other search field selected
        elif query and field != 'member_id':
            # Populate matches list and return JSON response with matching items
            matches = [member for member in members if query.lower() in str(member[field]).lower()]
            return jsonify(matches)
        
        # Render members.html
        return render_template('members.html', name=name, members=members)

    # User reached route via POST
    else:
        # Get the value of the button user clicked on
        button = request.form.get('button')
        
        # Remove button selected
        if button == 'remove':
            
            # Query database for a name of a member to be deleted
            removed = db.execute('SELECT name FROM members WHERE member_id = ?', request.form.get('id'))[0]['name']

            # Delete member (tag as deleted)
            db.execute('UPDATE members SET deleted = ? WHERE member_id = ?', 1, request.form.get('id'))

            # Flash a message
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
            db.execute('UPDATE members SET name = ?, email = ?, address = ?, phone = ? WHERE member_id = ?', member, email, address, phone, id)
            
            flash(f'Member ID:{id} details updated!')
            
            # Redirect to members route and show updated table
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
        db.execute('INSERT INTO members (name, email, address, phone, borrowed) VALUES (?, ?, ?, ?, ?)', member, email, address, phone, 0)
        
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

    members = db.execute('SELECT * FROM members WHERE deleted = ?', 0)
    books = db.execute('SELECT * FROM books WHERE deleted = ?', 0)
    transactions = db.execute('SELECT * FROM transactions')

    # User reached route via GET
    if request.method == 'GET':

        # Sarch queries
        queryMember = request.args.get('queryMember')
        queryBook = request.args.get('queryBook')

        # User searched for members
        if queryMember:
            # Return entire list of members as JSON response
            return jsonify(members)
        
        # User searched for books
        if queryBook:
            # Return entire list of books and transactions as JSON response
            return jsonify(books, transactions)        
        
        # Render checkout template
        return render_template('checkout.html', name=name)
    
    # User reached route via POST
    else:
        # Get a list of book ids and member id from user input      
        memberId = request.form.get('memberId')
        bookIds = request.form.getlist('bookId')
        
        # Iterate over bookIds
        for id in bookIds:

            # Query database for book availability and number of books borrowed for a particular member
            available = db.execute('SELECT available FROM books WHERE id = ?', id)[0]['available']
            borrowed = db.execute('SELECT borrowed FROM members WHERE member_id = ?', memberId)[0]['borrowed']

            # Insert all data into transactions table
            db.execute('INSERT INTO transactions (borrower_id, book_id, type, employee_id) VALUES (?, ?, ?, ?)', memberId, id, 'borrow', user_id)

            # Update books availability in books table and number of books borrowed in members table
            db.execute('UPDATE books SET available = ? WHERE id = ?', available - 1, id)
            db.execute('UPDATE members SET borrowed = ? WHERE member_id = ?', borrowed + 1, memberId)
        
        # Query for member's name from database
        member_name = db.execute('SELECT * FROM members WHERE member_id = ?', memberId)[0]['name']

        # Flash a message
        flash(f'Books successfully checked out to {member_name}')

        # Redirect to index page
        return redirect('/')


@app.route('/history')
@login_required
def history():
    '''Transactions history'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Query database for all transactions and join other tables
    transactions = db.execute('SELECT transactions.*, members.name, books.title, staff.name as staff_name FROM transactions JOIN books ON books.id=transactions.book_id JOIN members ON member_id=transactions.borrower_id JOIN staff ON staff_id=employee_id ORDER BY transactions.time DESC')

    return render_template('history.html', name=name, transactions=transactions)


@app.route('/register', methods = ['GET', 'POST'])
def register():
    '''Register new librarian'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # User reached route via POST
    if request.method == 'POST':

        # User input
        name = request.form.get('name')
        user_name = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Ensure all fields provided
        if not name or not user_name or not password:
            flash('All fields required')
            return redirect('/register')

        # Username already in database (even if tagged as deleted)
        elif db.execute('SELECT * FROM staff WHERE username = ?', user_name):
            flash('Username already exists')
            return redirect('/register')

        # Ensure password is at least 4 characters long
        if len(password) < 4:
            flash('Password must be at least four characters long')
            return redirect('/register')
        
        # Ensure password and confirmation password match
        elif password != confirmation:
            flash('Password and confirmation password do not match')
            return redirect('/register')
        
        # Generate hash for password
        hash = generate_password_hash(password)

        # Store name, username and password hash into database
        db.execute('INSERT INTO staff (name, username, hash) VALUES (?, ?, ?)', name, user_name, hash)
        
        # Redirect user
        flash('New librarian has been added')
        return redirect('/register')
    
    # Route reached via GET
    return render_template('/register.html', name=name)


@app.route('/remove', methods = ['GET', 'POST'])
def remove():
    '''Remove librarian'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Query database for all librarians except admin
    staff = db.execute('SELECT * FROM staff WHERE staff_id <> ? AND deleted = ?', 1, 0)

    # Route reached via POST
    if request.method == 'POST':

        # User selection
        staff_id = request.form.get('remove')

        # Query database for librarian name
        l_name = db.execute('SELECT name FROM staff WHERE staff_id = ?', staff_id)[0]['name']

        # Remove librarian (tag as deleted)
        db.execute('UPDATE staff SET deleted = ? WHERE staff_id = ?', 1,staff_id)

        # Flash a message on removal
        flash(f'Librarian { l_name } has been removed from LMS')

        return redirect('/remove')

    # Route reached via GET
    return render_template('remove.html', name=name, staff=staff)
        
    
@app.route('/account', methods = ['GET', 'POST'])
def account():
    '''Password change'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    # Route reached via POST
    if request.method == 'POST':

        # User input
        old_pass = request.form.get('old_pass')
        new_pass = request.form.get('new_pass')
        confirm_pass = request.form.get('confirm_pass')

        # Query database for a current password of a logged in librarian
        current_pass = db.execute('SELECT hash FROM staff WHERE staff_id = ?', user_id)[0]['hash']
        
        # Check if user input matches current password
        if not check_password_hash(current_pass, old_pass):
            flash('Invalid password')
            return redirect('/account')

        # Ensure all fields provided
        if not old_pass or not new_pass:
            flash('All fields required')
            return redirect('/account')
        
        # Ensure password is at least 4 characters long
        if len(new_pass) < 4:
            flash('Password must be at least four characters long')
            return redirect('/account')
        
        # Ensure new password matches confirm password
        elif new_pass != confirm_pass:
            flash('New password and confirmation password do not match')
            return redirect('/account')
        
        # Generate hash for a new password
        hash = generate_password_hash(new_pass)

        # Update database
        db.execute('UPDATE staff SET hash = ? WHERE staff_id = ?', hash, user_id)

        flash('Password changed')

        return redirect('/account')
        

    # Route reached via GET
    return render_template('account.html', name=name)
    


@app.route('/faq')
@login_required
def faq():
    '''Frequently asked questions'''

    # Get user_id from session
    user_id = session['user_id']

    # Query database for librarian name
    name = db.execute('SELECT name FROM staff WHERE staff_id = ?', user_id)[0]['name']

    return render_template('faq.html', name=name)




# Main driver function
if __name__ == '__main__':
    app.run()