from werkzeug.utils import secure_filename
from flask import Flask,render_template,send_from_directory,jsonify,request
import time,datetime
import base64
import redis
import os
import json

app = Flask(__name__)
conf = {}
r = None

KEY_MAX='TNOTE_MAX'
KEY_TNOTE='TNOTE_'


def getConf(key):
    if len(conf.keys())==0:
        filepath = os.path.dirname(os.path.realpath(__file__))
        source = filepath + "/.ini"
        with open(source, mode='r') as f:
            line = f.readline()
            while line:
                l = line.strip()
                if l and l[0] != '#':
                    arr = l.split('=')
                    if len(arr) > 1:
                        conf[arr[0]] = arr[1]
                line = f.readline()
    if key in conf.keys():
        return conf[key]
    else:
        print('Get ini error: not found key:', key)
        return ''

def getMax():
    v = r.get(KEY_MAX)
    return int(v) if v else 0

def incrMax():
    r.incr(KEY_MAX)
    r.expire(KEY_MAX, 24*3600*7)

@app.route("/")
def index():
    i = getMax()
    notes = []
    while i>=0:
        jsonStr = r.get(KEY_TNOTE+str(i))
        if jsonStr:
            item = json.loads(jsonStr, encoding='utf-8')
            if item:
                item['no']=i
                item['ishref'] = True if item['note'].find('http') > -1 else False
                print(item)
                notes.append(item)
        i = i-1
    return render_template('index.html',notes=notes)


@app.route("/add",methods=['POST'])
def add():
    note=request.form['note']
    if note:
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item = {
            "note": note,
            "created": created
        }
        ma = getMax()
        r.set(KEY_TNOTE + str(ma), json.dumps(item))
        r.expire(KEY_TNOTE + str(ma), 24*3600)
        incrMax()
    return """<script language='javascript' type='text/javascript'> window.location.href='/'; </script>"""


try:
    host = getConf('REDIS_HOST')
    port = getConf('REDIS_PORT')
    pwd  = getConf('REDIS_PASSWORD')

    if host and port and pwd:
        pool = redis.ConnectionPool(host=host, port=port, password=pwd)
        r = redis.Redis(connection_pool=pool)
        if r:
            print("Connect Redis successed")
        else:
            print("Connect Redis failed")
            exit(0)
    else:
        print("Get conf failed")
        exit(0)
except Exception as e:
    print("Connect Redis Error: ",e)
    exit(0)

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=8070)



    


