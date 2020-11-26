from db import db
import messages

def create(subject, message):
    sql = "INSERT INTO topics (subject) VALUES (:subject)"
    db.session.execute(sql, {"subject":subject})
    sql = "SELECT id FROM topics WHERE subject=:subject"
    result = db.session.execute(sql, {"subject":subject})
    topic_id = result.fetchone()[0]
    messages.send(message, topic_id)

def find_all():
    result = db.session.execute("SELECT * FROM topics")
    topics = result.fetchall()
    return topics

def find_by_id(topic_id):
    sql = "SELECT * FROM topics WHERE id=:id"
    result = db.session.execute(sql, {"id":topic_id})
    topic = result.fetchone()
    return topic
