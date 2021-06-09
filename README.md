# flasktask
This was a test app for building a flask application using mongodb.
<br>
*Database used*: mongodb<br>
*Email server*: gmail account<br>
*Link to setup gmail for app*: https://support.google.com/accounts/answer/3466521/manage-third-party-apps-amp-services-with-access-to-your-account?hl=en <br>
<br>
**Short description about app:**<br>
The home page include a main tasks list.<br>
Each task can have several subtasks.<br>
Each subtask can be assigned to a user.<br>
Each subtask has a status done, in progress, or blank(null). <br>


Admin script to intialize admin account<br>
Each User can register.<br>
Using gmail smtp to send reset email.<br>



**To install requirments.**<br>
```
pip install -r requirments.txt<br>
```
**First you should create .env file with the following variables.**<br>
```
DATABASE_URL=<link to mongodb>
GMAIL_PASS=<Gmail password for gmail app>
SECRET_KEY=<anyKey-You_want>
```
**To run app:**<br>
```
python tasks.py
```
