import pickle
from flask import Flask, jsonify, make_response, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import uuid
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from pymongo import MongoClient


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///../password.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['username'] = os.getenv('username')
app.config['password'] = os.getenv('password')

app.app_context().push()

print(app.config['username'])

client = MongoClient("mongodb+srv://"+app.config['username']+":"+app.config['password']+"@cluster0.c19uj.mongodb.net/?retryWrites=true&w=majority")
db = client.test
    
    
# db = SQLAlchemy(app)

# class users(db.Document):
# #     id = db.Column(db.Integer, primary_key=True)
#     public_id = db.StringField(required=True)
#     name = db.StringField(required=True)
#     email = db.StringField(required=True)
#     password = db.StringField()
#     admin = db.BooleanField(required=True)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message: ': 'token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = User.query.filter_by(public_id=data['public_id']).first()

        except:
            return jsonify({'message: ': 'token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({'message: ': 'cannot perform that function'})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({"users: ": output})

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message: ': 'cannot perform that function'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message: ": "no user found"})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['email'] = user.email
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({"user: ": user_data})

@app.route('/user', methods=['POST'])
# @token_required
def create_user():
    
    data = request.get_json()

    # if not current_user.admin:
    #     return jsonify({'message: ': 'cannot perform that function'})


    name = db.users.count_documents({"name":data['name']})
    
#     name = list(name)
    
#     print(name)

    if name > 0:
        return jsonify({"message: ": "username taken"})

    email = db.users.count_documents({"name":data['email']})

    if email > 0:
        return jsonify({"message: ": "email taken"})


 

    hashed_password = generate_password_hash(data['password'], method='sha256')

    db.users.insert_one({"public_id":str(uuid.uuid4()), "name":data['name'], "email":data['email'], "password":hashed_password, "admin":False})


    return jsonify({'message': 'new user created'})

@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message: ': 'cannot perform that function'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message: ": "no user found"})

    user.admin = True
    db.session.commit()

    return jsonify({"message: ": "the user has been promoted"})

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message: ': 'cannot perform that function'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message: ": "no user found"})

    db.session.delete(user)
    db.session.commit()

    return jsonify({"massage: ": "user has been deleted"})


@app.route('/login')
def login():

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token: ': token})

    return make_response('could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})

# vectorizer = pickle.load(open('svm_models/vectorizer.sav', 'rb'))
# classifier = pickle.load(open('svm_models/classifier.sav', 'rb'))
tree = pickle.load(open('svm_models/tree.pkl', 'rb'))

@app.route('/strength', methods=['GET'])
@token_required
def get(current_user):
    if request.method == 'GET':
        content = request.json
        text = content['text']
        # print(text)
        if text:
            text_vector = [str(text)]
            result = tree.predict(text_vector)
            resultt = result[0]
            resultt = resultt - .01
            resultt = round(resultt, 2)
            resultt = resultt/2
            resultt = resultt *100
            resultt = int(resultt)
            return make_response(jsonify({'strength': resultt, 'text': text, 'status_code':200}), 200)
        return make_response(jsonify({'error':'sorry! unable to parse', 'status_code':500}), 500)



@app.route('/signup')
def home():
   return render_template('signup.html')

@app.route('/docs')
def docs():
   return render_template('docs.html')

if __name__ == '__main__':
   app.run(debug=True)
