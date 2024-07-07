from pymongo import MongoClient
from flask import Flask, request,render_template,flash, url_for,redirect, session,Blueprint, render_template
from datetime import datetime
import re
import time
import os
from bson import ObjectId

admin=Blueprint("admin",__name__,template_folder='templates')

# Connect to our local MongoDB
client = MongoClient(os.environ.get("MONGO_HOSTNAME","localhost"))

# Access databases and useful collections
db = client['UnipiLibrary']
books=db['Books']
reservations=db['Bookings']
admins=db['Admins']

#Endpoint to login an existing user
@admin.route("/loginAdmin",methods=(['POST','GET']))
def loginAdmin():
    #session.clear()
    session['emailAdm']=None
    session['loggedInAdm']=False
    session['passwordAdm']=None

    requestsDict={"visMessage":"hidden","visError":"hidden","message":None,"activeChangePass":"active"}

    #Initialize first administrator of the system
    if not admins.find_one({"email":"nok@gmail.com"}):
        admins.insert_one({"email":"nok@gmail.com", "password":"asfd21@wrs"})

    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']

        #Validation check about request's data
        if not email or not password:
            flash("No field should be empty")
            requestsDict['visError']='visible'
            return render_template('loginAdmin.html', requestsDict=requestsDict)

        if admins.find_one({"email":email,"otp":password}) is not None:
            session['emailAdm']=email
            session['loggedInAdm']=True
            session['passwordAdm']=password
            return redirect(url_for('admin.changePassword'))

        elif admins.find_one({"email":email,"password":password}) is not None:
            session['emailAdm']=email
            session['loggedInAdm']=True
            session['passwordAdm']=password
            return redirect(url_for('admin.insertBook'))
        else:
            flash("Incorrect email or password")
            requestsDict['visError']='visible'
            return render_template("loginAdmin.html",requestsDict=requestsDict)

    return render_template("loginAdmin.html",requestsDict=requestsDict)

#Endpoint to insert new book to the system
@admin.route("/insertBook",methods=(['POST','GET']))
def insertBook():
    if session.get('loggedInAdm'):
        requestsDict={"visMessage":"hidden","visError":"hidden","message":None,"activeInsert":"active"}

        if request.method=="POST":
            date=request.form['date']
            title=request.form['title']
            author=request.form['author']
            pages=request.form['pages']
            abstract=request.form['abstract']
            rentdays=request.form['rentdays']

            if not date or not title or not author or not pages:
                flash("No field should be empty")
                requestsDict['visError']='visible'
                return render_template('insertBook.html',requestsDict=requestsDict)

            dateFormat = "%d/%m/%Y"
            timeFormat='%H:%M'
            dateStr=None

            #Change way all date time
            try:
                dateStr=datetime.strptime(date, dateFormat)
            except ValueError:
                flash("The date field should be in the format: dd/mm/yyyy")
                requestsDict['visError']='visible'
                return render_template("insertBook.html",requestsDict=requestsDict)


            if books.find_one({"title":title}) is not None:
                requestsDict['message']="Book already exists"
                requestsDict['visMessage']='visible'
                return render_template("insertBook.html",requestsDict=requestsDict)

            books.insert_one({"date":dateStr,"title":title,"author":author,\
                "pages":pages,"avaliability":1, "abstract":abstract, "rentdays":rentdays})
            requestsDict['message']='Book successfully inserted'
            requestsDict['visMessage']='visible'
            return render_template("insertBook.html",requestsDict=requestsDict)

        return render_template("insertBook.html",requestsDict=requestsDict)
    return redirect(url_for("admin.loginAdmin"))


# Endpoint to delete an existing book from the system
@admin.route("/deleteBook", methods=(['POST', 'GET']))
def deleteBook():
    if session.get('loggedInAdm'):
        requestsDict = {"visMessage": "hidden", "visError": "hidden", "message": None, "activeDelete": "active"}

        if request.method == "POST":
            bookId = request.form['bookId']

            if not bookId:
                flash("No field should be empty")
                requestsDict['visError'] = 'visible'
                return render_template("deleteBook.html", requestsDict=requestsDict)

            # Convert bookId to ObjectId and then search
            if books.find_one({"_id": ObjectId(bookId)}) is None:
                flash("Invalid Book's id")
                requestsDict['visError'] = 'visible'
                return render_template("deleteBook.html", requestsDict=requestsDict)

            books.delete_one({"_id": ObjectId(bookId)})
            requestsDict['message'] = "Book successfully deleted"
            requestsDict['visMessage'] = 'visible'
            return render_template("deleteBook.html", requestsDict=requestsDict)

        return render_template("deleteBook.html", requestsDict=requestsDict)

    return redirect(url_for("admin.loginAdmin"))

#Endpoint for an admin searching books
@admin.route('/adminSearchBook', methods=['GET', 'POST'])
def adminSearchBook():
    session.pop('_flashes', None)
    if session.get('loggedInAdm'):  # Assuming role-based session
        requestsDict = {"books": [], "actSearch": "active", "visMessage": None, "visError": None, "message": None}
        fields_to_return = {"_id": 1, "date": 1, "title": 1, "author": 1, "pages": 1, "avaliability": 1}

        if request.method == 'POST':
            if "get_all_books" in request.form:
                # Retrieve all books from the database
                booksData = list(books.find({}, fields_to_return))
                requestsDict['books'] = booksData
                return render_template('adminSearchBook.html', requestsDict=requestsDict)

            title = request.form.get('title', None)
            author = request.form.get('author', None)
            isbn = request.form.get('_id', None)

            query = {}

            if isbn:
                query["_id"] = ObjectId(isbn)
                fields_to_return.update({"abstract": 1, "rentdays": 1})

            if title:
                query["title"] = {"$regex": f"^{title}$", "$options": 'i'}

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

        return render_template('adminSearchBook.html', requestsDict=requestsDict)

    return redirect(url_for('admin.loginAdmin'))
# #Endpoint to logout an administrator from the system
@admin.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.loginAdmin"))