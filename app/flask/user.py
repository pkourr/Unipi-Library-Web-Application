from pymongo import MongoClient
from flask import Flask, request,render_template,flash, url_for,redirect, session, Blueprint, render_template
from datetime import datetime, timedelta
import re
import string
import random
import os
from bson import ObjectId
from bson.errors import InvalidId


user=Blueprint("user",__name__,template_folder='templates')

# Connect to our local MongoDB
client = MongoClient(os.environ.get("MONGO_HOSTNAME","localhost"))

# Access databases and useful collections
db = client['UnipiLibrary']
users=db['Users']
books=db['Books']
reservations=db['Bookings']


# Endpoint to register a new user to the system
@user.route('/registerUser', methods=['GET', 'POST'])
def registerUser():
    requestsDict = {"visError": "hidden"}

    # Check if request method is POST (form submit)
    if request.method == 'POST':
        session['username'] = None
        session['email'] = None
        session['loggedIn'] = False
        session['password'] = None
        session['userId'] = None  # Initialize userId in session

        username = request.form['username']
        email = request.form['email']
        name = request.form['firstName']
        surname = request.form['lastName']
        password = request.form['password']
        birthdate = request.form['birthdate']

        if not email or not username or not name or not surname \
                or not password or not birthdate:
            flash("Information incomplete")
            requestsDict['visError'] = 'visible'
            return render_template("registerUser.html", requestsDict=requestsDict)

        passExpression = "(?=.*\d)(?=.*\D){8,}"
        if not re.search(passExpression, password):
            flash("Password is incorrect. It must contain at least 8 characters and at least 1 digit.")
            requestsDict['visError'] = 'visible'
            return render_template("registerUser.html", requestsDict=requestsDict)

        if users.find_one({"email": email}) or users.find_one({"username": username}):
            flash("A user with the same username or email already exists.")
            requestsDict['visError'] = 'visible'
            return render_template("registerUser.html", requestsDict=requestsDict)

        user = {"email": email, "username": username, \
                "name": name, "surname": surname, "password": password, \
                "birthdate": birthdate, "active": 'True'}

        # Insert the new user and get the inserted ID
        inserted_user = users.insert_one(user)
        inserted_id = inserted_user.inserted_id

        # Set session variables
        session["loggedIn"] = True
        session["username"] = username
        session["password"] = password  # Storing password in session is not recommended for security reasons
        session["userId"] = str(inserted_id)  # Store userId in session

        return redirect(url_for('user.searchBook'))

    return render_template("registerUser.html", requestsDict=requestsDict)


# Endpoint to login an existing user
@user.route('/login', methods=['GET', 'POST'])
def login():
    session['username'] = None
    session['email'] = None
    session['loggedIn'] = False
    session['password'] = None
    session['userId'] = None  # Initialize userId in session
    requestsDict = {"visError": "hidden"}

    # Check if request method is POST (form submit)
    if request.method == 'POST':
        loginUser = request.form['user']
        password = request.form['password']

        # Validation check about request's data
        if not loginUser or not password:
            flash("All fields should be filled")
            requestsDict['visError'] = 'visible'
            return render_template('login.html', requestsDict=requestsDict)

        user_data = users.find_one({"$or": [{"username": loginUser}, {"email": loginUser}], "password": password})

        if user_data is None:
            flash("Incorrect username or/and password")
            requestsDict['visError'] = 'visible'
            return render_template('login.html', requestsDict=requestsDict)

        if user_data.get("active") != "True":
            flash("This account has been deactivated. You should activate it again to have access to the site.")
            requestsDict['visError'] = 'visible'
            return render_template('login.html', requestsDict=requestsDict)

        # Set session variables
        session["loggedIn"] = True
        session["username"] = user_data.get("username")
        session["email"] = user_data.get("email")
        session["password"] = password  # Storing password in session is not recommended for security reasons
        session["userId"] = str(user_data.get("_id"))  # Store userId in session

        return redirect(url_for('user.searchBook'))

    return render_template('login.html', requestsDict=requestsDict)

@user.route('/searchBook', methods=['GET', 'POST'])
def searchBook():
    session.pop('_flashes', None)
    if session.get('loggedIn'):
        requestsDict = {"books": [], "actSearch": "active", "visMessage": None, "visError": None, "message": None}

        if request.method == 'POST':
            if 'get_all_books' in request.form:
                booksData = list(books.find({}, {"_id": 1, "date": 1, "title": 1, "author": 1, "pages": 1, "avaliability": 1}))
                if booksData:
                    requestsDict['books'] = booksData
                else:
                    flash("No books found")
                return render_template('searchBook.html', requestsDict=requestsDict)

            title = request.form.get('title', None)
            author = request.form.get('author', None)
            date = request.form.get('date', None)
            isbn = request.form.get('_id', None)

            query = {}
            fields_to_return = {"_id": 1, "date": 1, "title": 1, "author": 1, "pages": 1, "avaliability": 1}

            if isbn:
                query["_id"] = ObjectId(isbn)
                fields_to_return.update({"abstract": 1, "rentdays": 1})

            if title:
                query["title"] = {"$regex": f"^{title}$", "$options": 'i'}

            if date:
                try:
                    dateStr = datetime.strptime(date, "%d/%m/%Y")
                    query["date"] = dateStr
                except ValueError:
                    flash("The date field should be in the format: dd/mm/yyyy")

            if author:
                query["author"] = {"$regex": f"^{author}$", "$options": 'i'}

            if not query:
                flash("At least one field should be filled")
            else:
                booksData = list(books.find(query, fields_to_return))
                if not booksData:
                    flash("No books found")
                else:
                    requestsDict['books'] = booksData

        return render_template('searchBook.html', requestsDict=requestsDict)

    return redirect(url_for('user.login'))


