from flask import Flask, request, jsonify
import json
import sqlite3
from peeweeDB import User, Notes, AuthToken
import bcrypt
from hashlib import sha256

app = Flask(__name__)
salt = bcrypt.gensalt()


notes = [
]


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('notes.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn


def password_hashing(thePassword):
    hashed_password = sha256(thePassword.encode('utf-8')).hexdigest()
    return hashed_password


@app.route('/')
def index():
    return 'hello world'


@app.route('/users', methods=['GET', 'POST'])
def userFunction():
    # conn = db_connection()
    # cursor = conn.cursor()

    if request.method == 'GET':
        # cursor = conn.execute("SELECT * FROM users")
        users_info = []
        for user in User.select():
            users_info.append({"id": user.id, "email": user.email})
        if len(users_info):
            return jsonify(users_info)

    if request.method == 'POST':
        users_email = []
        for user in User.select():
            users_email.append(user.email)
        email = request.form['email']
        password = request.form['password']
        if email in users_email:
            return "Email should be unique. You have signed up with this email previously!!!"
        User.create(email=email, password=password_hashing(password))
        return f"User created successfully", 201


@app.route('/login', methods=['POST'])
def loginView():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        thisUser = User.get(User.email==f"{email}")
        if thisUser.password == password_hashing(password):
            token = password_hashing(f"{email}-{thisUser.password}")
            if AuthToken.get(user=thisUser.id):
                return jsonify({'token': token})
            else:
                AuthToken.create(user=thisUser.id, token=token)
                return jsonify({"token": token})
        else:
            return "Password doesn't match"


def isAuthenticated(token):
    authToken = AuthToken.get(token=token)
    return {"id": authToken.user, "authenticated": True}


@app.route('/notes', methods=['GET', 'POST'])
def notesFun():
    if request.method == 'GET':
        notes_info = []
        for note in Notes.select():
            notes_info.append({"id": note.id, "author": note.author, "title": note.title, "description": note.content,})
        if notes_info is not None:
            return jsonify(note)

    if request.method == 'POST':
        token = request.form['token']
        authCheck = isAuthenticated(token)
        if authCheck['authenticated']:
            title = request.form['title']
            description = request.form['description']
            newNote = Notes.create(author=authCheck['id'], title=title, content=description)
            return f"book with the id: {newNote.id} created successfully", 201


@app.route('/update_note/', methods=['PUT', 'POST'])
def noteUpdate():
    if request.method == 'PUT':
        token = request.form['token']
        authCheck = isAuthenticated(token)
        note_id = request.form['id']
        if authCheck['authenticated']:
            newNote = Notes.get(id=note_id)
            if request.form['description']:
                newNote.content = request.form['description']
            newNote.save()
            return f"book with the id: {newNote.id} created successfully", 201


@app.route('/delete_note/', methods=['DELETE'])
def noteDelete():
    if request.method == 'DELETE':
        token = request.form['token']
        authCheck = isAuthenticated(token)
        note_id = request.form['id']
        if authCheck['authenticated']:
            newNote = Notes.get(id=note_id)
            newNote.delete_instance()
            return f"Note has been deleted!!!", 201


if __name__ == "__main__":
    app.run()
