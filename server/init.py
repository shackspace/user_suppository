import json
import time
import hashlib
import os.path
import redis
from flask import Flask,abort, redirect, url_for,render_template
app = Flask(__name__)
db={}
NS="users."
NSL=NS+"list."

REDIS_SERVER = "glados.shack"
r = redis.StrictRedis(host=REDIS_SERVER, port=6379, db=0)
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/online")
def online():
    return render_template('list_users.html',users=list_online_users())

@app.route("/all")
def all_users():
    return render_template('list_users.html',users=list_users())

@app.route("/user/online")
def json_online():
    return json.dumps(list_online_users())


@app.route("/user/list")
def json_list_users():
    return json.dumps(list_users())


@app.route("/user/<ident>/online")
def user_is_online(ident):
    """
    TODO generate hash from uid (default is currently RFID-UID)
    """
    ident = ident.lower()
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)
    return json.dumps(r.exists((NSL+hashedId+".online")))

@app.route("/user/<ident>/name")
def user_name(ident):
    ident = ident.lower()
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)

    return json.dumps(r.get((NSL+hashedId+".name")))

@app.route("/user/<ident>/login")
def user_login(ident):
    ident = ident.lower()
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)

    r.rpush(NSL+hashedId+".history",str(time.time())+" login")
    # half a day
    r.setex(NSL+hashedId+".online",86400/2,"True")
    return redirect(url_for("get_user_info",ident=ident))

@app.route("/user/<ident>/logout")
def user_logout(ident):
    ident = ident.lower()
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)

    r.rpush(NSL+hashedId+".history",str(time.time())+" logout")
    r.delete(NSL+hashedId+".online")

    return redirect(url_for("get_user_info",ident=ident))


@app.route("/user/<ident>")
def get_user_info(ident):
    ident = ident.lower()
    hashedId = hashlib.md5(ident).hexdigest()
    if not r.sismember(NS+"all",hashedId): abort(404)
    user = {}
    user["name"] = r.get(NSL+hashedId+".name")
    user["online"] = r.get(NSL+hashedId+".online")
    user["history"] = r.lrange(NSL+hashedId+".history",0,-1)
    return json.dumps(user)


def fuck_you(text):
    return "<html><head><script>while (1){ alert('%s');}</script></head></html>" %text

@app.route("/user/create/<ident>/<name>")
def create_user(ident,name):
    ident = ident.lower()
    try:
        int(ident,16)
    except:
        return fuck_you("uid has to be hex")
    import re
    pattern = re.compile("^[a-zA-Z_*+\[\]|+=!@#$%^&*()-]+$")
    if not pattern.match(name):
        return fuck_you("nick name must match pattern")
    #name = name.
    hashedId = hashlib.md5(ident).hexdigest()
    if r.sismember(NS+".all",hashedId):
        return abort(403)
    else:
        r.set(NSL+hashedId+".name",name)
        r.sadd(NS+"all",hashedId)
    return redirect(url_for("get_user_info",ident=ident))
    
def list_users():
    ret= []
    for uid in r.smembers(NS+"all"):
        nick = r.get(NSL+uid+".name")
        ret.append(nick)
    return ret

def list_online_users():
    ret= []
    for uid in r.smembers(NS+"all"):
        if r.get(NSL+uid+".online"):
            nick = r.get(NSL+uid+".name")
            ret.append(nick)
    return ret

if __name__ == "__main__":
    app.debug = True
    app.run("0.0.0.0")
