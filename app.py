import subprocess
from flask import Flask, render_template,request,redirect
import threading
import pymongo
import time
from pymongo.mongo_client import MongoClient
from flask_socketio import SocketIO, emit
app=Flask(__name__)
running_process = None
uri = "mongodb+srv://dhruvbhargav2001:qbR74yh4NzZENHsF@student.hx5tx4b.mongodb.net/?retryWrites=true&w=majority&appName=Student"
# Create a new client and connect to the server
client = MongoClient(uri)
db=client.Major_project    
client.server_info()
app = Flask(__name__) 
@app.route('/')
def home():
    return render_template('home_page.html')
@app.route('/signup',methods=['GET','POST'])
def create():
    return render_template('new.html')
@app.route('/new_user_create',methods=['GET','POST'])
def new_user_create():
    user={"email": request.form["email"],"name": request.form["name"],"password": request.form["password"],"role":request.form["role"]}
    if request.form["role"]=="Student":
        db.Student.insert_one(user)
    elif request.form["role"]=="Teacher":
        db.Teacher.insert_one(user)
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
    if data is not None:
        if str(name)==str(data['name']) and str(password)==str(data['password']):
            return render_template('test_verification.html',name=name)
        else:
            return render_template('login.html')
    else:
        return redirect("/create_test")

@app.route('/create_test')
def create_test():
    return render_template("create_test.html")

@app.route('/add_test',methods=['GET','POST'])
def add_test():
    if request.method == 'POST':
        test={}
        list=[]
        test_id= request.form.get('test_id')
        i=0
        questions=[]
        while request.form.get(f"questions[{i}]"):
            dict={}
            options={}
            for j in range (4):
                options[f"o{j}"]=request.form.get(f"questions[{i}][{j}]")
            dict["qid"]=i
            dict["q"]=request.form.get(f"questions[{i}]")
            dict["options"]=options
            dict["answer"]=request.form.get(f"questions[{i}]answer")
            questions.append(dict)
            i+=1
        data={
        "test_id":int(test_id),
        "questions":questions
        }
        db.Test.insert_one(data)
        return redirect("/")

@app.route('/details',methods=['GET','POST'])
def details():
    return render_template('details.html',test_id=request.form.get("testid"))
@app.route('/start',methods=['GET','POST'])
def give_test():
    test_id=int(request.form.get("test_id"))
    data = db.Test.find_one({"test_id":test_id})
    questions = data["questions"]
    dict={
        "testid":test_id,
        "laptop":0,
        "cell_phone": 0,
        "book": 0,
        "tv":0,
        "person":1
    }
    if db.Live_Test.find_one({"testid":test_id}):
        pass
    else:
        db.Live_Test.insert_one(dict)
    global running_process
    if running_process is None:
        # Start the Python script
        running_process = subprocess.Popen(['python', 'online_proctoring_system.py',str(test_id)])
        time.sleep(60)
        return render_template('test.html',questions=questions,test_id=test_id)


@app.route('/check',methods=['GET','POST'])
def check_result():
    global running_process
    if running_process:
        # Terminate the Python script
        running_process.terminate()
        running_process = None
    score=0
    test_id=int(request.form.get("test_id"))
    data=db.Test.find_one({"test_id":test_id})
    db.Live_Test.delete_one({"testid": test_id})
    questions=data["questions"]
    for question in questions:
        if question['answer']==request.form.get(str(question['qid'])):
            score+=1
    return render_template('result.html',score=score)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
