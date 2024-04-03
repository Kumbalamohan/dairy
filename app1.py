                                #Diary Management
''' installing all the packages that are needed to our project'''
from flask import Flask,redirect,render_template,request,url_for,session,flash,send_file
from flask_session import Session 
from flask_mysqldb import MySQL
from io import BytesIO      # the files in the form of bytes
import io
from itsdangerous import URLSafeTimedSerializer
#from tokenreset import token1
from stoken import token
from cmail import sendmail
from key import secret_key,salt1,salt2
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer


import random
app=Flask(__name__)
app.secret_key = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'adimin'
app.config['MYSQL_DB'] = 'dairy'
Session(app)
mysql = MySQL(app)
@app.route('/') 
def index():
    return render_template('index.html')
@app.route('/registration', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
       
        name = request.form['name']
        
        password = request.form['password']
        email = request.form['email']
        
        
        cursor = mysql.connection.cursor()
       
        cursor.execute ('select email from students')
        edata = cursor.fetchall()
          
        if (email,)in edata:
            flash('email already exits')                                                                                                                                                                                                                                                                                                                                                                                                                                                         
            return render_template('register.html')
        cursor.close()
        data={'username':name,'password':password,'email':email}
        subject='Email Confirmation'
        body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('confirm',token=token(data,salt1),_external=True)}"
        sendmail(to=email,subject=subject,body=body)
        flash('confirmation link sent to mail')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/confirm/<token>')
def confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt1,max_age=180)
    except Exception as e:
        return 'Link Expired register again'
    else:
        cursor=mysql.connection.cursor()
        username=data['email']
        cursor.execute('select count(*) from students where email=%s',[username])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('login'))
        else:
            cursor.execute('insert into students values(%s,%s,%s)',[data['email'],data['username'],data['password']])
            mysql.connection.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('login'))
@app.route('/login',methods =['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        rollno = request.form['id']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('select count(*) from students where email=%s and password=%s',[rollno,password])#if the count is 0 then either username or password is wrong or if it is 1 then it is login successfully
        count = cursor.fetchone()[0]
        if count == 0:
            flash('Invalid username or password')
            return render_template('login.html')
        else:
            session['user'] = rollno
            return redirect(url_for('home'))
    return render_template('login.html')
@app.route('/studenthome')
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        flash('login first')#implemente flash
        return redirect(url_for('login'))   
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        flash('Successfully logged out')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
@app.route('/noteshome')
def notehome():
    if session.get('user'):
        rollno = session.get('user')
        cursor = mysql.connection.cursor()
        cursor.execute('select * from diary where email = %s',[rollno])
        notes_data=cursor.fetchall()
       
        cursor.close()
        return render_template('addnotetable.html',data = notes_data)
    else:
        return redirect(url_for('login'))
@app.route('/addnotes',methods = ['GET','POST'])
def addnote():
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            rollno=session.get('user')
            cursor.execute('insert into diary(email,title,content) values (%s,%s,%s)',[rollno,title,content])
            mysql.connection.commit()
            cursor.close()
            flash(f'{title} added successfully')
            return redirect (url_for('notehome'))
            
            
        return render_template('notes.html')
    else:
        return redirect(url_for('login'))
@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    cursor=mysql.connection.cursor()
    cursor.execute('select title,content from diary where nid=%s',[nid])
    data=cursor.fetchone()#to fetch single row
    return render_template('notesview.html',data=data)
@app.route('/updatenotes/<nid>',methods=['GET','POST'])
def updatenotes(nid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select title,content from diary where nid=%s',[nid])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            cursor.execute('update diary set title=%s,content=%s where nid=%s',[title,content,nid])
            mysql.connection.commit()
            cursor.close()
            flash('Diary updated successfully')
            return redirect(url_for('notehome'))
        return render_template('updatenote.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/deteletnotes/<nid>')
def deletenotes(nid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from diary where nid=%s',[nid])
    mysql.connection.commit()
    cursor.close()
    flash('notes deleted successfully')
    return redirect(url_for('notehome'))

@app.route('/forget',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        email=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from students where email=%s',[email])
        count=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            
            subject='Forget Password'
            confirm_link=url_for('reset',token=token(email,salt=salt2),_external=True)
            body=f"Use this link to reset your password-\n\n{confirm_link}"
            sendmail(to=email,body=body,subject=subject)
            flash('Reset link sent check your email')
            return redirect(url_for('login'))
        else:
            flash('Invalid email id')
            return render_template('forgot.html')
    return render_template('forgot.html')
@app.route('/reset/<token>',methods=['GET','POST'])
def reset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        email=serializer.loads(token,salt=salt2,max_age=180)
    except:
        abort(404,'Link Expired')
    else:
        if request.method=='POST':
            newpassword=request.form['npassword']
            confirmpassword=request.form['cpassword']
            if newpassword==confirmpassword:
                cursor=mysql.connection.cursor()
                cursor.execute('update students set password=%s where email=%s',[newpassword,email])
                mysql.connection.commit()
                flash('Reset Successful')
                return redirect(url_for('login'))
            else:
                flash('Passwords mismatched')
                return render_template('newpassword.html')
        return render_template('newpassword.html')

    

app.run(use_reloader=True,debug=True)


























