from app import app
import messages
import topics
from flask import redirect, render_template, request

@app.route("/")
def index():
    topiclist = topics.get_all()
    return render_template("index.html", topics=topiclist)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/createtopic", methods=["POST"])
def createtopic():
    subject = request.form["subject"]
    message = request.form["content"]
    topics.create(subject, message)
    return redirect("/")

@app.route("/topic/<int:id>")
def topic(id):
    topic = topics.get_by_id(id)
    messagelist = messages.get_by_topic(id)
    return render_template("topic.html", topic=topic, messages=messagelist)

@app.route("/topic/<int:topic_id>/send", methods=["POST"])
def send(topic_id):
    content = request.form["content"]
    messages.send(content, topic_id)
    return redirect("/topic/"+str(topic_id))
