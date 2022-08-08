import flask
from flask import Flask, jsonify, request, make_response, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
from email.message import EmailMessage
import smtplib
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

import datetime
from functools import wraps
import static
CLIENT_SECRET_FILE='client_secret.json'
API_NAME='gmail'
API_VERSION='v1'
SCOPES=['https://mail.google.com/']
# service=Create_Services(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
app = Flask(__name__)
CORS(app)

app.secret_key = "123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
  return {
    'raw': raw_message.decode("utf-8")
  }
def send_message(service, user_id, message):
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    print('Message Id: %s' % message['id'])
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None


class users(db.Model):
    username = db.Column(db.Text,
                         primary_key=True,
                         unique=True,
                         nullable=False)
    password = db.Column(db.Text, nullable=False)



SENDER = "palash.tiwari00718@gmail.com"
PASSWORD ="batman123@"

def send_email(recipient, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = recipient
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(SENDER, PASSWORD)
    server.send_message(msg)
    server.quit()



class deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer)
    lr = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)


class card(db.Model):
    did = db.Column(db.Integer, nullable=False)
    cid = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)

@cross_origin()
def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
      token = None

      if request.args['token']:
          token = request.args['token']

      if not token:
          return jsonify({'message' : 'Token is missing!'}), 401

      try: 
          data = jwt.decode(token, app.config['SECRET_KEY'],"HS256")
          global USER_ID
          USER_ID=data['user']
      except:
          return jsonify({'message' : 'Token is invalid!'}), 401

      return f( *args, **kwargs)

  return decorated

def check_token(a):
  
  try:
    data =jwt.decode(a,app.config['SECRET_KEY'],"HS256")
  except:
    return False
  user=users.query.filter_by(username=data['user']).first()  
    
 
  if(user):
    
    
    return user.username
  else:
    return False

# @app.route('/unprotected/str:token')
# def unprotected(token):
#   if(check_token(token)):
    
#     return check_token(token)
#   else:
#     return 'please login'


@app.route('/protected/<string:token>', methods=["GET", "POST"])
@cross_origin()

def protected(token):
  if(check_token(token)):
    
    return jsonify({'username':check_token(token)})
  else:
    return False


@app.route('/dashboard/<string:token>', methods=["GET", "POST"])
@cross_origin()

def dashboard(token):
  if(check_token(token)):
    u=check_token(token)
    print(u)
    if request.method=="GET":
      
    
      return check_token(token)
    elif request.method=="POST":
      data=request.get_json(force=True)
      
      name = data["name"]
      des=data['des']
      stmt = deck(name=name,description=des,user=u)
      db.session.add(stmt)
      db.session.commit()
      return "ok",200
      
@app.route('/decks/<string:token>/<int:i>', methods=["GET", "POST","DELETE"])
@cross_origin()
def edit_deck(token,i):
  if(check_token(token)):
    if request.method=="POST":
      data=request.get_json(force=True)
        
      f = data["front"]
      b =data['back']
      stmt = card(front=f,back=b,did=i)
      db.session.add(stmt)
      db.session.commit()
      return "ok",200
      
    else:
      ob=deck.query.filter_by(id=i).first()
      ob1=card.query.filter_by(did=i).delete()

      db.session.delete(ob)
      db.session.commit()
      return "ok"
@app.route('/decks/<string:token>', methods=["GET", "POST"])
@cross_origin()
def get_deck(token):
  if(check_token(token)):
    if request.method=="GET":
      l=[]
      u=check_token(token)
      print(u)
      decks = deck.query.filter_by(user=u)
      for d in decks:
        l1=[]
        l1.append(d.score)
        l1.append(d.lr)
        l1.append(d.name)
        l1.append(d.description)
        l1.append(d.id)
        l.append(l1)
        
        
      
     
      return jsonify({'deck':l})
  else:
    return 'please login',302    

@app.route('/login', methods=["GET", "POST"])
@cross_origin()
def login():

    if request.method == "POST":
        data=request.get_json(force=True)
        print(data)
        user = data['user']

        Password = data["pass"]
        if users.query.filter_by(username=user, password=Password).first():

            token = jwt.encode(
                {
                    "user":
                    user,
                    'exp':
                    datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                app.secret_key,
                algorithm="HS256")

            ##resp.headers["Access-Control-Allow-Credentials"] = True
            ##resp=make_response(jsonify({'token':token}))
            ##resp.set_cookie('token',token)
          
            return jsonify({'token':token})

        else:
            return "Username or Password Incorrect",302
            
    else:
        return render_template("login.html")

    if request.method=="GET":
      return "hello"
      
@app.route("/signup", methods=["POST", "GET"])
@cross_origin()
def signup():
    if request.method == "POST":
        data=request.get_json(force=True)
        
        user = data["user"]
        Password =data['pass']
        

        if ((len(user) != 0 and len(Password) != 0)):
            if users.query.filter_by(username=user).first():

                
                return "Name already taken",302
            else:
                stmt = users(username=user, password=Password)
                db.session.add(stmt)
                db.session.commit()
                return "ok",200
        else:
            flash("(recheck username/password)")
            return redirect(url_for("signup"))


    else:

        return render_template("signup.html")
@app.route('/review/<string:token>/<string:d>', methods=["GET", "POST"])
def get_review(token,d):
  if(check_token(token)):
    if request.method=="GET":
      l=[]
      print("f running")
      cards = card.query.filter_by(did=d)
      for c in cards:
        l1=[]
        l1.append(c.front)
        l1.append(c.back)
        l.append(l1)
        
        
      
     
      return jsonify({'card':l})
    else:
      data=request.get_json(force=True)
      score=data['score']
      x=deck.query.filter_by(id=d).first()
      x.score=score
      now = datetime.datetime.utcnow()
      x.lr=now

      db.session.commit()
      return 'Success',200
      
  else:
    return 'please login',302
    





@app.route("/", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        print("bikaji bhujiya moment")
        return "test"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
