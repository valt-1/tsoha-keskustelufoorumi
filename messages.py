from db import db

def send(content, topic_id):
    sql = "INSERT INTO messages (content, sent_at, topic_id) VALUES (:content, NOW(), :topic_id)"
    db.session.execute(sql, {"content":content, "topic_id":topic_id})
    db.session.commit()

def get_all():
    result = db.session.execute("SELECT * FROM messages")
    messages = result.fetchall()
    return messages

def get_by_topic(id):
    sql = "SELECT * FROM messages WHERE topic_id=:topic_id"
    result = db.session.execute(sql, {"topic_id":id})
    return result.fetchall()
