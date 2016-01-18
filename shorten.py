import sqlite3
import string
import random
from flask import Flask, render_template, request, g, redirect

# configuration
DATABASE = 'shorten.db'
DEBUG = True
SECRET_KEY = 'mysecret'
USERNAME = 'root'
PASSWORD = 'password'

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('form.html')


@app.route("/shorten", methods=['POST'])
def shorten():
    long_url = request.form['url']
    existing_url_record = query_db('select short from shorten where url = ?', (long_url,), one=True)
    if existing_url_record is None:
        short_url = shorten_url(3)
        insert_db('shorten', ('url', 'short'), (long_url, short_url))
    else:
        short_url = existing_url_record[0]

    return render_template('shortened.html', url=long_url, short=short_url)


@app.route('/<short_url>')
def catch_all(short_url):
    existing_url_record = query_db('select url from shorten where short = ?', (short_url,), one=True)
    if existing_url_record is None:
        long_url = '/'
    else:
        long_url = existing_url_record[0]
    return redirect(long_url, code=302)


def shorten_url(x):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(x))


def connect_db():
    return sqlite3.connect('shorten.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_db(table, fields=(), values=()):
    cur = g.db.cursor()
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur.execute(query, values)
    g.db.commit()
    cur.close()
    return ''


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
