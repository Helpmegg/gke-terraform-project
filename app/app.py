import os
from flask import Flask, render_template, request, redirect
from google.cloud.sql.connector import Connector
import sqlalchemy

app = Flask(__name__)


INSTANCE_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")


connector = Connector()

def getconn():
    conn = connector.connect(
        INSTANCE_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        ip_type="private"
    )
    return conn


pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)


with pool.connect() as conn:
    conn.execute(sqlalchemy.text(
        "CREATE TABLE IF NOT EXISTS entries (id SERIAL PRIMARY KEY, name TEXT, message TEXT);"
    ))
    conn.commit()

@app.route("/")
def index():
    with pool.connect() as conn:
        entries = conn.execute(sqlalchemy.text("SELECT name, message FROM entries")).fetchall()
    return f"<h1>Cloud Guestbook</h1>" + "".join([f"<p><b>{e[0]}:</b> {e[1]}</p>" for e in entries]) + \
           '<form action="/post" method="post"><input name="name" placeholder="Ім\'я"><br><textarea name="msg"></textarea><br><button>Відправити</button></form>'

@app.route("/post", methods=["POST"])
def post():
    name = request.form.get("name")
    msg = request.form.get("msg")
    with pool.connect() as conn:
        conn.execute(sqlalchemy.text("INSERT INTO entries (name, message) VALUES (:n, :m)"), {"n": name, "m": msg})
        conn.commit()
    return redirect("/")

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)