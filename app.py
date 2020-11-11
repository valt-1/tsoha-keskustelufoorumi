from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute("SELECT content, sent_at FROM messages")
    messages = result.fetchall()
    return render_template("index.html", messages=messages)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/sendmessage", methods=["POST"])
def sendmessage():
    content = request.form["content"]
    sql = "INSERT INTO messages (content, sent_at) VALUES (:content, NOW())"
    db.session.execute(sql, {"content":content})
    db.session.commit()
    return redirect("/")
