from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re #check for valid email
import md5 #use md5 hashing

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') #email format
NAME_REGEX= re.compile(r'[a-zA-Z]') #name format

app = Flask(__name__)
mysql = MySQLConnector(app, 'wall')
app.secret_key="ThisisSecret!"

@app.route('/', methods=['GET'])
def index():
    if 'user_id' in session and 'first_name' in session:
        return redirect('/wall')
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    email=request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    user_query= "SELECT * FROM users WHERE users.email= :email AND users.password=:password"
    query_data={'email':email, 'password':password}
    user= mysql.query_db(user_query,query_data)
    if user:
        # id_query= "SELECT users.id FROM users WHERE users.email= :email AND users.password=:password"
        # id_data={'email':email, 'password':password}
        # user_id=mysql.query_db(id_query,id_data)
        session['user_id']=int(user[0]['id'])
        return redirect('/wall')
    else:
        flash(u"User email or password invalid","login")
    return redirect('/')

@app.route('/register', methods=['POST'])
def namevalid():
    if len(request.form['first_name'] or request.form['last_name'])<2:
        flash(u"Name must be at least 2 characters long","registration")
    if len(request.form['email'])<1:
        flash(u"Email cannot be blank!","registration")
    if len(request.form['password'])<8:
        flash(u"Password must be at least 8 characters long","registration")
    if request.form['confirm_password']==request.form['password']:
        flash(u"Password does not match","registration")
    if not NAME_REGEX.match(request.form['first_name'] or request.form['last_name']):
        flash(u"Name must be letters only","registration")
    if not EMAIL_REGEX.match(request.form['email']):
        flash(u"Invalid Email Address!","registration")
    else:
        first_name= request.form['first_name']
        last_name= request.form['last_name']
        email= request.form['email']
        password= md5.new(request.form['password']).hexdigest()
        insert_query="INSERT INTO users(first_name,last_name,email,password,created_at,updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        query_data={'first_name':first_name,'last_name':last_name, 'email':email, 'password':password}
        mysql.query_db(insert_query,query_data)
        return redirect('/wall')
    return redirect('/')

@app.route('/wall')
def userwall():
    msg_query="SELECT messages.id, messages.message, DATE_FORMAT(messages.created_at,'%b %d %Y'), users.id, users.first_name, users.last_name FROM messages JOIN users ON messages.user_id=users.id order BY DATE_FORMAT(messages.created_at,'%b %d %Y') DESC"
    messages=mysql.query_db(msg_query)

    comment_query="SELECT comments.id, comments.comment, DATE_FORMAT(comments.created_at,'%b %d %Y'), users.id, users.first_name, users.last_name FROM comments JOIN users ON comments.user_id=users.id order BY DATE_FORMAT(comments.created_at,'%b %d %Y') DESC"
    comments=mysql.query_db(comment_query)
    session['message_id']=int(messages[0]['id'])

    return render_template('wall.html', all_messages=messages, all_comments=comments)

@app.route('/message', methods=['POST'])
def addmessage():
    addmsg_query="INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id,:message,NOW(),NOW())"
    addmsg_data={'user_id':session['user_id'],'message':request.form['message']}
    mysql.query_db(addmsg_query,addmsg_data)
    return redirect('/wall')

@app.route('/comment', methods=['POST'])
def addcomment():
    addcomment_query="INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES (:user_id,:message_id,:comment,NOW(),NOW())"
    addcomment_data={'user_id':session['user_id'],'message_id':session['message_id'],'comment':request.form['comment']}
    mysql.query_db(addcomment_query,addcomment_data)
    return redirect('/wall')

app.run(debug=True)
