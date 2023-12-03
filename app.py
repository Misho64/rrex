from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import json


app = Flask(__name__)
app.secret_key = 'somekey'


@app.route('/')
def home():
    if 'user' in session:
        updateCurrentUser()
        return render_template('home.html', user=session['user'])
    return redirect(url_for('login'))


def updateCurrentUser():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT id,empid,user_role,hours FROM users WHERE empid = '{session['user'].get('empid')}'")
    user = cursor.fetchone()
    user = {
        "id": user[0],
        "empid": user[1],
        "user_role": user[2],
        "hours": user[3]
    }
    conn.close()
    session['user'] = user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        empID = request.form['empID']  # Employee ID
        password = request.form['password']
        # Replace this with a more secure authentication mechanism
        user = check_credentials(empID, password)
        if user is not None:
            session['user'] = user
            flash("success", 'Login Successful')
            return redirect(url_for('home'))
        else:
            flash("error", 'Login Failed')
    return render_template('login.html')


@app.route('/listOfEmployees', methods=['GET'])
def getListOfEmployees():
    if session.get('user').get('user_role') == 'admin':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id,empid,hours FROM users where user_role != 'admin'")
        usersList = cursor.fetchall()
        conn.close()
        data = [
            {
                "id": i[0],
                "empid": i[1],
                "hours": i[2]
            }
            for i in usersList]
        return data


@app.route('/add_user', methods=['POST', 'GET'])
def addUser():
    if session.get('user').get('user_role') == 'admin':
        if request.method == 'POST':
            empid = request.form.get('empid')
            password = request.form.get('password')
            if empid is not None and password is not None:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute(
                    "insert into users(empid,password,user_role) values(?,?,'user') ", (empid, password))

                conn.commit()
                conn.close()
                flash('success', 'User Added Successfully')
                return redirect(url_for('home'))
            else:
                flash('error', 'Error Creating User')
                return render_template('add_user.html')
        return render_template('add_user.html')


@app.route('/submitHours', methods=['POST'])
def submitHours():
    if session.get('user').get('user_role') == 'admin':
        try:
            empid = request.json.get('empid')
            newHours = request.json.get('newHours')
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                "update users set hours = ? where empid = ?", (newHours, empid))
            conn.commit()
            conn.close()
            return jsonify({'OK': True})
        except Exception as e:
            print(e)
            return jsonify({'OK': False})

    # User section
    if session.get('user').get('user_role') == 'user':
        try:
            empid = session.get('user').get('empid')
            newHours = request.json.get('newHours')

            print(empid, newHours)
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                "update users set hours = hours + ? where empid = ?", (newHours, empid))
            conn.commit()
            conn.close()
            return jsonify({'OK': True})
        except Exception as e:
            print(e)
            return jsonify({'OK': False})


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


def check_credentials(empID, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,empid,user_role,hours FROM users WHERE empid = ? and password = ? ", (empID, password))
    user = cursor.fetchone()
    user = {
        "id": user[0],
        "empid": user[1],
        "user_role": user[2],
        "hours": user[3]
    }
    conn.close()
    return user


if __name__ == '__main__':
    app.run(debug=True)
