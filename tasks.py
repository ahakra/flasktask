from flask import Flask, render_template, url_for, request, redirect, url_for, Blueprint
from logging import log
import datetime
import pymongo
from bson.objectid import ObjectId
#from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from views import app_views
from users import app_users
import os
from decouple import config



app = Flask(__name__)
app.register_blueprint(app_views)
app.register_blueprint(app_users)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = config("SECRET_KEY")




 




if __name__ == "__main__":
    app.run(debug=True)