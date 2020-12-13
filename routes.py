from os import getenv, urandom
from flask import abort, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
import messages
import subforums
import topics
import users

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    subforum_list = subforums.find_all()
    return render_template("index.html", subforums=subforum_list)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if users.find_by_username(username) is None:
        flash("Virheellinen käyttäjätunnus")
    else:
        hash_value = users.get_password(username)
        if check_password_hash(hash_value, password):
            session["logged_in"] = True
            session["username"] = username
            session["user_role"] = users.get_user_role(username)
            session["csrf_token"] = urandom(16).hex()
        else:
            flash("Virheellinen salasana")

    return redirect(request.referrer)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    del session["username"]
    del session["user_role"]
    del session["csrf_token"]

    return redirect(request.referrer)

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

    session["logged_in"] = True
    session["username"] = username
    session["user_role"] = users.get_user_role(username)
    session["csrf_token"] = urandom(16).hex()
    return redirect("/")

@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")

@app.route("/search", methods=["POST"])
def search_for():
    keyword = request.form["search"]
    message_list = messages.find_by_keyword(keyword)
    return render_template("search.html", messages=message_list)

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    subforum = subforums.find_by_id(subforum_id)
    topic_list = topics.find_by_subforum(subforum_id)
    return render_template("/subforum.html", subforum=subforum, topics=topic_list)

@app.route("/subforum/<subforum_id>/newtopic")
def new_topic(subforum_id):
    if not session.get("logged_in"):
        return render_template("error.html",
                               error="Kirjaudu sisään luodaksesi uuden aiheen")
    return render_template("newtopic.html", subforum_id=subforum_id)

@app.route("/subforum/<subforum_id>/createtopic", methods=["POST"])
def create_topic(subforum_id):
    if not session.get("logged_in"):
        return render_template("error.html",
                               error="Kirjaudu sisään luodaksesi uuden aiheen")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    subject = request.form["subject"]
    message = request.form["content"]

    subject_error = check_subject(subject)
    if subject_error:
        flash(subject_error)
    message_error = check_message(message)
    if message_error:
        flash(message_error)

    if subject_error or message_error:
        return render_template("newtopic.html", subforum_id=subforum_id)

    user_id = users.find_by_username(session.get("username"))[0]
    topics.create(subject, message, user_id, subforum_id)
    return redirect("/subforum/" + str(subforum_id))

@app.route("/deletetopic/<int:topic_id>", methods=["POST"])
def delete_topic(topic_id):
    if session.get("user_role") != "admin":
        abort(403)

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    topics.delete(topic_id)
    return redirect("/")

@app.route("/topic/<int:topic_id>")
def topic(topic_id):
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

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    content = request.form["content"]

    error = check_message(content)
    if error:
        flash(error)
        return redirect("/topic/" + str(topic_id) + "#newmessage")

    user_id = users.find_by_username(session.get("username"))[0]
    messages.create(content, topic_id, user_id)
    return redirect("/topic/" + str(topic_id))

@app.route("/editmessage/<int:message_id>", methods=["GET"])
def edit_message(message_id):
    allow = check_authorization(message_id)

    if not allow:
        return render_template("error.html",
                               error="""Vain kirjautuneet käyttäjät
                               voivat muokata omia viestejään""")

    content = messages.get_content(message_id)
    return render_template("editmessage.html",
                           content=content, message_id=message_id)

@app.route("/updatemessage/<int:message_id>", methods=["POST"])
def update_message(message_id):
    allow = check_authorization(message_id)

    if not allow:
        return render_template("error.html",
                               error="""Vain kirjautuneet käyttäjät
                               voivat muokata omia viestejään""")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    content = request.form["content"]
    error = check_message(content)
    if error:
        flash(error)
        return redirect("/editmessage/" + str(message_id))

    messages.update(message_id, content)
    topic_id = messages.get_topic_id(message_id)
    return redirect("/topic/" + str(topic_id))

@app.route("/<int:topic_id>/deletemessage/<int:message_id>", methods=["POST"])
def delete_message(topic_id, message_id):
    allow = check_authorization(message_id)

    if not allow:
        return render_template("error.html",
                               error="""Vain kirjautuneet käyttäjät
                               voivat poistaa omia viestejään""")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    messages.delete(message_id)
    return redirect("/topic/"+str(topic_id))

def check_authorization(message_id):
    if not session.get("logged_in"):
        return False

    allow = False
    user = users.find_by_username(session.get("username"))
    user_id = user[0]
    user_role = session.get("user_role")
    if user_id == messages.get_sender_id(message_id) or user_role == "admin":
        allow = True

    return allow

def check_subject(subject):
    if len(subject) < 3:
        return "Liian lyhyt otsikko. Otsikon pituuden tulee olla 3-100 merkkiä."
    if len(subject) > 100:
        return "Liian pitkä otsikko. Otsikon pituuden tulee olla 3-100 merkkiä."

    return None

def check_message(message):
    if len(message) < 3:
        return "Liian lyhyt viesti. Viestin pituuden tulee olla 3-5000 merkkiä."
    if len(message) > 5000:
        return "Liian pitkä viesti. Viestin pituuden tulee olla 3-5000 merkkiä."

    return None
