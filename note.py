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
            self.host = host
            self.user = user
            self.pwd = pwd
            self.database = database
            self.db = pymysql.connect(host, user, pwd, database)
        except Exception as e:
            logging.error(str(e))
            exit(0)

    def checkDB(self):
        if not self.db or not self.db.open:
            try:
                self.db = pymysql.connect(self.host, self.user, self.pwd, self.database)
            except Exception as e:
                logging.error(str(e))
                exit(0)

    def closeDB(self):
        try:
            if self.db and self.db.open:
                self.db.close()
        except Exception as e:
            logging.error(str(e))
            exit(0)

    def getLast24hrsNotes(self):
        self.checkDB()
        last_time = int(time.time()) - 24*3600
        sql = "select id,note,create_time from tnote where create_time >= %d order by id desc" % (last_time)
        # print(sql)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            self.closeDB()  
            return data
        except Exception as e:
            logging.error("get notes error:" + str(e))
            # print("get notes error:" + str(e))
        return []

    def addNote(self, note):
        self.checkDB()
        nowtime = int(time.time())
        sql = "insert into tnote (note, create_time) values (%s, %s)"
        # print(sql)

        try:
            cursor = self.db.cursor()
            cursor.execute(sql, (note, str(nowtime)) )
            cursor.close()
            self.db.commit()
        except Exception as e:
            logging.error("insert note error:" + str(e))
            self.db.rollback()
        self.closeDB()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(BASE_DIR + '/.ini')

    note = Note(config['MYSQL']['HOST'],
            config['MYSQL']['USER'],
            config['MYSQL']['PASSWORD'],
            config['MYSQL']['DATABASE'])

