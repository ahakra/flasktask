from flask import Flask, render_template, url_for, request, redirect, url_for, Blueprint,flash
from flask.globals import session
import pymongo
from bson.objectid import ObjectId
import datetime
from decouple import config

import os

s3 = config('DATABASE_URL')

app_views = Blueprint('app_views',__name__)



client = pymongo.MongoClient(s3)

def connect(collection):
 mydb = client['mainTask']
 connect.tasks = mydb[collection] 



@app_views.route('/', methods=['GET','POST'])
def index():
 connect("task") 
 
 if request.method == 'POST':
      task = request.form.get('main_task')
      user= request.form.get('user')
      my_task = {"task":task , "date_ins":datetime.datetime.now()}
     
      connect.tasks.insert_one(my_task)
     
      return redirect('/')
    
 else:
      connect("task")  
      retrieve_tasks = connect.tasks.find({}).sort("date_ins",-1)
      
      return render_template('index.html',retrieved_tasks = retrieve_tasks)

@app_views.route('/delete/<string:id>')
def delete(id):
 if session and session["name"] and session['role'] == "admin":   
  connect("task")    
  myquery = { "_id": ObjectId(id) }
  connect.tasks.delete_one(myquery)

  connect("sub_task")    
  myquery = { "parent_ID": ObjectId(id) }
  connect.tasks.delete_many(myquery)
  return redirect('/') 
 else:
      return  "you must be admin to delete task"



@app_views.route('/update/<string:id>',methods=['GET','POST'])
def update(id):
     if session and session["name"]:
      connect("task")  
      retrieved_task = connect.tasks.find_one({"_id": ObjectId(id)})
      if request.method == 'POST':
          content = request.form.get("main_task")
          connect.tasks.update_one({"_id": ObjectId(id)},{ "$set" :{"task":content}})
          return redirect('/')
      else:
          return render_template('update.html',retrieved_task=retrieved_task)
     else:
      return  "you must be loggedin to update task"

@app_views.route('/subtask/<string:id>',methods=['GET','POST'])
def details(id):
  if session and session["name"]:  
   connect("sub_task")
   retrieved_subtask = connect.tasks.find({"parent_ID": ObjectId(id)})
   connect("task")
   retrieved_task = connect.tasks.find_one({"_id": ObjectId(id)})
   connect("users")
   users = connect.tasks.find({})
   if request.method == 'POST':
           connect("sub_task")  
           task = request.form.get('main_task')
           user = request.form.get('user')
           my_task = {"parent_ID":ObjectId(id),"task":task , "date_ins":datetime.datetime.now(),"assigned_to":user}
           connect.tasks.insert_one(my_task)
           redirect_url = "/subtask/"+id
           
           return redirect(redirect_url)

   else:
     return render_template('subtask.html',users=users,retrieved_subtask=retrieved_subtask, retrieved_task=retrieved_task)
  else:
     return  "you must be loggedin to view details"
@app_views.route('/delete_sub/<string:id>')
def delete_sub(id):
  connect("sub_task")    
  myquery = { "_id": ObjectId(id) }
  x = connect.tasks.find_one(myquery)
  parent_ID = x['parent_ID']
  connect.tasks.delete_one(myquery)
 
  connect("sub_task")
  retrieved_subtask = connect.tasks.find({"parent_ID": ObjectId(parent_ID)})
  connect("task")
  retrieved_task = connect.tasks.find_one({"_id": ObjectId(parent_ID)})
  connect("users")
  users = connect.tasks.find({})
  return render_template('subtask.html',users=users,retrieved_subtask=retrieved_subtask, retrieved_task=retrieved_task)




@app_views.route('/update_sub/<string:id>',methods=['GET','POST'])
def update_sub(id):
     connect("sub_task")  
     retrieved_task = connect.tasks.find_one({"_id": ObjectId(id)})
     connect("users")
     users = connect.tasks.find({})
     if request.method == 'POST':
          connect("sub_task")  
          content = request.form.get("main_task")
          connect.tasks.update_one({"_id": ObjectId(id)},{ "$set" :{"task":content,"assigned_to":request.form.get("user"),"status":request.form.get("status")}})
          connect("sub_task")
          myquery = { "_id": ObjectId(id) }
          x = connect.tasks.find_one(myquery)
          parent_ID = x['parent_ID']
          retrieved_subtask = connect.tasks.find({"parent_ID": ObjectId(parent_ID)})
          connect("task")
          retrieved_task = connect.tasks.find_one({"_id": ObjectId(parent_ID)})
          connect("users")
          users = connect.tasks.find({})
          return render_template('subtask.html',users=users,retrieved_subtask=retrieved_subtask, retrieved_task=retrieved_task)



     else:
          return render_template('update_sub.html',retrieved_task=retrieved_task,users=users)

@app_views.route("/view_tasks/<string:username>")
def view_tasks(username):
   if session and session['name'] == username :  
     connect("sub_task")
     retrieved_subtask = list(connect.tasks.find({"assigned_to": username}))
     connect("task")
     retrieve_tasks = list(connect.tasks.find({}).sort("date_ins",-1))
     return render_template("view_assigned_tasks.html",retrieved_subtask=retrieved_subtask,retrieved_task=retrieve_tasks)
   else:
        return("you are not authorized")
@app_views.route("/dashboard")
def dashboard():
     connect("sub_task")
     sub_task = list(connect.tasks.find({}))
     connect("task")
     main_task = list(connect.tasks.find({}).sort("date_ins",-1))
     return render_template("dashboard.html",sub_task=sub_task,main_task=main_task)
