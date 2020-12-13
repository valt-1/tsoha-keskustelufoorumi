from db import db

def find_all():
    result = db.session.execute("SELECT * FROM subforums")
    return result.fetchall()

def find_by_id(subforum_id):
    sql ="SELECT * FROM subforums WHERE id=:subforum_id"
    result = db.session.execute(sql, {"subforum_id":subforum_id})
    return result.fetchone()
