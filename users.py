from db import db

def create(username, password):
    sql = """INSERT INTO users (username, password, user_role)
             VALUES (:username, :password, 'user')"""
    db.session.execute(sql, {"username":username, "password":password})
    db.session.commit()

def find_by_username(username):
    sql = "SELECT * FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    return result.fetchone()

def get_password(username):
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    return result.fetchone()[0]

def get_user_role(username):
    sql = "SELECT user_role FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    return result.fetchone()[0]
