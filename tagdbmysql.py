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
import report1
import report2

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

    def getMostRecentLogEntries(self):

        timeBackInSeconds = 240
        now_time_stamp = int(self.get_gmt_ts())
        as_of_timeStamp = str(now_time_stamp - timeBackInSeconds)

        fields = ("user_email, "
                  "tag_id, "
                  "tag_timestamp, "
                  "users.ID as userID, "
                  "user_external_ID, "
                  "taglogs.ID, "
                  "tag_device_ID")

        table = "(taglogs JOIN tagIDs on taglogs.tag_ID=tagIDs.ID) LEFT JOIN users on tagIDs.user_id=users.ID"
        sql_string = ("SELECT " + fields + " FROM " + table +
                      " WHERE tag_timestamp>=" + as_of_timeStamp +
                      " ORDER BY tag_timestamp")
        result = self.selectDict(sql_string)

        return result

    def disconnectTagFromUser(self, tagID):
        sql_string = "UPDATE  tagIDs SET user_ID=-1 WHERE ID = " + str(tagID)
        result  = self.execute(sql_string)
        return result

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

    def registerUser(self, user_name, user_surname, user_email, event_id):
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



        return data

    def getMostRecentLogEntry(self, device_id):
        fields = ("user_name, "
                  "user_surname, "
                  "user_email, "
                  "tag_id, "
                  "tag_timestamp, "
                  "users.ID, "
                  "user_external_ID, "
                  "taglogs.ID, "
                  "tag_qr_scanned ")

        table = "(taglogs JOIN tagIDs on taglogs.tag_ID=tagIDs.ID) LEFT JOIN users on tagIDs.user_id=users.ID"
        sql_string = ("SELECT " + fields + " FROM " + table +
                      " WHERE tag_device_ID=" + str(device_id) +
                     " ORDER BY tag_timestamp DESC LIMIT 1")
        result = self.selectDict(sql_string)
        if not result:
            return "No recent log entry found for device ID " + str(device_id)

        result = self.selectDict(sql_string)[0]

        log_id = result["ID"]
        sql_string_qr = "UPDATE taglogs SET tag_qr_scanned = 1 WHERE tag_device_ID=" + str(device_id)
        self.execute(sql_string_qr)

        logged_time_stamp = result["tag_timestamp"]
        now_time_stamp = int(self.get_gmt_ts())

        if now_time_stamp-logged_time_stamp > 150:
            return ("No recent (last 2 minutes) log entry found for device ID " + str(device_id) +
                    ". TSDelta=" + str(now_time_stamp-logged_time_stamp))
        else:
            return result

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


    def get_logs(self, user_id, start_date, end_date, device_id):

        #If user_id < 0 -> any user
        # If device_id < 0 -> any device

        if type(user_id) == int:
            user_id = str(user_id)

        if type(device_id) == int:
            device_id = str(device_id)

        selectString = 'SELECT users.user_name, users.user_surname, users.user_email, taglogs.tag_timestamp'
        fromString = ' FROM (uhtagtool.taglogs  inner join tagIDs on taglogs.tag_ID=tagIDs.ID) inner join users on tagIDs.user_id=users.ID'
        whereString = ' where taglogs.tag_device_ID=$device_ID and tag_timestamp>$start_date AND tag_timestamp<$end_date AND users.ID = $user_ID'
        orderString = ' order by user_surname, user_name, taglogs.tag_timestamp'

        SQLString = selectString + fromString + whereString + orderString
        SQLString = str.replace(SQLString, '$start_date', start_date)
        SQLString = str.replace(SQLString, '$end_date', end_date)

        if int(user_id)>=0:
            SQLString = str.replace(SQLString, '$user_ID', user_id)
        else:
            SQLString = str.replace(SQLString, ' AND users.ID = $user_ID', '')

        if int(device_id)>=0:
            SQLString = str.replace(SQLString,'$device_ID',device_id)
        else:
            SQLString = str.replace(SQLString, ' taglogs.tag_device_ID=$device_ID and', '')

        data = self.selectDict(SQLString)

        return  data

    def get_logs_per_group(self,group_id, start_date, end_date, device_id ):

        if type(group_id) == int:
            group_id = str(group_id)

        if type(device_id) == int:
            device_id = str(device_id)

        selectString = 'select user_id, user_name, user_surname, user_email, user_external_ID, tag_timestamp'
        fromString = ' from (taglogs JOIN tagIDs on taglogs.tag_ID = tagIDs.ID) join users on users.ID = tagIDs.user_id'
        whereString = (' where taglogs.tag_device_ID=$device_ID '
                       ' and tag_timestamp>$start_date'
                       ' and tag_timestamp<$end_date'
                       ' and user_ID in (select group_members.group_member_user_ID FROM group_members WHERE group_member_group_ID = $group_ID)')
        orderString = ' order by user_surname, user_name, taglogs.tag_timestamp'

        SQLString = selectString + fromString + whereString + orderString
        SQLString = str.replace(SQLString, '$start_date', start_date)
        SQLString = str.replace(SQLString, '$end_date', end_date)
        SQLString = str.replace(SQLString, '$group_ID', group_id)

        if int(device_id)>=0:
            SQLString = str.replace(SQLString,'$device_ID',device_id)
        else:
            SQLString = str.replace(SQLString, ' taglogs.tag_device_ID=$device_ID and', '')

        data_logs = self.selectDict(SQLString)

        SQLString = ("select group_member_user_ID as ID, user_name, user_surname, user_external_ID, user_email "
                     " from group_members join users on users.ID=group_members.group_member_user_ID"
                     " where group_member_group_id = $group_ID order by user_surname, user_name")
        SQLString = str.replace(SQLString, '$group_ID', group_id)

        data_members = self.selectDict(SQLString)

        out = {'logs': data_logs, 'members' : data_members}

        return  out

    def get_logs_excel(self, start_time, end_time, device_id):


        search_string = " WHERE tag_timestamp >  " + str(start_time) + \
                            " AND tag_timestamp< " + str(end_time) + \
                            " AND tag_device_ID =" + device_id

        fields = "tagIDs.ID AS tagID, tag_timestamp, user_name, user_surname, " \
                 "users.ID as user_id, user_email, user_external_ID "
        sql_string = 'SELECT ' + fields + ' FROM (taglogs JOIN tagIDs on tagIDs.ID=taglogs.tag_ID) ' \
                                          'LEFT JOIN users on users.ID = tagIDs.user_id ' + search_string
        sql_string = sql_string + ' ORDER BY tag_timestamp ASC'

        data = self.selectDict(sql_string)

        try:
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
        except:
            print("Workbook creation failed")

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

    def get_device_id(self, deviceMAC):

        sql_string = "SELECT ID, device_name FROM devices WHERE device_mac='" + deviceMAC + "'"
        result = self.selectDict(sql_string)

        if len(result) == 0:
            return 'ID Not found'
        else:
            return str(result[0]['ID']) + ";" + str(result[0]['device_name'])

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

    def get_admins(self):
        sql_string = "SELECT * FROM uhtagtool.admins join users on users.ID = admins.admin_user_ID;"
        data = self.selectDict(sql_string)
        return data

    def insert_admin(self, user_ID):
        insert_sql_string = ("insert into admins (admins.admin_can_assign_devices, admins.admin_can_edit_users,  "
                             "admins.admin_is_god, admins.admin_entry_date, admins.admin_user_ID) values ")
        values_sql = '(0,0,0,' + self.get_gmt_ts() + ',' + str(user_ID) + ')'

        self.execute(insert_sql_string + values_sql)
        return 'http200OK'

    def insert_group(self, _name, _owner_ID, _is_public):
        insert_sql_string = "insert into uhtagtool.groups (group_name, group_owner_ID, group_created) values "
        values_sql = "('" + _name + "'," +  str(_owner_ID) + "," + self.get_gmt_ts() + ")"
        self.execute(insert_sql_string + values_sql)
        return 'http200OK'

    def edit_group(self, group_ID, new_name, new_is_public, new_is_editable):
        sql_string = ("UPDATE uhtagtool.groups SET group_name='" + new_name +
                    "', group_is_public=" + new_is_public +
                    ", group_is_editable=" + new_is_editable +
                    " WHERE ID=" + group_ID)
        self.execute(sql_string)
        return 'http200OK'

    def remove_group(self, _group_ID, user_ID):
        sql_string = "SELECT group_owner_id FROM uhtagtool.groups WHERE ID=" + str(_group_ID)
        result = self.selectDict(sql_string)
        owner_ID = result[0]['group_owner_id']
        if owner_ID == int(user_ID):
            sql_string = "DELETE FROM uhtagtool.group_members WHERE group_member_group_ID=" + _group_ID
            self.execute(sql_string)
            sql_string = "DELETE FROM uhtagtool.groups WHERE ID=" + _group_ID
            self.execute(sql_string)
            return 'http200OK'
        else:
            return 'Unauthorized. Not owner of group'

    def add_group_member(self, group_ID, user_ID):
        sql_string = "select ID from group_members WHERE group_member_group_ID = %group_ID% and group_member_user_ID = %user_ID%"
        sql_string = sql_string.replace('%group_ID%', str(group_ID))
        sql_string = sql_string.replace('%user_ID%', str(user_ID))
        ID = self.selectDict(sql_string)
        #If not already in list
        if ID.__len__() == 0:
            insert_sql_string = "insert into uhtagtool.group_members (group_member_user_ID, group_member_group_ID) values "
            values_sql = "(" + str(user_ID) + "," + str(group_ID) + ")"
            self.execute(insert_sql_string + values_sql)
        return self.get_group_members(group_ID)

    def add_group_member_by_email(self, group_id, user_email, user_name, user_surname, user_external_ID):
        sql_string = "select ID from users where user_email='%user_email%'"
        sql_string = sql_string.replace('%user_email%', user_email)
        res = self.selectDict(sql_string)
        if not res:
            sql_string = ("insert into users (user_name, user_surname, user_email, user_external_ID, user_entry_date) "
                          "values ('%user_name%','%user_surname%', '%user_email%', '%user_external_ID%',%user_entry_date%)")
            sql_string = sql_string.replace('%user_name%', user_name)
            sql_string = sql_string.replace('%user_surname%', user_surname)
            sql_string = sql_string.replace('%user_email%', user_email)
            sql_string = sql_string.replace('%user_external_ID%', user_external_ID)
            sql_string = sql_string.replace('%user_entry_date%', self.get_gmt_ts())
            self.execute(sql_string)
            self.add_group_member_by_email(group_id, user_email, user_name, user_surname, user_external_ID)
        else:
            self.add_group_member(group_id, res[0]['ID'])
        return 'http200OK'

    def remove_group_member(self,group_member_ID):
        sql_string = "SELECT group_member_group_ID FROM group_members WHERE ID=" + str(group_member_ID)
        data = self.selectDict(sql_string)
        group_ID = data[0]["group_member_group_ID"]
        sql_string = "DELETE FROM group_members WHERE ID=" + group_member_ID
        self.execute(sql_string)
        return self.get_group_members(group_ID)

    def insert_event(self, _name, _owner_ID, _is_public):
        insert_sql_string = "insert into events (event_name, event_owner_ID, event_created) values "
        values_sql = "('" + _name + "'," + str(_owner_ID) + "," + self.get_gmt_ts() + ")"
        self.execute(insert_sql_string + values_sql)
        return 'http200OK'

    def edit_event(self, event_ID, new_name, new_is_public, new_is_editable, event_start_datetime, event_end_datetime):
        sql_string = ("UPDATE events SET event_name='" + new_name +
                      "', event_is_public=" + new_is_public +
                      ", event_is_editable=" + new_is_editable +
                      ", event_start_datetime=" + event_start_datetime +
                      ", event_end_datetime=" + event_end_datetime +
                      " WHERE ID=" + event_ID)
        self.execute(sql_string)
        return 'http200OK'

    def remove_event(self, _event_ID, user_ID):
        sql_string = "SELECT event_owner_ID FROM events WHERE ID=" + str(_event_ID)
        result = self.selectDict(sql_string)
        owner_ID = result[0]['event_owner_ID']
        if owner_ID == int(user_ID):
            sql_string = "DELETE FROM event_members WHERE event_member_event_ID=" + _event_ID
            self.execute(sql_string)
            sql_string = "DELETE FROM events WHERE ID=" + _event_ID
            self.execute(sql_string)
            return 'http200OK'
        else:
            return 'Unauthorized. Not owner of events'

    def add_event_member(self, event_ID, user_ID):
        sql_string = "select ID from event_members WHERE event_member_event_ID = %event_ID% and event_member_user_ID = %user_ID%"
        sql_string = sql_string.replace('%event_ID%', str(event_ID))
        sql_string = sql_string.replace('%user_ID%', str(user_ID))
        ID = self.selectDict(sql_string)
        # If not already in list
        if ID.__len__() == 0:
            insert_sql_string = "insert into event_members (event_member_user_ID, event_member_event_ID) values "
            values_sql = "(" + str(user_ID) + "," + str(event_ID) + ")"
            self.execute(insert_sql_string + values_sql)
        return self.get_event_members(event_ID)

    def add_event_member_by_email(self, group_id, user_email, user_name, user_surname, user_external_ID):
        sql_string = "select ID from users where user_email='%user_email%'"
        sql_string = sql_string.replace('%user_email%', user_email)
        res = self.selectDict(sql_string)
        if not res:
            sql_string = ("insert into users (user_name, user_surname, user_email, user_external_ID, user_entry_date) "
                          "values ('%user_name%','%user_surname%', '%user_email%', '%user_external_ID%',%user_entry_date%)")
            sql_string = sql_string.replace('%user_name%', user_name)
            sql_string = sql_string.replace('%user_surname%', user_surname)
            sql_string = sql_string.replace('%user_email%', user_email)
            sql_string = sql_string.replace('%user_external_ID%', user_external_ID)
            sql_string = sql_string.replace('%user_entry_date%', self.get_gmt_ts())
            self.execute(sql_string)
            self.add_event_member_by_email(group_id, user_email, user_name, user_surname, user_external_ID)
        else:
            self.add_event_member(group_id, res[0]['ID'])
        return 'http200OK'

    def remove_event_member(self,event_member_ID):
        sql_string = "SELECT event_member_group_ID FROM event_members WHERE ID=" + str(event_member_ID)
        data = self.selectDict(sql_string)
        group_ID = data[0]["event_member_event_ID"]
        sql_string = "DELETE FROM event_members WHERE ID=" + event_member_ID
        self.execute(sql_string)
        return self.get_event_members(group_ID)

    def get_events(self, current_user_ID, include_public):

        sqlString = ('SELECT \
                users.user_name, \
                users.user_surname, \
                events.event_name, events.ID, \
                event_member_event_ID, \
                event_owner_id, \
                event_is_public, \
                event_is_editable, \
                event_created, \
                event_start_datetime, \
                event_end_datetime, \
                COUNT(event_members.event_member_event_ID) AS nrOfMembers \
            FROM \
                events \
                LEFT JOIN event_members ON (event_members.event_member_event_ID = events.ID) \
                LEFT JOIN users ON users.ID = events.event_owner_id \
            WHERE events.ID IN \
                (select ID from events WHERE events.event_owner_id = %current_user_ID% \
                %include_public%) \
            GROUP BY \
                events.event_name, \
                events.ID, \
                event_member_event_ID, \
                event_owner_ID, \
                users.user_name, \
                users.user_surname \
            ORDER BY \
                events.event_name;')

        sqlString = sqlString.replace('%current_user_ID%',current_user_ID)
        if include_public.lower().capitalize() == "True":
            sqlString = sqlString.replace('%include_public%', 'OR events.event_is_public = 1')
        else:
            sqlString = sqlString.replace('%include_public%', '')

        data = self.selectDict(sqlString)

        return data

    def getLastAddedIDFromTable(self, _table):
        sql_string = "SELECT ID FROM "  + _table + " ORDER BY ID DESC LIMIT 1;"
        data = self.selectDict(sql_string)
        if data:
            return str(data[0]['ID'])
        else:
            return -1

    def get_event_members(self, event_ID):
        sql_string = (
                         "SELECT event_members.*, users.user_name, users.user_surname FROM event_members join users on users.ID = event_members.event_member_user_ID "
                         "WHERE event_member_event_ID = ") + str(event_ID) + " ORDER BY user_surname ASC"
        data = self.selectDict(sql_string)
        return data

    def get_event(self, event_ID):
        sql_string = "SELECT * FROM events WHERE ID=" + str(event_ID)
        data = self.selectDict(sql_string)
        return data


    def get_groups(self, current_user_ID, include_public):

        sqlString = ('SELECT \
                users.user_name, \
                users.user_surname, \
                uhtagtool.groups.group_name, uhtagtool.groups.ID, \
                group_member_group_ID, \
                group_owner_id, \
                COUNT(group_members.group_member_group_ID) AS nrOfMembers \
            FROM \
                uhtagtool.groups \
                LEFT JOIN group_members ON (group_members.group_member_group_ID = uhtagtool.groups.ID) \
                LEFT JOIN users ON users.ID = uhtagtool.groups.group_owner_id \
            WHERE uhtagtool.groups.ID IN \
                (select ID from uhtagtool.groups WHERE uhtagtool.groups.group_owner_id = %current_user_ID% \
                %include_public%) \
            GROUP BY \
                uhtagtool.groups.group_name, \
                uhtagtool.groups.ID, \
                group_member_group_ID, \
                group_owner_ID, \
                users.user_name, \
                users.user_surname \
            ORDER BY \
                uhtagtool.groups.group_name;')

        sqlString = sqlString.replace('%current_user_ID%',current_user_ID)
        if include_public.lower().capitalize() == "True":
            sqlString = sqlString.replace('%include_public%', 'OR uhtagtool.groups.group_is_public = 1')
        else:
            sqlString = sqlString.replace('%include_public%', '')

        data = self.selectDict(sqlString)

        return data

    def get_group_members(self, group_ID):
        sql_string = ("SELECT group_members.*, users.user_name, users.user_surname FROM group_members join users on users.ID = group_members.group_member_user_ID "
                      "WHERE group_member_group_ID = ") + str(group_ID) + " ORDER BY user_surname ASC"
        data = self.selectDict(sql_string)
        return data

    def get_group(self, group_ID):
        sql_string = "SELECT * FROM uhtagtool.groups WHERE ID=" + str(group_ID)
        data = self.selectDict(sql_string)
        return data

    def get_last_names(self, name_start):
        sql_string = 'SELECT user_name, user_surname, ID FROM users where user_surname like "' + name_start + '%"'
        data = self.selectDict(sql_string)
        names = []
        IDs = []
        out = []
        if len(data) > 0:
            for name in data:
                names.append(name.get('user_surname') + ' ' + name.get('user_name'))
                IDs.append(name.get('ID'))
            out = {"names":names, "IDs": IDs}

        return out

    def generateReportStyle1(self, user_id, start_time_stamp, stop_time_stamp, device_id):
        data = self.get_logs(user_id, start_time_stamp, stop_time_stamp, device_id)
        out = report1.report_all_users(data, True, True)
        return(out)

    def generateReportStyle2(self, group_id, start_time_stamp, stop_time_stamp, device_id):
        data = self.get_logs_per_group(group_id, start_time_stamp, stop_time_stamp, device_id)
        out = report2.create_group_report(data, True)
        return(out)









