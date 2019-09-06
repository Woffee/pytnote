# coding=utf-8
import pymysql
import time
import configparser
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

today = time.strftime("%Y-%m-%d", time.localtime())
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(filename)s line: %(lineno)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=BASE_DIR + '/logs/tnote-' + today + '.log')


class Note:
    def __init__(self, host, user, pwd, database):
        try:
            self.db = pymysql.connect(host, user, pwd, database)
        except Exception as e:
            logging.error(str(e))
            exit(0)

    def getLast24hrsNotes(self):
        last_time = int(time.time()) - 24*3600
        sql = "select id,note,create_time from tnote where create_time >= %d order by id desc" % (last_time)
        # print(sql)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
        except Exception as e:
            print("get notes error:" + str(e))
        return []

    def addNote(self, note):
        nowtime = int(time.time())
        sql = "insert into tnote (note, create_time) values ('%s', %d)" % (note, nowtime)
        # print(sql)

        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            logging.error("insert note error:" + str(e))
            self.db.rollback()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(BASE_DIR + '/.ini')

    note = Note(config['MYSQL']['HOST'],
            config['MYSQL']['USER'],
            config['MYSQL']['PASSWORD'],
            config['MYSQL']['DATABASE'])

