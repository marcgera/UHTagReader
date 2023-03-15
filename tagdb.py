import sqlite3
import os
import platform
import calendar
from datetime import datetime


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def csv_factory(cursor, row):
    d = ''
    for idx, col in enumerate(cursor.description):
        if idx == 0:
            d = str(row[idx])
        else:
            d = d + ';' + str(row[idx])
    return d

class tagdb(object):

    def __init__(self):
        import configparser
        config = configparser.ConfigParser()
        current_os = platform.system().lower()

        if current_os.lower() == "windows":
            db_path = os.path.dirname(os.path.realpath(__file__))  + os.path.sep + 'database' + os.path.sep
        else:
            db_path = os.getcwd() + '/database/'

        self.db_f_name = 'tagdb'
        self.db_dir_name = db_path
        self.db_full_f_name = self.db_dir_name + self.db_f_name + '.db'
        print('Database location:')
        print(self.db_full_f_name)
        self.conn = sqlite3.connect(self.db_full_f_name)


    def create_table(self, table_name):
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        sql_string1 = 'CREATE TABLE IF NOT EXISTS ' \
                      + table_name \
                      + '(ID INTEGER PRIMARY KEY);'
        c.execute(sql_string1)
        conn.close()
        return

    def conn(self):
        return self.conn

    def insert_columns(self, table_name, columns):
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        for column in columns:
            sql_string = 'ALTER TABLE ' + table_name + '  ADD COLUMN ' + column + ';'
            try:
                c.execute(sql_string)
            except sqlite3.Error as e:
                if not 'duplicate column name:' in e.args[0]:
                    print(e.args[0])
        conn.close()

    def select(self, sql_string):
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        return data

    def get_base_name(self):
        splitted = self.db_f_name.split('.')
        return splitted[0]

    def get_name(self):
        return self.db_f_name

    def execute(self, sql_string):
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        c.execute(sql_string)
        conn.commit()
        conn.close()
        return

    def tagExists(self, tagMD5):

        conn = sqlite3.connect(self.db_full_f_name)
        conn.row_factory = dict_factory
        c = conn.cursor()
        sql_string = "SELECT * FROM tagIDs WHERE tagID = '" + tagMD5 + "'"
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        return data

    def log_tag(self, tagMD5):

        ti = self.tagExists(tagMD5)
        if ti:
            return 'Tag in db'
        else:
            return 'Not in db'



    def create_db(self):
        # ********************************************************
        table_name = 'tagIDs'

        self.create_table(table_name)

        columns = ["tagID TEXT DEFAULT ''", "entry_date INTEGER", "person_id INTEGER"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'users'

        self.create_table(table_name)
        columns = ["user_name TEXT DEFAULT ''",
                   "user_surname TEXT DEFAULT ''",
                   "user_email TEXT DEFAULT ''",
                   "user_entry_date INTEGER DEFAULT ''"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'taglogs'

        self.create_table(table_name)
        columns = ["tag_id INTEGER DEFAULT ''",
                   "tag_timestamp INTEGER DEFAULT ''",
                   "tag_device TEXT DEFAULT ''"]

        self.insert_columns(table_name, columns)