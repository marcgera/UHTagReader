import sqlite3
import os
import platform
from datetime import datetime
import arrow
import xlsxwriter

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

    def get_gmt_ts(self):
        utc = arrow.utcnow()
        ldt = utc.to('Europe/Brussels')

        year = str(ldt.year)
        month = str(ldt.month).zfill(2)
        day = str(ldt.day).zfill(2)
        hour = str(ldt.hour).zfill(2)
        minute = str(ldt.minute).zfill(2)
        second = str(ldt.second).zfill(2)

        datenum_str = year + month + day + hour + minute + second

        return datenum_str

    def dump(self):
        conn = sqlite3.connect(self.db_full_f_name)
        strdump = ''
        for line in conn.iterdump():
            strdump = strdump + line + '<br>'
        return strdump

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

    def getUsers(self, select_field, selection):
        sql_string = "SELECT * FROM users WHERE " + select_field + " LIKE '" + selection + "'"
        return self.selectDict(sql_string)



    def getMostRecentLogEntry(self, device_id):
        fields = "user_name, user_surname, user_email, tag_id, tag_timestamp, users.ID "
        table = "(taglogs JOIN tagIDs on taglogs.tag_ID=tagIDs.ID) LEFT JOIN users on tagIDs.person_ID=users.ID"
        sql_string = "SELECT " + fields + " FROM " + table + " WHERE tag_device_ID=" + str(device_id) + \
                     " ORDER BY tag_timestamp DESC LIMIT 1"
        result = self.selectDict(sql_string)[0]
        loggedTimeStamp = result["tag_timestamp"]
        nowTimeStamp = int(self.get_gmt_ts())

        if nowTimeStamp-loggedTimeStamp > 200:
            return "No recent (last 2 minutes) log entry found for device ID" + str(device_id)
        else:
            return self.selectDict(sql_string)[0]

    def selectDict(self, sql_string):
        conn = sqlite3.connect(self.db_full_f_name)
        conn.row_factory = dict_factory
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

    def registerUser(self, user_name , user_surname, user_email, event_id):
        sqlString = 'SELECT *  FROM Users WHERE LOWER(user_email) LIKE LOWER("' + user_email + '")'
        result = self.select(sqlString)
        if result.__len__() == 0:
            sqlString = 'INSERT INTO Users (user_name, User_surname, user_email) VALUES (' + \
                '"' + user_name + '","' + '"' + user_surname + '","' + '"' + user_email + '")'
            self.execute(sqlString)
            sqlString = 'SELECT ID FROM users WHERE user_email="' + user_email


    def get_logs(self, start_time, end_time, device_id):
        conn = sqlite3.connect(self.db_full_f_name)
        conn.row_factory = dict_factory
        c = conn.cursor()

        search_string = " WHERE tag_timestamp >  " + str(start_time) + \
                            " AND tag_timestamp< " + str(end_time) + \
                            " AND tag_device_ID =" + device_id

        fields = "tagIDs.ID AS tagID, tag_timestamp, user_name, user_surname, " \
                 "users.ID as user_id, user_email, user_external_ID "
        sql_string = 'SELECT ' + fields + ' FROM (taglogs JOIN tagIDs on tagIDs.ID=taglogs.tag_ID) ' \
                                          'LEFT JOIN users on users.ID = tagIDs.person_id ' + search_string
        sql_string = sql_string + ' ORDER BY tag_timestamp ASC'
        c.execute(sql_string)

        data = c.fetchall()
        conn.close()

        workbook = xlsxwriter.Workbook('static/downloads/logs.xlsx')
        worksheet = workbook.add_worksheet()

        row = 1

        for entry in data:
            ts = entry.get('tag_timestamp')
            dte = self.getDate(ts)
            tme = self.getTime(ts)

            if entry['user_name']:
                user_name = entry['user_name']
            else:
                user_name = ' '

            if entry['user_surname']:
                user_surname = entry['user_surname']
            else:
                user_surname = ' '

            if entry['user_email']:
                user_email = entry['user_email']
            else:
                user_email = ' '

            if entry['user_external_ID']:
                user_external_ID = entry['user_external_ID']
            else:
                user_external_ID = ' '
            entry['datestr'] = dte
            entry['timestr'] = tme

            worksheet.write(row, 0, row)
            worksheet.write(row, 1, dte)
            worksheet.write(row, 2, tme)
            worksheet.write(row, 3, user_name)
            worksheet.write(row, 4, user_surname)
            worksheet.write(row, 5, user_email)
            worksheet.write(row, 6, user_external_ID)
            row += 1

        workbook.close()

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


    def insert_user_and_link2tag(self, tag_id, user_name, user_surname, user_external_id, user_email):

        sql_string = 'SELECT ID FROM users WHERE user_email="' + user_email + '"'
        result = self.selectDict(sql_string)

        if result:
            result = result[0];
            user_ID = result.get('ID')
            sql_string = 'UPDATE users set user_name = "' \
                        + user_name + '", user_surname="' \
                        + user_surname + '",user_external_id="' \
                        + user_external_id + '" WHERE ID=' \
                        + str(user_ID)
            self.execute(sql_string)
            lastID = user_ID

        else:

            sql_string = 'INSERT INTO users (user_name, user_surname, user_email, user_external_ID, user_entry_date) ' \
                         'VALUES ("' +  user_name + \
                         '","' + user_surname + \
                         '","' + user_external_id + \
                         '","' + user_email + \
                         '",' +self.get_now_timestamp() + ')'

            self.execute(sql_string)
            sql_string = "SELECT ID FROM users ORDER BY ID DESC LIMIT 1"
            conn = sqlite3.connect(self.db_full_f_name)
            c = conn.cursor()
            c.execute(sql_string)
            data = c.fetchall()
            conn.close()
            lastID = data[0][0]

        sql_string = 'UPDATE tagIDs SET person_id=' + str(lastID) + ' WHERE ID=' + tag_id
        self.execute(sql_string)
        return 'http200OK'

    def update_user(self, ID, user_name, user_surname, user_external_id, user_email):
        sql_string = 'UPDATE users SET user_name="' + user_name + '", user_surname="' + user_surname + '", ' + \
            ' user_external_ID="' + user_external_id + '", user_email="' + user_email + '" WHERE ID=' + ID
        self.execute(sql_string)
        return 'http200OK'

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

    def get_now_timestamp(self):
        current_date = datetime.now()
        datenum = current_date.strftime("%Y%m%d%H%M%S")
        return datenum

    def insertDevice(self, deviceMAC):

        datenum = self.get_now_timestamp()

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

        sql_string = 'INSERT INTO tagIDs (tagMD5, entry_date, person_id)' \
                     'VALUES ("' + tagMD5 + '",' + self.get_gmt_ts() + ',-1)'
        self.execute(sql_string)

        sql_string = "SELECT  ID FROM tagIDs ORDER BY ID DESC LIMIT 1"
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        c.execute(sql_string)
        data = c.fetchall()
        conn.close()
        lastID = data[0]
        return lastID[0]

    def get_user_from_tag_id(self, tag_id, only_name):
        conn = sqlite3.connect(self.db_full_f_name)
        c = conn.cursor()
        sql_string = "SELECT person_id FROM tagIDs WHERE ID = " + str(tag_id)
        c.execute(sql_string)
        data = c.fetchall()

        if len(data) == 0:
            person_id = -1
        else:
            person_id = data[0][0]

        if person_id > -1:
            conn.row_factory = dict_factory
            c = conn.cursor()
            search_string = " WHERE ID=" + str(person_id)
            fields = "*"
            sql_string = 'SELECT ' + fields + ' FROM users ' + search_string
            c.execute(sql_string)
            data = c.fetchall()

            if only_name:
                return data[0].get('user_name') + ' ' + data[0].get('user_surname')


            return data
        else:
            return 'not in db'
        conn.close()



    def log_tag(self, tagMD5, deviceMAC):

        tagID = self.tagExists(tagMD5)
        if not tagID:
            tagID = self.insertTag(tagMD5)

        deviceID = self.deviceExists(deviceMAC)
        if not deviceID:
            deviceID = self.insertDevice(deviceMAC)


        sql_string2 = 'INSERT INTO taglogs (tag_id, tag_timestamp, tag_device_ID' \
                     ') VALUES (' +  str(tagID) + ',' + self.get_gmt_ts() + ',' +  str(deviceID) + ')'
        self.execute(sql_string2)
        user = self.get_user_from_tag_id(tagID, 1)
        return user

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
        table_name = 'divisions'

        self.create_table(table_name)
        columns = ["division_organisation_ID INTEGER DEFAULT ''",
                   "division_name TEXT DEFAULT ''"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'organisation'

        self.create_table(table_name)
        columns = ["organisation_name TEXT DEFAULT ''"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'taglogs'

        self.create_table(table_name)
        columns = ["tag_ID INTEGER DEFAULT ''",
                   "tag_timestamp INTEGER DEFAULT ''",
                   "tag_lat INTEGER DEFAULT ''",
                   "tag_lon INTEGER DEFAULT ''",
                   "tag_qr_scanned INTEGER DEFAULT ''",
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

        # ********************************************************
        table_name = 'startups'

        self.create_table(table_name)
        columns = ["startup_device_ID INTEGER DEFAULT -1",
                   "startup_SSID TEXT DEFAULT ''",
                   "startup_coldstart INTEGER DEFAULT -1",
                   "startup_timestamp INTEGER DEFAULT ''"]

        self.insert_columns(table_name, columns)


        # ********************************************************
        table_name = 'admins'

        self.create_table(table_name)
        columns = ["admin_user_ID INTEGER DEFAULT ''",
                   "admin_can_edit_users INTEGER DEFAULT 0",
                   "admin_can_assign_devices INTEGER DEFAULT 0",
                   "admin_is_god INTEGER DEFAULT 0",
                   "admin_external_ID TEXT DEFAULT ''",
                   "admin_google_ID TEXT DEFAULT ''",
                   "admin_picture TEXT DEFAULT ''",
                   "admin_entry_date INTEGER DEFAULT ''"]

        self.insert_columns(table_name, columns)

        # ********************************************************
        table_name = 'admin_devices'

        self.create_table(table_name)
        columns = ["admin_ID INTEGER DEFAULT -1",
                   "device_ID INTEGER DEFAULT 0",
                   "entry_date INTEGER DEFAULT ''",
                   "granted_by_ID INTEGER DEFAULT -1"]

        self.insert_columns(table_name, columns)


        # ********************************************************
        table_name = 'events'

        self.create_table(table_name)
        columns = ["event_name TEXT DEFAULT, "
                    "event_admin_ID INTEGER DEFAULT -1",
                   "entry_date INTEGER DEFAULT ''",
                   "event_start_date INTEGER DEFAULT ''",
                   "event_end_date INTEGER DEFAULT ''",
                   "event_url INTEGER DEFAULT ''"]


        self.insert_columns(table_name, columns)

        table_name = 'registrations'

        self.create_table(table_name)
        columns = ["registration_event_ID INTEGER DEFAULT -1",
                   "registration_user_ID INTEGER DEFAULT ''",
                   "registration_entry_date INTEGER DEFAULT ''"
                   ]


        self.insert_columns(table_name, columns)