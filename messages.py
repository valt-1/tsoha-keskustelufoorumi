from db import db

def create(content, topic_id, user_id):
    sql = """INSERT INTO messages (content, sent_at, visible, topic_id, user_id)
             VALUES (:content, NOW(), 1, :topic_id, :user_id)"""
    db.session.execute(sql, {"content":content, "topic_id":topic_id, "user_id":user_id})
    db.session.commit()

def delete(message_id):
    sql = "UPDATE messages SET visible=0 WHERE id=:message_id"
    db.session.execute(sql, {"message_id":message_id})
    db.session.commit()

def update(message_id, content):
    sql = "UPDATE messages SET content=:content WHERE id=:message_id"
    db.session.execute(sql, {"content":content, "message_id":message_id})
    db.session.commit()

def find_all():
    result = db.session.execute("SELECT * FROM messages")
    return result.fetchall()

def find_by_topic(topic_id):
    sql = """SELECT M.visible, U.username, M.content, M.sent_at, M.user_id, M.id
             FROM messages M, users U
             WHERE topic_id=:topic_id AND M.user_id=U.id
             ORDER BY M.id"""
    result = db.session.execute(sql, {"topic_id":topic_id})
    return result.fetchall()

def find_by_keyword(keyword):
    keyword = "%" + keyword + "%"
    sql = """SELECT M.visible, U.username, M.content, M.sent_at, M.user_id, M.id, M.topic_id, T.subject
             FROM messages M, users U, topics T
             WHERE M.user_id=U.id AND M.topic_id=T.id
             AND (U.username LIKE :keyword OR M.content LIKE :keyword)
             ORDER BY id DESC"""
    result = db.session.execute(sql, {"keyword":keyword})
    return result.fetchall()

def get_sender_id(message_id):
    sql = "SELECT user_id FROM messages WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id":message_id})
    return result.fetchone()[0]

def get_topic_id(message_id):
    sql = "SELECT topic_id FROM messages WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id":message_id})
    return result.fetchone()[0]

def get_content(message_id):
    sql = "SELECT content FROM messages WHERE id=:message_id"
    result = db.session.execute(sql, {"message_id":message_id})
    return result.fetchone()[0]
