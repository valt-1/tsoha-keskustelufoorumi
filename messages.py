from db import db

def send(content, topic_id, user_id):
    sql = """INSERT INTO messages (content, sent_at, visible, topic_id, user_id)
             VALUES (:content, NOW(), 1, :topic_id, :user_id)"""
    db.session.execute(sql, {"content":content, "topic_id":topic_id, "user_id":user_id})
    db.session.commit()

def remove(message_id):
    sql = "UPDATE messages SET visible=0 WHERE id=:id"
    db.session.execute(sql, {"id":message_id})
    db.session.commit()

def find_all():
    result = db.session.execute("SELECT * FROM messages")
    messages = result.fetchall()
    return messages

def find_by_topic(topic_id):
    sql = "SELECT * FROM messages WHERE topic_id=:topic_id AND visible=1"
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def find_sender_id(message_id):
    sql = "SELECT user_id FROM messages WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id":message_id})
    return result.fetchone()[0]
