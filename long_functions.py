import smtplib,ssl
import random
from flask import flash,session
from passlib.hash import pbkdf2_sha256
import pymongo
import os
from decouple import config


s3 = config('DATABASE_URL')
pass_= config('GMAIL_PASS')
client = pymongo.MongoClient(s3)

def connect():
 mydb = client['mainTask']
 connect.tasks = mydb['users'] 

def reset_email(email):
    gmail_user = 'ah.akra@gmail.com'
    to = email
    gmail_password = pass_
    subject = 'rest password code'
    
    random_number = random.randint(100000,999999)
    session['code']=pbkdf2_sha256.hash(str(random_number))
    subject="reset password"
    message = 'Subject:reset code\n\n'+str(random_number)
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    context = ssl.create_default_context()
    try:
     server = smtplib.SMTP(smtp_server,port)
     server.ehlo() # Can be omitted
     server.starttls(context=context) # Secure the connection
     server.ehlo() # Can be omitted
     server.login(gmail_user, gmail_password)
     server.sendmail(gmail_user, to, message)
     flash("email sent")
    except  Exception as e:
    # Print any error messages to stdout
     print(e)
     print('Something went wrong...')

