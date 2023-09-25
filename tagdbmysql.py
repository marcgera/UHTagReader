

import decimal, datetime
import logging
import pymysql
import os
import platform
from datetime import datetime
import arrow
import xlsxwriter
import json

import sqlalchemy
from connect_connector import connect_with_connector
from connect_connector_auto_iam_authn import connect_with_connector_auto_iam_authn
from connect_tcp import connect_tcp_socket
from connect_unix import connect_unix_socket
from sqlalchemy.orm import Session




class tagdbmysql(object):

    def __init__(self):

        self.db = self.init_connection_pool()


    def init_connection_pool(self) -> sqlalchemy.engine.base.Engine:
        """Sets up connection pool for the app."""
        # use a TCP socket when INSTANCE_HOST (e.g. 127.0.0.1) is defined
        if os.environ.get("INSTANCE_HOST"):
            return connect_tcp_socket()

        # use a Unix socket when INSTANCE_UNIX_SOCKET (e.g. /cloudsql/project:region:instance) is defined
        if os.environ.get("INSTANCE_UNIX_SOCKET"):
            return connect_unix_socket()

        # use the connector when INSTANCE_CONNECTION_NAME (e.g. project:region:instance) is defined
        if os.environ.get("INSTANCE_CONNECTION_NAME"):
            # Either a DB_USER or a DB_IAM_USER should be defined. If both are
            # defined, DB_IAM_USER takes precedence.
            return (
                connect_with_connector_auto_iam_authn()
                if os.environ.get("DB_IAM_USER")
                else connect_with_connector()
            )

        raise ValueError(
            "Missing database connection type. Please define one of INSTANCE_HOST, INSTANCE_UNIX_SOCKET, or INSTANCE_CONNECTION_NAME"
        )


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

        with self.db.connect() as conn:
            res = conn.execute(sqlalchemy.text(sql_string)).fetchall()
            res_dict = [self.row2dict(r) for r in res]
        return res_dict

    def row2dict(self, row):
        d = {}
        counter = 0
        for field in row._fields:
            d[field] = row[counter]
            counter = counter +1
        return d


    def alchemyencoder(obj):
        """JSON encoder function for SQLAlchemy special classes."""
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)



    def getUsers(self, select_field, selection):
        sql_string = "SELECT * FROM users WHERE " + select_field + " LIKE '" + selection + "'"
        return self.selectDict(sql_string)

    def getMostRecentLogEntry(self, device_id):
        fields = "user_name, user_surname, user_email, tag_id, tag_timestamp, users.ID, user_external_ID "
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
        with self.db.connect() as conn:
            res = conn.execute(sqlalchemy.text(sql_string))
            conn.commit()
        return res

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
            lastID = data[0]['ID']

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
        data = self.selectDict(sql_string)
        if len(data) == 0:
            return 0
        else:
            return data[0]['ID']

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
        data = self.selectDict(sql_string)
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
        data = self.selectDict(sql_string)
        lastID = data[0]
        return lastID['ID']

    def get_user_from_tag_id(self, tag_id, only_name):

        sql_string = "SELECT user_id FROM tagIDs WHERE ID = " + str(tag_id)
        data = self.selectDict(sql_string)

        if len(data) == 0:
            user_id = -1
        else:
            user_id = data[0]['user_id']

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

    def log_reader_stat(self, stats):

        ts = self.get_gmt_ts()
        stat = stats["status"]
        mac = stats["mac"]
        sql_string = "SELECT ID FROM devices WHERE device_mac='"  + mac +"'"
        result = self.selectDict(sql_string)
        if len(result) == 0:
            device_id = self.insertDevice(mac)
        else:
            device_id = result[0]['ID']

        sql_string = 'INSERT INTO devicestats (stat, deviceID, timestamp) VALUES ("' + stat + '",' + str(device_id) + ',' + str(ts) + ')'
        self.execute(sql_string)

        ssids = stats["ssid"]
        if len(ssids) > 0:
            rssi = stats["rssi"]
            sql_string = "SELECT ID FROM devicestats ORDER BY ID DESC LIMIT 1"
            result = self.selectDict(sql_string)
            stat_id = result[0]['ID']
            for i in range(1,len(ssids)):
                sql_string = 'INSERT INTO SSIDs (SSIDName, SSIDRSSI, SSIDStatID) VALUES ("' + ssids[i] + '",' + str(rssi[i]) + ',' + str(stat_id) + ')'
                self.execute(sql_string)
        return stats















