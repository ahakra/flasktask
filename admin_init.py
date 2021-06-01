
import pymongo
from decouple import config
import os
import getpass
from passlib.hash import pbkdf2_sha256

s3 = config('DATABASE_URL')
client = pymongo.MongoClient(s3)

def connect():
 mydb = client['mainTask']
 connect.tasks = mydb['users'] 
    

print("Creating Admin user")
name = input("Enter you name: ")
email = input("Enter admin email address: ")
description = input("Enter description: ")
password = getpass.getpass("enter admin password: ")
retype_password = getpass.getpass("retype password: ")

connect()
if connect.tasks.find_one({"username":"admin"}) :
    print("Admin user was created before")
    
elif connect.tasks.find_one({"email":email}) :
       print("There is account registered with this email")
       
elif password != retype_password :
         print("passwords don't match")
else  :
           connect.tasks.insert_one({"name":name,"email":email,
             "description":description,"username":"admin","password":pbkdf2_sha256.hash(password),
             "role":"admin",})
           print("Admin user is created")  

    

