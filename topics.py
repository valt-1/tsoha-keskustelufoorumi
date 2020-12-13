from db import db
import messages

def create(subject, message, user_id, subforum_id):
    sql = """INSERT INTO topics (subject, user_id, subforum_id)
             VALUES (:subject, :user_id, :subforum_id)"""
    db.session.execute(sql,
                       {"subject":subject, "user_id":user_id, "subforum_id":subforum_id})
    db.session.commit()
    topic_id = db.session.execute("SELECT MAX(id) FROM topics").fetchone()[0]
    messages.create(message, topic_id, user_id)

def delete(topic_id):
    sql = "DELETE FROM messages WHERE topic_id=:topic_id"
    db.session.execute(sql, {"topic_id":topic_id})
    sql = "DELETE FROM topics WHERE id=:topic_id"
    db.session.execute(sql, {"topic_id":topic_id})
    db.session.commit()

def find_all():
    result = db.session.execute("SELECT * FROM topics")
    return result.fetchall()

def find_by_subforum(subforum_id):
    sql = "SELECT * FROM topics WHERE subforum_id=:subforum_id"
    result = db.session.execute(sql, {"subforum_id":subforum_id})
    return result.fetchall()

def find_by_id(topic_id):
    sql = "SELECT * FROM topics WHERE id=:id"
    result = db.session.execute(sql, {"id":topic_id})
    return result.fetchone()
