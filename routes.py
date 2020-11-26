from flask import redirect, render_template, request
from app import app
import messages
import topics

@app.route("/")
def index():
    topic_list = topics.find_all()
    return render_template("index.html", topics=topic_list)

@app.route("/new")
def new_topic():
    return render_template("new.html")

@app.route("/createtopic", methods=["POST"])
def create_topic():
    subject = request.form["subject"]
    message = request.form["content"]
    topics.create(subject, message)
    return redirect("/") # TODO: fix redirect

@app.route("/topic/<int:topic_id>")
def show_topic(topic_id):
    topic = topics.find_by_id(topic_id)
    message_list = messages.find_by_topic(topic_id)
    return render_template("topic.html", topic=topic, messages=message_list)

@app.route("/topic/<int:topic_id>/send", methods=["POST"])
def send_message(topic_id):
    content = request.form["content"]
    messages.send(content, topic_id)
    return redirect("/topic/"+str(topic_id))

@app.route("/<int:topic_id>/deletemessage/<int:message_id>", methods=["POST"])
def delete_message(topic_id, message_id):
    messages.remove(message_id)
    return redirect("/topic/"+str(topic_id))
