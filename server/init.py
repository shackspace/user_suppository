import json
import time
import hashlib
import os.path
import redis
from flask import Flask,abort, redirect, url_for
app = Flask(__name__)
db={}
NS="users."
NSL=NS+"list."
## db : 
##     key = hashedId
##     value = { 'name': 'Bob Ross',online: false}

REDIS_SERVER = "glados.shack"
r = redis.StrictRedis(host=REDIS_SERVER, port=6379, db=0)

@app.route("/user/online")
def list_online_users():
    ret= []
    for uid in r.smembers(NS+"all"):
        if r.get(NSL+uid+".online"):
            nick = r.get(NSL+uid+".name")
            ret.append(nick)

    return json.dumps(ret)

@app.route("/user/<ident>/online")
def user_is_online(ident):
    """
    TODO generate hash from uid (default is currently RFID-UID)
    """
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)
    return json.dumps(r.exists((NSL+hashedId+".online")))

@app.route("/user/<ident>/name")
def user_name(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)

    return json.dumps(r.get((NSL+hashedId+".name")))

@app.route("/user/<ident>/login")
def user_login(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)

    r.rpush(NSL+hashedId+".history",str(time.time())+" login")
    r.setex(NSL+hashedId+".online",86400,"True")
    return redirect(url_for("get_user_info",ident=ident))

@app.route("/user/<ident>/logout")
def user_logout(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)

    r.rpush(NSL+hashedId+".history",str(time.time())+" logout")
    r.delete(NSL+hashedId+".online")

    return redirect(url_for("get_user_info",ident=ident))

@app.route("/user/list")
def list_users():
    ret= []
    for uid in r.smembers(NS+"all"):
        nick = r.get(NSL+uid+".name")
        ret.append(nick)
    return json.dumps(ret)

@app.route("/user/<ident>")
def get_user_info(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)
    user = {}
    user["name"] = r.get(NSL+hashedId+".name")
    user["online"] = r.get(NSL+hashedId+".online")
    user["history"] = r.lrange(NSL+hashedId+".history",0,-1)
    return json.dumps(user)


@app.route("/user/create/<ident>/<name>")
def create_user(ident,name):
    hashedId = hashlib.md5(ident).hexdigest()
    if r.sismember(NS+".all",hashedId):
        return abort(403)
    else:
        r.set(NSL+hashedId+".name",name)
        r.sadd(NS+"all",hashedId)
    return redirect(url_for("get_user_info",ident=ident))
    
if __name__ == "__main__":
    app.debug = True
    app.run("0.0.0.0")
