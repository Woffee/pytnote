from werkzeug.utils import secure_filename
from flask import Flask, render_template, send_from_directory, jsonify, request, redirect
import time
import datetime
import logging
import os
import json
import configparser

app = Flask(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = BASE_DIR + '/notes/'

today = time.strftime("%Y-%m-%d", time.localtime())
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(filename)s line: %(lineno)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=BASE_DIR + '/logs/tnote-' + today + '.log')

def get_notes(day):
    filepath = SAVE_PATH + 'tnote-' + day + '.txt'
    res = []
    if os.path.exists(filepath):
        # Iterate over the lines of the file
        with open(filepath, 'rt') as f:
            for line in f:
                item = json.loads(line, encoding='utf-8')
                if item:
                    res.append(item)
        # process line
    return res


@app.route("/")
def index():
    yesterday = str(datetime.date.today() + datetime.timedelta(-1))
    today = str(datetime.date.today())

    d1 = get_notes(yesterday)
    d2 = get_notes(today)

    notes = []
    d1.extend(d2)

    i = 1
    for d in d1:
        item = {}
        item['no'] = i
        item['note'] = d['note']
        item['created'] = d['created']
        item['ishref'] = True if item['note'].find('http') > -1 else False
        notes.append(item)
        i = i + 1

    return render_template('index.html', notes=notes)

@app.route("/list", methods=['GET'])
def list():
    yesterday = str(datetime.date.today() + datetime.timedelta(-1))
    today = str(datetime.date.today())

    d1 = get_notes(yesterday)
    d2 = get_notes(today)

    notes = []
    d1.extend(d2)

    i = 1
    for d in d1:
        item = {}
        item['no'] = i
        item['note'] = d['note']
        item['created'] = d['created']
        item['ishref'] = True if item['note'].find('http') > -1 else False
        notes.append(item)
        i = i + 1

    return jsonify({
        "success": True,
        "notes": notes
    })

@app.route("/add", methods=['POST'])
def add():
    note = request.form['note']
    if note:
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item = {
            "note": note,
            "created": created
        }
        today = str(datetime.date.today())
        filepath = SAVE_PATH + 'tnote-' + today + '.txt'
        # Write chunks of text data
        with open(filepath, 'at') as f:
            f.write(json.dumps(item) + "\n")

        return json.dumps({
            "success":True,
            "note": note,
            "created": created
        })
    return json.dumps({
        "success": False,
        "message": "Unknown error"
    })

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    down_path = BASE_DIR + '/files/'
    if not os.path.exists(down_path) :
        os.makedirs(down_path) 
    return send_from_directory(down_path, filename, as_attachment=True)

# app.before_request(checkMysql)
# app.after_request(closeMysql)

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=8070)