#Endpoint to rent a book
@user.route('/rentBook', methods=['GET', 'POST'])
def rentBook():
    session.pop('_flashes', None)
    if session.get('loggedIn'):
        requestsDict = {"booking": {}, "actBooking": "active", "visMessage": None, "visError": None, "message": None}

        if request.method == 'POST':
            isbn = request.form['isbn']
            name = request.form['name']
            surname = request.form['surname']
            phone = request.form['phone']

            if not isbn or not name or not surname or not phone:
                flash("No field should be empty")
                return render_template("rentBook.html", requestsDict=requestsDict)

            book_info = books.find_one({"_id": ObjectId(isbn)})

            if book_info:
                if book_info['avaliability'] == 1:
                    # Create new booking
                    new_booking = {
                        "ISBN": isbn,
                        "name": name,
                        "surname": surname,
                        "phone": phone,
                        "dateOfRent": datetime.now(),
                        "userId": session['userId']  # Assuming the user ID is stored in the session
                    }

                    reservations.insert_one(new_booking)

                    # Update book availability
                    books.update_one({"_id": ObjectId(isbn)}, {"$set": {"avaliability": 0}})

                    flash("Book successfully rented")
                    requestsDict['booking'] = new_booking
                    return render_template("rentBook.html", requestsDict=requestsDict)
                else:
                    flash("Book is not available")
            else:
                flash("Invalid ISBN")

        return render_template('rentBook.html', requestsDict=requestsDict)

    return redirect(url_for('user.login'))


# Endpoint for view user Bookings
@user.route("/viewBookings", methods=["GET", "POST"])
def viewBookings():
    if session.get('loggedIn'):
        requestsDict = {"bookings": [], "visMessage": "hidden", "visError": "hidden", "message": None}

        # Fetch the userId from the session
        userId = session.get('userId', None)

        # Debugging: Print the userId
        print(f"Debug: UserId from session is {userId}")

        if userId is None:
            flash("User ID not found in session")
            return redirect(url_for('user.login'))

        # Fetch bookings for the user
        user_bookings = list(reservations.find({"userId": userId}))

        # Debugging: Print the fetched bookings
        print(f"Debug: User bookings from DB are {user_bookings}")

        if user_bookings:
            for booking in user_bookings:
                book_info = books.find_one({"_id": ObjectId(booking["ISBN"])})
                if book_info:
                    booking['booking_id'] = booking.pop('_id')  # Rename '_id' to 'booking_id'
                    booking.update(book_info)
            requestsDict['bookings'] = user_bookings
        else:
            requestsDict['message'] = "There are no available bookings for this user"
            requestsDict['visMessage'] = "visible"

        return render_template("viewBookings.html", requestsDict=requestsDict)

    return redirect(url_for('user.login'))



@user.route('/returnBook', methods=['GET', 'POST'])
def returnBook():
    print("Debug: Inside returnBook endpoint")  # Debugging line
    if session.get('loggedIn'):
        requestsDict = {"visMessage": "hidden", "visError": "hidden", "message": None}

        if request.method == 'POST':
            print("Debug: POST request received")  # Debugging line
            bookingId = request.form['bookingId']
            print(f"Debug: Booking ID is {bookingId}")  # Debugging line

            if not bookingId:
                flash("Booking ID field should not be empty")
                return render_template("returnBook.html", requestsDict=requestsDict)

            try:
                # Try to find the booking using the ObjectId
                booking_info = reservations.find_one({"_id": ObjectId(bookingId)})

                if booking_info:
                    print("Debug: Booking found")  # Debugging line
                    # Update book availability
                    books.update_one({"_id": ObjectId(booking_info["ISBN"])}, {"$set": {"avaliability": 1}})

                    # Delete the booking
                    reservations.delete_one({"_id": ObjectId(bookingId)})

                    flash("Book successfully returned")
                    return redirect(url_for('user.viewBookings'))
                else:
                    flash("Invalid Booking ID")

            except InvalidId:
                flash("Invalid Booking ID format")

        return render_template('returnBook.html', requestsDict=requestsDict)

    return redirect(url_for('user.login'))


#Endpoint for Deleting User's account
@user.route("/deactivateAccount", methods=["GET", "POST"])
def deactivateAccount():
    requestsDict = {
        "bookings": [],
        "actDeactivation": "active",
        "visMessage": "hidden",
        "visError": "hidden",
        "message": None
    }

    if session.get('loggedIn'):
        if request.method == 'POST':
            if request.form['submit_button'] == "Deactivate account":
                loginField = None
                if 'username' in session:
                    loginField = "username"
                elif 'email' in session:
                    loginField = "email"

                if loginField:
                    users.delete_one({loginField: session[loginField]})
                    session.clear()
                    return redirect(url_for('user.login'))

        return render_template("deactivateAccount.html", requestsDict=requestsDict)

    return redirect(url_for('user.login'))


# #Endpoint to logout a user from the system
@user.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("user.login"))
