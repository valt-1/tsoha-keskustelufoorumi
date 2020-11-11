from app import app
import messages
from flask import redirect, render_template, request

@app.route("/")
def index():
    allmessages = messages.get_messages()
    return render_template("index.html", messages=allmessages)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    messages.send(content)
    return redirect("/")
