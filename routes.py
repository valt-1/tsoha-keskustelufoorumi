from os import getenv
from flask import flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
import messages
import topics
import users

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    topic_list = topics.find_all()
    return render_template("index.html", topics=topic_list)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if users.find_by_username(username) is None:
        flash("Virheellinen käyttäjätunnus")
    else:
        hash_value = users.find_password(username)
        if check_password_hash(hash_value, password):
            session["logged_in"] = True
            session["username"] = username
            return redirect("/")
        else:
            flash("Virheellinen salasana")

    return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    del session["username"]
    return redirect("/")

@app.route("/signup")
def signup():
    if session.get("logged_in"):
        return redirect("/")
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def new_user():
    username = request.form["username"]
    password = request.form["password"]
    confirmation = request.form["password_confirmation"]

    error = False
    if len(username) < 3 or len(username) > 20:
        error = True
        flash("Käyttäjätunnuksen pituuden tulee olla 3-20 merkkiä")
    if users.find_by_username(username):
        error = True
        flash("Käyttäjätunnus on varattu")
    if len(password) < 8:
        error = True
        flash("Salasanan pituuden tulee olla vähintään 8 merkkiä")
    if confirmation != password:
        error = True
        flash("Salasana ja vahvistus eivät täsmää")

    if error:
        return render_template("signup.html")

    hash_value = generate_password_hash(password)
    users.create(username, hash_value)
    return redirect("/")

@app.route("/newtopic")
def new_topic():
    if not session.get("logged_in"):
        return render_template("error.html",
                               error="Kirjaudu sisään luodaksesi uuden aiheen")
    return render_template("newtopic.html")

@app.route("/createtopic", methods=["POST"])
def create_topic():
    if not session.get("logged_in"):
        return render_template("error.html",
                               error="Kirjaudu sisään luodaksesi uuden aiheen")

    subject = request.form["subject"]
    message = request.form["content"]

    error = check_subject_errors(subject)
    if error:
        flash(error)
    error = check_message_errors(message)
    if error:
        flash(error)

    if error:
        return render_template("newtopic.html")

    user_id = users.find_by_username(session.get("username"))[0]
    topics.create(subject, message, user_id)
    return redirect("/")

@app.route("/topic/<int:topic_id>")
def show_topic(topic_id):
    topic = topics.find_by_id(topic_id)
    message_list = messages.find_by_topic(topic_id)

    if not session.get("logged_in"):
        user_id = None
    else:
        user_id = users.find_by_username(session.get("username"))[0]

    return render_template("topic.html", topic=topic,
                           messages=message_list, user_id=user_id)

@app.route("/topic/<int:topic_id>/send", methods=["POST"])
def send_message(topic_id):
    if not session.get("logged_in"):
        return render_template("error.html",
                               error="Kirjaudu sisään lähettääksesi viestin")

    content = request.form["content"]

    error = check_message_errors(content)
    if error:
        flash(error)
        return redirect("/topic/" + str(topic_id))

    user_id = users.find_by_username(session.get("username"))[0]
    messages.send(content, topic_id, user_id)
    return redirect("/topic/" + str(topic_id))

@app.route("/<int:topic_id>/deletemessage/<int:message_id>", methods=["POST"])
def delete_message(topic_id, message_id):
    allow = False
    user_id = users.find_by_username(session.get("username"))[0]
    if user_id == messages.find_sender_id(message_id):
        allow = True

    if not allow:
        return render_template("error.html",
                               error="""Vain kirjautuneet käyttäjät
                               voivat poistaa omia viestejään""")

    messages.remove(message_id)
    return redirect("/topic/"+str(topic_id))

def check_subject_errors(subject):
    if len(subject) < 3:
        return "Liian lyhyt otsikko. Otsikon pituuden tulee olla 3-100 merkkiä."
    if len(subject) > 100:
        return "Liian pitkä otsikko. Otsikon pituuden tulee olla 3-100 merkkiä."

    return None

def check_message_errors(message):
    if len(message) < 3:
        return "Liian lyhyt viesti. Viestin pituuden tulee olla 3-5000 merkkiä."
    if len(message) > 5000:
        return "Liian pitkä viesti. Viestin pituuden tulee olla 3-5000 merkkiä."

    return None
