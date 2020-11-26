from db import db
import messages

def create(subject, message, user_id):
    sql = "INSERT INTO topics (subject, user_id) VALUES (:subject, :user_id)"
    db.session.execute(sql, {"subject":subject, "user_id":user_id})
    db.session.commit()
    topic_id = db.session.execute("SELECT MAX(id) FROM topics").fetchone()[0]
    messages.send(message, topic_id, user_id)

def find_all():
    result = db.session.execute("SELECT * FROM topics")
    topics = result.fetchall()
    return topics

def find_by_id(topic_id):
    sql = "SELECT * FROM topics WHERE id=:id"
    result = db.session.execute(sql, {"id":topic_id})
    topic = result.fetchone()
    return topic
