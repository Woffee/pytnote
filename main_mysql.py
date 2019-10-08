from werkzeug.utils import secure_filename
from flask import Flask, render_template, send_from_directory, jsonify, request, redirect
import time
import logging
import os
import json
import configparser
from note import Note

app = Flask(__name__)

noteObj = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(BASE_DIR + '/.ini')

today = time.strftime("%Y-%m-%d", time.localtime())
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(filename)s line: %(lineno)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=BASE_DIR + '/logs/tnote-' + today + '.log')


@app.route("/")
def index():
    global noteObj
    notes = []

    data = noteObj.getLast24hrsNotes()
    for d in data:
        item = {}
        item['no'] = d[0]
        item['note'] = d[1]
        item['created'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d[2]))
        item['ishref'] = True if item['note'].find('http') > -1 else False
        notes.append(item)

    return render_template('index.html', notes=notes)


@app.route("/add", methods=['POST'])
def add():
    nn = request.form['note']
    if nn:
        noteObj.addNote(nn)
    return redirect('/')


def checkMysql():
    global noteObj,config
    if noteObj:
        # logging.info("MySQL already connected")
        return
    try:
        noteObj = Note(config['MYSQL']['HOST'],
                config['MYSQL']['USER'],
                config['MYSQL']['PASSWORD'],
                config['MYSQL']['DATABASE'])
    except Exception as e:
        logging.error("Connect MySQL error: "+str(e))
        exit(0)

# def closeMysql():
#     global noteObj
#     if noteObj:
#         noteObj.closeDB()
#         print("close db....")

app.before_request(checkMysql)
# app.after_request(closeMysql)

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=8070)






