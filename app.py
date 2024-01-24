import subprocess
from flask import Flask, render_template,request,redirect
import threading
import pymongo
import time
from flask_socketio import SocketIO, emit
app=Flask(__name__)
running_process = None
mongo=pymongo.MongoClient(host="localhost",port=27017,serverSelectionTimeoutMS=1000) #connecting to mongo server
db=mongo.Major_Project    
mongo.server_info()
app = Flask(__name__) 
@app.route('/')
def home():
    return render_template('home_page.html')
@app.route('/signup',methods=['GET','POST'])
def create():
    return render_template('new.html')
@app.route('/new_user_create',methods=['GET','POST'])
def new_user_create():
    user={"email": request.form["email"],"name": request.form["name"],"password": request.form["password"]}
    db.Student.insert_one(user)
    return render_template('home_page.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/test_verification',methods=['GET','POST'])
def test_verification():
    email=request.form.get('email')
    name=request.form.get('name')
    password=request.form.get('password')
    data=db.Student.find_one({'email': email})
    if str(name)==str(data['name']) and str(password)==str(data['password']):
        return render_template('test_verification.html',name=name)
    else:
        return render_template('login.html')
@app.route('/details',methods=['GET','POST'])
def details():
    return render_template('details.html')
@app.route('/start',methods=['GET','POST'])
def give_test():
    data = db.Test.find_one({"test_id": 1})
    questions = data["questions"]
    global running_process
    if running_process is None:
        # Start the Python script
        running_process = subprocess.Popen(['python', 'online_proctoring_system.py'])
        time.sleep(30)
        return render_template('test.html', questions=questions)

@app.route('/check',methods=['GET','POST'])
def check_result():
    global running_process
    if running_process:
        # Terminate the Python script
        running_process.terminate()
        running_process = None
    score=0
    data=db.Test.find_one({"test_id":1})
    questions=data["questions"]
    for question in questions:
        if question['answer']==request.form.get(str(question['qid'])):
            score+=1
    return render_template('result.html',score=score)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
