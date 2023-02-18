from flask import Flask, render_template, request, redirect
from mysql.connector import connect


con = connect(host = 'localhost', port=3306, database='pms',  user='root')
cur = con.cursor()
app = Flask(__name__)
@app.route("/")
def home():
    cur.execute("SELECT * FROM projects")
    obj=cur.fetchall()
    print(obj)
    return render_template("home.html",project=obj,len=len(obj))

@app.route("/add_project", methods=["GET","POST"])
def add_project():
    if request.method == "POST":
        project_title = request.form['project_title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        description = request.form['description']
        link = request.form['link']
        cur.execute("insert into projects(project_title,start_date,end_date,description,link) values(%s,%s,%s,%s,%s)",(project_title,start_date,end_date,description,link))
        con.commit()
        cur.execute("SELECT * FROM projects")
        obj=cur.fetchall()
        print(obj)
        return render_template("home.html",project=obj,len=len(obj))
    else:
        return render_template("add_project.html")

@app.route('/edit_project/<string:id>', methods=['GET','POST'])
def edit_project(id):
    if request.method == 'POST':
        project_title = request.form['project_title']
        start_date = request.form['start_date']
        end_date  = request.form['end_date']
        description = request.form['description']
        link = request.form['link']

        cur.execute("DELETE FROM projects WHERE project_id=%s",(id,))
        con.commit()
        
        cur.execute("insert into projects values(%s,%s,%s,%s,%s,%s)",(id,project_title,start_date,end_date,description,link))
        con.commit()

        cur.execute("SELECT * FROM projects")
        obj=cur.fetchall()
        return redirect("/")
    else:
        cur.execute("SELECT * FROM projects WHERE project_id=%s",(id,))
        obj=cur.fetchall()
        return render_template("edit_project.html",project=obj[0])


@app.route('/del_project/<string:id>', methods=['GET'])
def del_project(id):
    cur.execute("DELETE FROM projects WHERE project_id=%s",(id,))
    con.commit()
    return "del "

if __name__ == "__main__":
    app.run(debug=True)
