import json
import time
import hashlib
import os.path
import redis
from flask import Flask,abort, redirect, url_for
app = Flask(__name__)
db={}
## db : 
##     key = hashedId
##     value = { 'name': 'Bob Ross',online: false}

REDIS_SERVER = "glados.shack"
r = redis.StrictRedis(host=REDIS_SERVER, port=6379, db=0)

@app.route("/user/online")
def list_online_users():
    ret= {"users":[]}
    for uid in r.smembers("users.all"):
        if r.get("users.list."+uid+".online"):
            nick = r.get("users.list."+uid+".online")
            ret["users"].append(nick)

    return json.dumps(ret)

@app.route("/user/<ident>/online")
def user_is_online(ident):
    """
    TODO generate hash from uid (default is currently RFID-UID)
    """
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.ismemeber("users.all",hashedId): abort(404)
    return json.dumps(r.exists(("users.list."+hashedId+".online")))

@app.route("/user/<ident>/name")
def user_name(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.ismemeber("users.all",hashedId): abort(404)

    return json.dumps(r.get(("users.list."+hashedId+".name")))

@app.route("/user/<ident>/login")
def user_login(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.ismemeber("users.all",hashedId): abort(404)

    r.rpush("users.list."+hashedId+".history",str(time.time())+";login")
    r.setex("users.list."+hashedId+".online",True,86400)
    return redirect(url_for("get_user_info",ident=ident))

@app.route("/user/<ident>/logout")
def user_logout(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.ismemeber("users.all",hashedId): abort(404)

    r.rpush("users.list."+hashedId+".history",str(time.time())+";logout")
    r.delete("users.list."+hashedId+".online")

    return redirect(url_for("get_user_info",ident=ident))

@app.route("/user/list")
def list_users():
    ret= {"users":[]}
    for uid in r.smembers("users.all"):
        nick = r.get("users.list."+uid+".nick")
        ret["users"].append(nick)
    return json.dumps(ret,indent=2)

@app.route("/user/<ident>")
def get_user_info(ident):
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember("users.all",hashedId): abort(404)
    user = {}
    user["name"] = r.get("users.list."+hashedId+".name")
    user["online"] = r.get("users.list."+hashedId+".online")
    user["history"] = r.get("users.list."+hashedId+".history")
    return json.dumps(user)


@app.route("/user/create/<ident>/<name>")
def create_user(ident,name):
    db = read_db()
    hashedId = hashlib.md5(ident).hexdigest()
    if r.ismemeber("users.all",hashedId):
        return abort(403)
    else:
        r.set("users.list."+hashedId+".name")
    return redirect(url_for("get_user_info",ident=ident))
    
if __name__ == "__main__":
    app.debug = True
    app.run("0.0.0.0")
