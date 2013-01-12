import json

import hashlib
import os.path
from flask import Flask,abort, redirect, url_for
app = Flask(__name__)
## db : 
##     key = hashedId
##     value = { 'name': 'Bob Ross',online: false}

DB_FILE= 'users.json'

def read_db():
    if not os.path.isfile(DB_FILE):
        write_db({})    
    return json.load(open(DB_FILE,'r'))

def write_db(db):
    json.dump(db,open(DB_FILE,'w+'))


@app.route("/user/online")
def list_online_users():
    db = read_db()
    return json.dumps([user for ident,user in db.iteritems() if user['online']])

@app.route("/user/<ident>/online")
def user_is_online(ident):
    db = read_db()
    hashedId = hashlib.md5(ident).hexdigest()
    if hashedId in db:
        return json.dumps(db[hashedId]['online'])
    else:
        abort(404)

@app.route("/user/<ident>/name")
def user_name(ident):
    db = read_db()
    hashedId = hashlib.md5(ident).hexdigest()
    if hashedId in db:
        return json.dumps(db[hashedId]['name'])
    else:
        abort(404)

@app.route("/user/<ident>/login")
def user_login(ident):
    db = read_db()
    hashedId = hashlib.md5(ident).hexdigest()
    if db[hashedId]['online']: return abort(403)
    else: 
        db[hashedId]['online'] = True
        write_db(db)
        return redirect(url_for("get_user_info",ident=ident))

@app.route("/user/<ident>/logout")
def user_logout(ident):
    db = read_db()
    hashedId = hashlib.md5(ident).hexdigest()
    if not db[hashedId]['online']: return abort(403)
    else: 
        db[hashedId]['online'] = False
        write_db(db)
        return redirect(url_for("get_user_info",ident=ident))
@app.route("/user/list")
def list_users():
    db = read_db()
    return json.dumps(db,indent=2)

@app.route("/user/<ident>")
def get_user_info(ident):
    db = read_db()
    hashedId = hashlib.md5(ident).hexdigest()
    if not hashedId in db: return abort(404)
    return json.dumps(db[hashedId])


@app.route("/user/create/<ident>/<name>")
def create_user(ident,name):
    db = read_db()
    hashedId = hashlib.md5(ident).hexdigest()
    if hashedId in db:
        return abort(403)
    else:
        db[hashedId] = {"name":name,"online":False}
    write_db(db)
    return redirect(url_for("get_user_info",ident=ident))
    
if __name__ == "__main__":
    app.debug = True
    app.run()
