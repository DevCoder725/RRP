from flask import Flask, render_template, request, redirect, session,flash, url_for
import sqlite3, math

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key'

# Initialize the database
def init_db():
    conn = sqlite3.connect("rrp.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS professor (
            pid INTEGER PRIMARY KEY,
            pname VARCHAR NOT NULL,
            post VARCHAR NOT NULL,
            dept VARCHAR NOT NULL,
            password VARCHAR NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS student (
            sid INTEGER PRIMARY KEY,
            sname VARCHAR NOT NULL,
            course VARCHAR NOT NULL,
            dept VARCHAR NOT NULL,
            year INTEGER NOT NULL,
            sem INTEGER NOT NULL,
            password VARCHAR NOT NULL,
            cgpa INTEGER
        )
    """)
    
    conn.close()

init_db()

subjects = ('m1', 'ecse', 'se', 'sd')
# Home route
@app.route('/')
def index():
    return render_template("select.html")

# Login for prof
@app.route('/prof', methods=["GET", "POST"])
def prof():
    if request.method == "POST":
        pid = request.form.get("pid")
        pword = request.form.get("pword")
        if not pid or not pword:
            return render_template("l_login.html", error="Username and Password are required")

        conn = sqlite3.connect("rrp.db")
        c = conn.cursor()
        c.execute("SELECT password FROM professor WHERE pid = ?", (pid,))
        result = c.fetchone()
        print(pid,result,result[0],pword)
        if result and result[0]==pword:
            session['pid']=pid
            c.execute("SELECT subject FROM professor WHERE pid = ?", (pid,))
            sub = c.fetchone()
            session['sub'] = sub
            print(session,pid)
            return redirect('/l_dashboard')
        return render_template("l_login.html")

    #     if result and result[0] == pword:  # Plain-text password comparison
    #         session['username'] = pid
    #         return redirect("/l_dashboard")
    #     return render_template("l_login.html", error="Invalid credentials")
    return render_template("l_login.html")

# Registration for professionals
# @app.route('/l_register', methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         uid = request.form.get("id")
#         pword = request.form.get("password")
#         uname = request.form.get("name")
#         pos = request.form.get("pos")
#         dept = request.form.get("dept")
#         print(uid, uname, pos, dept, pword)  # Check what you're trying to insert
#         if not uid or not pword or not uname or not pos or not dept:
#             return "Error: All fields are required", 400

#         conn = sqlite3.connect("rrp.db")
#         c = conn.cursor()
#         c.execute("SELECT pid FROM professor WHERE pid= ?",(uid,))
#         if c.fetchone():
#             conn.close()
#             return render_template("l_register.html", error="Professor with this ID already exists")
#         c.execute("INSERT INTO professor (pid, pname, post, dept, password) VALUES (?, ?, ?, ?, ?)",
#                   (uid, uname, pos, dept, pword))
#         conn.commit()
#         conn.close()
#         return redirect("/prof")

#     return render_template("l_register.html")

# Dashboard for professionals
@app.route('/l_dashboard', methods=["GET", "POST"])
def l_dash():
    if 'pid' in session:
        conn = sqlite3.connect('rrp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT pid, pname, post, dept FROM professor WHERE pid = ?", (session['pid'],))
        prof = cursor.fetchone()
        n = len(prof)
        conn.commit()
        conn.close()
        return render_template('l_dashboard.html', prof=prof, n=n)
    else:
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('prof'))

#Selecting course from dropdown menu
@app.route('/course_dropdown', methods=['GET', 'POST'])
def dropdown():
    return render_template("course_dropdown.html")

# Marks upload route
@app.route('/upload_marks', methods=["GET", "POST"])
def upload():
    if 'pid' in session:
        dept = request.form.get('dept')
        course = request.form.get('course')
        year = request.form.get('year')
        sem = request.form.get('sem')
        exam = request.form.get('exam')

        # Check if parameters are missing
        if not all([dept, course, year, sem, exam]):
            flash("Missing query parameters. Please select the course again.", "warning")
            return redirect(url_for('dropdown'))

        conn = sqlite3.connect('rrp.db')
        c = conn.cursor()
        c.execute("""SELECT sid FROM student
                  WHERE dept = ? AND course = ? AND year = ? AND sem = ?""", (dept, course, year, sem))
        id_l = c.fetchall()
        print(id_l)
        n = len(id_l)
        session['id_l'] = id_l
        session['exam'] = exam
        print(session['exam'])
        conn.close()
        return render_template("upload_marks.html", id_l=id_l, n=n)

    flash("Session timeout! Please log in again.", "warning")
    return redirect(url_for('prof'))

#Saving marks from table
@app.route('/enter_marks',methods=["GET","POST"])
def enter():
        conn = sqlite3.connect('rrp.db')
        c = conn.cursor()
        exam = session['exam']
        if request.method == "POST":
            for i in range(len(session['id_l'])):
                m = request.form.get(f"marks{i+1}")
                sub = session['sub'][0]
                if m != "":
                    print(sub)
                    c.execute(f"UPDATE [{exam}] SET [{sub}] = ? WHERE sid = ?", (m, session['id_l'][i][0]))
                    conn.commit()
                    print(session['exam'])
                    print(session['id_l'][i][0])
                    print(type(m))
                    confirmation = "Done entering!! :)"
                else:
                    confirmation = f"Marks not entered for {session['id_l'][i][0]}!"
            return render_template("upload_marks.html",text = confirmation, id_l = session['id_l'],n=len(session['id_l']) )
        return render_template("upload_marks.html")


# Login for students
@app.route('/student', methods=["GET", "POST"])
def stud():
    if request.method == "POST":
        sid= request.form.get("sid")
        pword=request.form.get("pword")
        if not sid or not pword:
            return render_template("s_login.html", error="Username and Password are required")

        conn = sqlite3.connect("rrp.db")
        c = conn.cursor()
        c.execute("SELECT password FROM student WHERE sid = ?", (sid,))
        result = c.fetchone()
        conn.close()
        print(sid,result,result[0],pword)
        if result and result[0]==pword:
            session['sid']=sid
            print(session['sid'])
            gpCalc()
            sgpaCalc()
            return redirect('/s_dashboard')
        return render_template("s_login.html")

  
    return render_template("s_login.html")

# Student dashboard
@app.route('/s_dashboard')
def std():
    if 'sid' in session:
        conn = sqlite3.connect('rrp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT sid, sname, course, dept,year,sem FROM student WHERE sid = ?", (session['sid'],))
        stud = cursor.fetchone()

        sid = stud[0]
        name = stud[1]
        course = stud[2]
        dept = stud[3]
        year=stud[4]
        sem=stud[5]

        cursor.execute("SELECT sgpa FROM sgpa WHERE sid = ?",(session['sid'],))
        sgpa = cursor.fetchone()
        conn.close()

        return render_template('s_dashboard.html', id = sid, name=name, course=course, dept=dept,year=year,sem=sem, sgpa=sgpa)
    else:
        flash('You must be logged in to access this page.', 'warning')
        return redirect('/logout')

# Past exams route
@app.route('/past_exams')
def past_exams():
    if 'sid' in session:
        return render_template('past_exams.html')
    return redirect('/logout')

# Performance route
@app.route('/performance')
def performance():
    if ('sid' in session) :
        return render_template('performance.html')
    return redirect('/s_dashboard')
    return render_template('performance.html')

#MID 1 route
@app.route('/mid_1')
def exam():
    if 'sid' in session:
        conn = sqlite3.connect('rrp.db')
        c = conn.cursor()
        c.execute("SELECT m1, ecse, se, sd FROM MID_1 WHERE sid = ?", (session['sid'],))
        marks = c.fetchone()
        n = len(subjects)
        return render_template('mid_1.html', marks = marks, subjects = subjects, n=n)
    return redirect('/logout')

# logout
@app.route('/logout',methods=['GET','POST'])
def logout():
    if 'pid' in session or 'sid' in session:
        session.clear()
        print(session)
        return redirect('/')
    flash('Already Logged Out')
    print(session)
    return redirect('/')
    
if __name__ == '__main__':
    def gpCalc():
        conn = sqlite3.connect('rrp.db')
        c = conn.cursor()
        c.execute("SELECT * FROM sub_gpa WHERE sid = ?",(session['sid'],))
        info = c.fetchone()
        print(type(info[0]))
        if None in info:
            c.execute("SELECT m1, ecse, se, sd FROM MID_1 WHERE sid = ?", (session['sid'],))
            mid1 = c.fetchone()
            c.execute("SELECT m1, ecse, se, sd FROM MID_2 WHERE sid = ?", (session['sid'],))
            mid2 = c.fetchone()
            c.execute("SELECT m1, ecse, se, sd FROM End_Semester WHERE sid = ?", (session['sid'],))
            endsem = c.fetchone()
            print(mid1)
            print(mid2)
            print(endsem)
            gpa = []
            for i in range(4):
                avg = (mid1[i]+mid2[i])/2
                total = avg + endsem[i]
                score = math.ceil(total/10)
                gpa.append(score)
            c. execute("UPDATE sub_gpa SET m1=?, ecse=?, se=?, sd=? WHERE sid=?",(gpa[0],gpa[1],gpa[2],gpa[3],session['sid']))
            conn.commit()

    def sgpaCalc():
        conn = sqlite3.connect('rrp.db')
        c = conn.cursor()
        c.execute("SELECT creds FROM credits")
        creds = c.fetchall()
        c.execute("SELECT m1, ecse, se, sd FROM sub_gpa WHERE sid = ?", (session['sid'],))
        gpas = c.fetchone()
        # print(creds)
        # print(creds[0][0])
        # print(creds[1][0])
        # print(creds[2][0])
        # print(creds[3][0])
        # print(gpas)
        num = 0
        denom = 0
        for i in range(4):
            num+= (creds[i][0]*gpas[0])
            denom += creds[i][0]
        # print(num)
        # print(denom)
        sgpa = num/denom
        c.execute("UPDATE sgpa SET sgpa = ? WHERE sid = ?", (sgpa, session['sid']))
        conn.commit()
        # print(sgpa)


    app.run(debug=True)