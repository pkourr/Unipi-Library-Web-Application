#from pymongo import MongoClient
#from pymongo.errors import DuplicateKeyError
import pymongo
from pymongo import MongoClient
from flask import Flask, request,render_template,flash, jsonify, url_for,redirect, Response, session
import os
#from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt

from admin import admin
from user import user

# Connect to our local MongoDB
client = MongoClient(os.environ.get("MONGO_HOSTNAME","localhost"))

# Choose InfoSys database
db = client['UnipiLibrary']
users=db['Users']
books=db['Books']
reservations=db['Bookings']
admins=db['Admins']


# Initiate Flask App
app = Flask(__name__)
app.secret_key = 'awteflj@#$adf5jiepjgnv2223tg'


#app.permanent_session_lifetime = timedelta(minutes=15)
app.register_blueprint(admin,url_prefix="/admin")
app.register_blueprint(user,url_prefix="/user")



@app.route('/')
def index():
    # admins.insert_one({'email':'nok@gmail.com','password':'asfd21@wrs'})
    return render_template("index.html")


# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
