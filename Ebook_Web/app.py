from flask import Flask, render_template, request, session, redirect, url_for
from datetime import timedelta
import mysql.connector

app = Flask(__name__)
app.secret_key = 'hello'
app.permanent_session_lifetime = timedelta(minutes=2)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '7t9_oR.9gyE<',
    'database': 'cotneDb'
}


def is_logged_in():
    return 'user' in session


@app.route('/books')
def books():
    db = mysql.connector.connect(**db_config)
    mycursor = db.cursor()
    mycursor.execute("SELECT * FROM books")
    books = mycursor.fetchall()
    mycursor.close()
    db.close()
    return render_template('books.html', books=books, user=session.get('user'))


@app.route('/')
def tohome():
    if is_logged_in():
        return render_template('home.html', user=session.get('user'))
    else:
        return redirect(url_for('login'))

@app.route('/addbook', methods=['GET', 'POST'])
def addbook():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages = request.form['pages']
        imageurl = request.form['imageurl']
        downloadlink = request.form['downloadlink']

        db = mysql.connector.connect(**db_config)
        mycursor = db.cursor()
        mycursor.execute("INSERT INTO books (title, author, page_count, cover_url, download_url) VALUES (%s, %s, %s, "
                         "%s, %s)",
                         (title, author, pages, imageurl, downloadlink))
        db.commit()
        mycursor.close()
        db.close()

        return redirect(url_for('books'))

    return render_template("addbook.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        email = request.form['email']
        session['user'] = user
        session['password'] = password
        session['email'] = email

        db = mysql.connector.connect(**db_config)
        mycursor = db.cursor()
        mycursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                         (user, password, email))
        db.commit()
        mycursor.close()
        db.close()

        return redirect(url_for('books'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        session['user'] = user
        session['password'] = password

        db = mysql.connector.connect(**db_config)
        mycursor = db.cursor()
        mycursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user, password))
        user_record = mycursor.fetchone()
        mycursor.close()
        db.close()

        if user_record:
            return redirect(url_for('books'))
        else:
            return "Invalid credentials. Please try again."

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('password', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
