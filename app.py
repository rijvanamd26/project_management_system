import os
from flask import Flask, render_template, request, redirect,url_for,flash,session
from mysql.connector import connect
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import re

UPLOADS = 'static/uploads/'
app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOADS'] = UPLOADS
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
bcrypt=Bcrypt(app)
con=connect(host='localhost',port=3306,database='pms',user='root')
cur=con.cursor()
@app.route('/')
def homepage():
    if not session.get("name"):
        return redirect("/login")
    return redirect("/home")


@app.route('/sign',methods=["GET","POST"])
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        session["name"] = None
        pwd=request.form["password"]
        cur.execute("SELECT password FROM login WHERE email=%s",[email])
        log=cur.fetchall()
        if(log):
            log=str(log[0])[2:-3]
            if(bcrypt.check_password_hash(log,pwd)):
                session["name"] = email
                return redirect('/home')
            else:
                flash('wrong password','pswd')
        else:
            flash('invalid user','email')
    return render_template('sign.html')

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

@app.route("/change_password",methods=["GET","POST"])
def change_password():
    user=session.get('name')
    if user:
        reg="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,15}$"
        pat=re.compile(reg)
        if request.method=="POST":
            email=session.get('name')
            pwd=request.form["password"]
            confirm=request.form["confirm"]
            mat=re.search(pat,pwd)
            if mat:
                pwd=bcrypt.generate_password_hash(pwd).decode('utf-8')
                if(bcrypt.check_password_hash(pwd,confirm)):
                            cur.execute("UPDATE login  SET password=%s WHERE email=%s",(pwd,email))
                            con.commit()
                            flash('password changed successfully')
                            return redirect('/home')      
                else:
                        flash('password and confirm password must match','danger')
            else:
                    flash('password must contain atleast 8 characters,it should contain atleast one uppercase,one lowercase,one special character and one digit.Maximum length of password is 15')
            return render_template('change_password.html')
        else:
            return render_template('change_password.html')
    return redirect('/sign')    


@app.route('/register',methods=["GET","POST"])
def register():
    
    reg="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,15}$"
    pat=re.compile(reg)
    if request.method=="POST":
        email=request.form["email"]
        session["name"] = email
    
        cur.execute("SELECT * FROM login WHERE email=%s",[email])
        log=cur.fetchall()
        if(log):
            flash("user already exists")
            return render_template('sign.html')

        else:
            pwd=request.form["password"]
            confirm=request.form["confirm"]
            mat=re.search(pat,pwd)
            if mat:
                pwd=bcrypt.generate_password_hash(pwd).decode('utf-8')
                if(bcrypt.check_password_hash(pwd,confirm)):
                        cur.execute("INSERT INTO login(email,password) VALUES(%s,%s)",(email,pwd))
                        con.commit()
                        return redirect('/home')      
                else:
                    flash('password and confirm password must match','danger')
            else:
                flash('password must contain atleast 8 characters,it should contain atleast one uppercase,one lowercase,one special character and one digit.Maximum length of password is 15')
            return render_template('sign.html')
    return render_template('sign.html')    


con1 = connect(host = 'localhost', port=3306, database='pms',  user='root')
cur1 = con1.cursor()

@app.route("/home")
def home():
    user=session.get('name')
    if user:
        cur1.execute("SELECT * FROM projects WHERE user=%s",(user,))
        obj=cur1.fetchall()
        # print(obj)
        return render_template("home.html",project=obj,len=len(obj))
    return redirect("/login")

@app.route("/add_project", methods=["GET","POST"])
def add_project():
    user=session.get('name')
    if user:
        if request.method == "POST":
            project_title = request.form['project_title']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            description = request.form['description']
            link = request.form['link']
            user=session.get('name')
            
            if 'file' not in request.files:
                return redirect(request.url)
            file=request.files['file']
            if file.filename=='':
                return redirect(request.url)
            else:
                filename=secure_filename(file.filename)
                # print(filename)
                file.save(os.path.join(app.config['UPLOADS'],filename))
                
            cur1.execute("insert into projects(project_title,start_date,end_date,description,link,filename,user) values(%s,%s,%s,%s,%s,%s,%s)",(project_title,start_date,end_date,description,link,filename,user))
            con1.commit()
            cur1.execute("SELECT * FROM projects where user=%s",[user])
            obj=cur1.fetchall()
            # print(obj)
        
            return render_template("home.html",project=obj,len=len(obj),filename=filename)
        else:
            return render_template("add_project.html")
    return redirect('/sign')
    
@app.route('/display/<filename>')
def display(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/edit_project/<string:id>', methods=['GET','POST'])
def edit_project(id):
    user=session.get('name')
    if user:
        if request.method == 'POST':
            print('edit')
            project_title = request.form['project_title']
            start_date = request.form['start_date']
            end_date  = request.form['end_date']
            description = request.form['description']
            link = request.form['link']
            user=session.get('name')
            file=request.files['file']

            cur.execute("UPDATE projects SET project_title=%s, start_date=%s, end_date=%s, description=%s, link=%s WHERE project_id=%s",(project_title,start_date,end_date,description,link,id))
            con.commit()
            if (len(file.filename))!=0:
                filename=secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOADS'],filename))
                cur.execute("UPDATE projects SET filename=%s WHERE project_id=%s",(filename,id))
                con.commit()

            cur1.execute("SELECT * FROM projects where user=%s",(user,))
            obj=cur1.fetchall()
            print(obj)
            return render_template("home.html",project=obj,len=len(obj))

        else:
            cur1.execute("SELECT * FROM projects WHERE user=%s",(session.get('name'),))
            obj=cur1.fetchall()
            print(obj)
            return render_template("edit_project.html",project=obj[0])
    return redirect("/sign")
            


@app.route('/del_project/<string:id>', methods=['GET'])
def del_project(id):
    user=session.get('name')
    if user:
        cur1.execute('SELECT filename FROM projects WHERE project_id=%s',(id,))
        filename=cur1.fetchall()
        filename=str(filename[0])[2:-3]
        cur1.execute("SELECT COUNT(filename) FROM projects WHERE filename=%s",(filename,))
        count=cur1.fetchall()
        cur1.execute("DELETE FROM projects WHERE project_id=%s",(id,))
        con1.commit()
        if(count[0][0]==1):
            os.remove(os.path.join(app.config['UPLOADS'],filename))
        return redirect('/home')
    else:
        return redirect("/sign")
    

if __name__ == "__main__":
    app.run(debug=True)

    
