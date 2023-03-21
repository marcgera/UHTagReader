import sqlite3
import os
import platform
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


    def getLogs(self, start_time, end_time, device_id):
        conn = sqlite3.connect(self.db_full_f_name)
        conn.row_factory = dict_factory
        c = conn.cursor()

        search_string = " WHERE tag_timestamp >  " + str(start_time) + \
                            " AND tag_timestamp< " + str(end_time) + \
                            " AND tag_device_ID =" + device_id

        fields = "tagIDs.ID AS tagID, tag_timestamp, user_name, user_surname"
        sql_string = 'SELECT ' + fields + ' FROM (taglogs JOIN tagIDs on tagIDs.ID=taglogs.tag_ID) LEFT JOIN users on users.ID = tagIDs.person_id ' + search_string
        c.execute(sql_string)

        data = c.fetchall()
        conn.close()

        for entry in data:
            ts = entry.get('tag_timestamp')
            dte = self.getDate(ts)
            tme = self.getTime(ts)
            entry['datestr'] = dte
            entry['timestr'] = tme

        return data

    def getDevices(self):
        conn = sqlite3.connect(self.db_full_f_name)
        conn.row_factory = dict_factory
        c = conn.cursor()
        search_string = ""
        fields = "device_name, ID"
        sql_string = 'SELECT ' + fields + ' FROM devices ' + search_string
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        return data

    def getDate(self, timestamp):
        timestamp = str(timestamp)
        year = str(timestamp[0:4])
        month = str(timestamp[4:6])
        day = str(timestamp[6:8])
        seperator = '-'
        return year + seperator + month + seperator + day

    def getTime(self, timestamp):
        timestamp = str(timestamp)
        hour = str(timestamp[8:10])
        minute = str(timestamp[10:12])
        second = str(timestamp[12:])
        seperator = ':'
        return hour + seperator + minute + seperator + second


    def deviceExists(self, deviceMAC):
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        sql_string = "SELECT ID FROM devices WHERE device_mac = '" + deviceMAC + "'"
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        if len(data) == 0:
            return 0
        else:
            return data[0][0]

    def insertDevice(self, deviceMAC):

        current_date = datetime.now()
        datenum = current_date.strftime("%Y%m%d%H%M%S")

        sql_string = 'INSERT INTO devices (device_name, device_mac, device_entry_date)' \
                     'VALUES ("", "' + deviceMAC + '",' + datenum + ')'
        self.execute(sql_string)

        sql_string = "SELECT  ID FROM devices ORDER BY ID DESC LIMIT 1"
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        lastID = data[0]
        return lastID[0]

    def tagExists(self, tagMD5):
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        sql_string = "SELECT ID FROM tagIDs WHERE tagMD5 = '" + tagMD5 + "'"
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        if len(data) == 0:
            return 0
        else:
            return data[0][0]

    def insertTag(self, tagMD5):

        current_date = datetime.now()
        datenum = current_date.strftime("%Y%m%d%H%M%S")

        sql_string = 'INSERT INTO tagIDs (tagMD5, entry_date, person_id)' \
                     'VALUES ("' + tagMD5 + '",' + datenum + ',-1)'
        self.execute(sql_string)

        sql_string = "SELECT  ID FROM tagIDs ORDER BY ID DESC LIMIT 1"
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        lastID = data[0]
        return lastID[0]

    def log_tag(self, tagMD5, deviceMAC):

        tagID = self.tagExists(tagMD5)
        if not tagID:
            tagID = self.insertTag(tagMD5)

        deviceID = self.deviceExists(deviceMAC)
        if not deviceID:
            deviceID = self.insertDevice(deviceMAC)

        current_date = datetime.now()
        datenum = current_date.strftime("%Y%m%d%H%M%S")
        sql_string2 = 'INSERT INTO taglogs (tag_id, tag_timestamp, tag_device_ID' \
                     ') VALUES (' +  str(tagID) + ',' + datenum + ',' +  str(deviceID) + ')'
        self.execute(sql_string2)
        return 'http200OK'

    def create_db(self):
        # ********************************************************
        table_name = 'tagIDs'

        self.create_table(table_name)

        columns = ["tagMD5 TEXT DEFAULT ''", "entry_date INTEGER", "person_id INTEGER"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'users'

        self.create_table(table_name)
        columns = ["user_name TEXT DEFAULT ''",
                   "user_surname TEXT DEFAULT ''",
                   "user_email TEXT DEFAULT ''",
                   "user_external_ID TEXT DEFAULT ''",
                   "user_entry_date INTEGER DEFAULT ''"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'taglogs'

        self.create_table(table_name)
        columns = ["tag_ID INTEGER DEFAULT ''",
                   "tag_timestamp INTEGER DEFAULT ''",
                   "tag_lat INTEGER DEFAULT ''",
                   "tag_lon INTEGER DEFAULT ''",
                   "tag_device_ID INTEGER DEFAULT ''"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'devices'

        self.create_table(table_name)
        columns = ["device_name TEXT DEFAULT ''",
                   "device_mac TEXT DEFAULT ''",
                   "device_is_fixed INTEGER DEFAULT -1",
                   "device_entry_date INTEGER DEFAULT ''"]

        self.insert_columns(table_name, columns)