from flask import Flask, render_template, url_for, request, redirect, url_for, Blueprint,flash, session  
import pymongo
from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo
import re
from passlib.hash import pbkdf2_sha256
import os
from long_functions import reset_email
from decouple import config

app_users = Blueprint('app_users',__name__)

regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
username_regex='\s'

s3 = config('DATABASE_URL')
client = pymongo.MongoClient(s3)

def connect():
 mydb = client['mainTask']
 connect.tasks = mydb['users'] 
     
class MyLogin(FlaskForm):
   
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    
class MyForm(MyLogin):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    retype_password = PasswordField('Retype Password', validators=[DataRequired(),
    EqualTo("password", message='Passwords must match')])
    
class MyChangePassword(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    retype_password = PasswordField('Retype Password', validators=[DataRequired()])

class MyResetPassword(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])   
class MyResetPasswordUsername(MyResetPassword):
   
    code = PasswordField('Code', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    retype_password = PasswordField('Retype Password', validators=[DataRequired()])


@app_users.route('/register', methods=['GET','POST'])
def index():
    form = MyForm()
    session.pop('_flashes', None)
    if request.method == 'POST':    

     if form.validate_on_submit():
         if re.search(regex, form.email.data):
            
            connect()
            name = form.name.data
            email = form.email.data
            username = form.username.data.lower()
            password = form.password.data
            description = form.description.data
            if connect.tasks.find_one({"email":email}) :
               flash("There is account registered with this email")
               return render_template("register.html",form=form)    
            elif  re.search(username_regex,form.username.data):    
              flash("Username syntax error")
              return render_template("register.html",form=form)     
            elif  connect.tasks.find_one({"username":username}):    
              flash("username already taken")
              return render_template("register.html",form=form) 

            else:
             connect.tasks.insert_one({"name":name,"email":email,
             "description":description,"username":username,"password":pbkdf2_sha256.hash(password),
             "role":"user",})
             session['name'] = username
             x = connect.tasks.find_one({"username":username})  
             session['role'] = x['role']
             print(session['role'])
             return redirect("/")
         else:
             flash("invalid email address")
             return render_template("register.html",form=form)   
     elif form.name.data is not None:
         if form.password.data != form.retype_password.data:
          flash("password dont match")
          return render_template("register.html",form=form)
         else:
          return render_template("register.html",form=form)   
                
     else:
           session.pop('_flashes', None)  
           return render_template("register.html",form=form) 
    else:
       # session['name'] = form.name.data
        return render_template("register.html",form=form) 


@app_users.route('/reset', methods=['GET','POST'])
def reset():
    session.pop('_flashes', None)
    form = MyResetPassword()
    
    if request.method == "POST":
        connect()   
        user= form.username.data
        username =  connect.tasks.find_one({"username":user.lower()})
        if connect.tasks.find_one({"username":user.lower()}):
          
          reset_email(username["email"])
          session["username"] = user.lower()
          return redirect("reset_username")
        else:
          flash("There is no account registered with this user: "+str(form.username.data))
          return render_template("reset.html",form=form) 

    return render_template('reset.html',form=form)      

@app_users.route('/reset_username', methods=['GET','POST'])
def reset_username():
    connect()
    form= MyResetPasswordUsername()
    if request.method == "POST":
        if session["username"] == form.username.data:
           if pbkdf2_sha256.verify(str(form.code.data),session["code"]):
             if form.new_password.data == form.retype_password.data:
                 connect.tasks.update_one({"username": form.username.data.lower()},{ "$set" :{"password":pbkdf2_sha256.hash(form.retype_password.data)}})
                 session.clear()
                 session["name"] = form.username.data.lower()
                 x = connect.tasks.find_one({"username":session["name"]})  
                 session['role'] = x['role']
                
                 return redirect("/")
             else:
                 flash("password dont match")
                 return   render_template('reset_username.html',form=form)
           else:
               flash("wrong code")
               return render_template('reset_username.html',form=form)      
        else:
            flash("username doesnt match")
            return render_template('reset_username.html',form=form)       
    return render_template('reset_username.html',form=form)
    




@app_users.route('/login', methods=['GET','POST'])
def login():
    form = MyLogin()
    session.pop('_flashes', None)
    if request.method == 'POST':    
     if form.validate_on_submit():
            connect()
            username = form.username.data
            password = form.password.data
            if  connect.tasks.find_one({"username":username.lower()}):
             x = connect.tasks.find_one({"username":username.lower()})  

             if pbkdf2_sha256.verify(password,x['password']):
                 session['name'] =  username
                 session['role'] = x['role']
                 print(session['role'])
                 return redirect("/")
             else:    
               flash("wrong combination")
               return render_template("login.html",form=form)   
            else:
               flash("wrong combination")
               return render_template("login.html",form=form) 
     else:
           session.pop('_flashes', None)  
           return render_template("login.html",form=form) 
    return render_template("login.html",form=form) 
@app_users.route('/logout', methods=['GET','POST'])
def logout():
     session['name'] = None
     session.clear()
     return redirect("/")

@app_users.route('/profile/<string:username>',methods=['GET','POST'])
def profile(username):
    if session and session['name'] == username :
     connect()
     info = connect.tasks.find_one({"username":username})
     return render_template('profile.html',info=info)
    else:
       return("you are not authorized") 
@app_users.route('/change_password',methods=['GET','POST'])
def change_password():
   session.pop('_flashes', None)
   form = MyChangePassword()
  
   if  request.method == 'POST':     
        connect()
        username = form.username.data
        old_password = form.old_password.data
           
        if  connect.tasks.find_one({"username":username}):
               x = connect.tasks.find_one({"username":username})
               
               if pbkdf2_sha256.verify(old_password,x['password']):
                   if form.new_password.data != form.retype_password.data:
                     flash("password dont match")
                     return render_template("change_password.html",form=form)    
                   else:
                     new_password = form.new_password.data  
                     connect.tasks.update_one({"username": username},{ "$set" :{"password":pbkdf2_sha256.hash(new_password)}})
                     flash("password changed")
                     return render_template("profile.html",info=x)
               else:
                flash("wrong combination")
                return render_template("change_password.html",form=form) 
        else:
                 flash("wrong combination/user")
                 return render_template("change_password.html",form=form)  
   else:
            
             return render_template('change_password.html',form=form)
