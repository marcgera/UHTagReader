import mysql.connector
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

class tagdbmysql(object):

    def __init__(self):

        print('Connecting to mySQL db...')
        self.connection = mysql.connector.connect(
            host="/cloudsql/uhtagtools:europe-west9:revaldb",
            user="quickstart-user",
            passwd="revaldb_user##%%2+",
            database="uhtagtool"
        )

        if self.connection:
            print("Connected Successfully")
        else:
            print("Connection Not Established")


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
        strdump = 'Needs implementation'
        return strdump

    def createJson(self, result):
        out = list()
        for row in result:
            out.append(row)
        return out

    def selectDict(self, sql_string):
        my_cursor = self.connection.cursor(dictionary=True)
        my_cursor.execute(sql_string)
        result = self.createJson(my_cursor.fetchall())
        return result

    def select(self, sql_string):
        my_cursor = self.connection.cursor()
        my_cursor.execute(sql_string)
        return my_cursor.fetchall()

    def getUsers(self, select_field, selection):
        sql_string = "SELECT * FROM users WHERE " + select_field + " LIKE '" + selection + "'"
        return self.selectDict(sql_string)

    def getMostRecentLogEntry(self, device_id):
        fields = "user_name, user_surname, user_email, tag_id, tag_timestamp, users.ID "
        table = "(taglogs JOIN tagIDs on taglogs.tag_ID=tagIDs.ID) LEFT JOIN users on tagIDs.user_id=users.ID"
        sql_string = "SELECT " + fields + " FROM " + table + " WHERE tag_device_ID=" + str(device_id) + \
                     " ORDER BY tag_timestamp DESC LIMIT 1"
        result = self.selectDict(sql_string)[0]
        logged_time_stamp = result["tag_timestamp"]
        now_time_stamp = int(self.get_gmt_ts())

        if now_time_stamp-logged_time_stamp > 200:
            return "No recent (last 2 minutes) log entry found for device ID" + str(device_id)
        else:
            return self.selectDict(sql_string)[0]

    def get_base_name(self):
        splitted = self.db_f_name.split('.')
        return splitted[0]

    def get_name(self):
        return self.db_f_name

    def execute(self, sql_string):
        cursor = self.connection.cursor()
        cursor.execute(sql_string)
        self.connection.commit()
        return

    def registerUser(self, user_name , user_surname, user_email, event_id):
        sqlString = 'SELECT *  FROM Users WHERE LOWER(user_email) LIKE LOWER("' + user_email + '")'
        result = self.selectDict(sqlString)
        if result.__len__() == 0:
            sql_string = 'INSERT INTO Users (user_name, User_surname, user_email) VALUES (' + \
                '"' + user_name + '","' + '"' + user_surname + '","' + '"' + user_email + '")'
            self.execute(sql_string)
            sql_string = 'SELECT ID FROM users WHERE user_email="' + user_email


    def get_logs(self, start_time, end_time, device_id):


        search_string = " WHERE tag_timestamp >  " + str(start_time) + \
                            " AND tag_timestamp< " + str(end_time) + \
                            " AND tag_device_ID =" + device_id

        fields = "tagIDs.ID AS tagID, tag_timestamp, user_name, user_surname, " \
                 "users.ID as user_id, user_email, user_external_ID "
        sql_string = 'SELECT ' + fields + ' FROM (taglogs JOIN tagIDs on tagIDs.ID=taglogs.tag_ID) ' \
                                          'LEFT JOIN users on users.ID = tagIDs.user_id ' + search_string
        sql_string = sql_string + ' ORDER BY tag_timestamp ASC'

        data = self.selectDict(sql_string)

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
        search_string = ""
        fields = "device_name, ID"
        sql_string = 'SELECT ' + fields + ' FROM devices ' + search_string
        return self.selectDict(sql_string)

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
            data = self.selectDict(sql_string)
            lastID = data[0][0]

        sql_string = 'UPDATE tagIDs SET user_id=' + str(lastID) + ' WHERE ID=' + tag_id
        self.execute(sql_string)
        return 'http200OK'

    def update_user(self, ID, user_name, user_surname, user_external_id, user_email):
        sql_string = 'UPDATE users SET user_name="' + user_name + '", user_surname="' + user_surname + '", ' + \
            ' user_external_ID="' + user_external_id + '", user_email="' + user_email + '" WHERE ID=' + ID
        self.execute(sql_string)
        return 'http200OK'

    def deviceExists(self, deviceMAC):
        sql_string = "SELECT ID FROM devices WHERE device_mac = '" + deviceMAC + "'"
        data = self.select(sql_string)
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
        data = self.select(sql_string)
        lastID = data[0]
        return lastID['ID']

    def tagExists(self, tagMD5):
        sql_string = "SELECT ID FROM tagIDs WHERE tagMD5 = '" + tagMD5 + "'"
        data = self.selectDict(sql_string)

        if len(data) == 0:
            return 0
        else:
            return data[0]['ID']

    def insertTag(self, tagMD5):

        sql_string = 'INSERT INTO tagIDs (tagMD5, entry_date, user_id)' \
                     'VALUES ("' + tagMD5 + '",' + self.get_gmt_ts() + ',-1)'
        self.execute(sql_string)

        sql_string = "SELECT  ID FROM tagIDs ORDER BY ID DESC LIMIT 1"
        data = self.select(sql_string)
        lastID = data[0]
        return lastID[0]

    def get_user_from_tag_id(self, tag_id, only_name):

        sql_string = "SELECT user_id FROM tagIDs WHERE ID = " + str(tag_id)
        data = self.select(sql_string)

        if len(data) == 0:
            user_id = -1
        else:
            user_id = data[0][0]

        if user_id > -1:

            search_string = " WHERE ID=" + str(user_id)
            fields = "*"
            sql_string = 'SELECT ' + fields + ' FROM users ' + search_string

            data = self.selectDict(sql_string)


            if only_name:
                return data[0].get('user_name') + ' ' + data[0].get('user_surname')

            return data
        else:
            return 'not in db'


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













