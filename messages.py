from db import db

def send(content):
    sql = "INSERT INTO messages (content, sent_at) VALUES (:content, NOW())"
    db.session.execute(sql, {"content":content})
    db.session.commit()

def get_messages():
    result = db.session.execute("SELECT content, sent_at FROM messages")
    messages = result.fetchall()
    return messages
