#Report based on groups
import json

import xlsxwriter
from datetools import *
from datetime import datetime, timedelta

import tagdbmysql
#db = tagdbmysql.tagdbmysql()

def create_group_report(data, do_generate_excel = True):

    if len(data) == 0:
        return("Query contains no data, please adjust query parameters")

    lines = ""
    out = ''

    all_members = data["members"]
    logs = data["logs"]

    for member in all_members:
        log_list_per_user = [];
        for log in logs:
            if log["user_id"] == member["ID"]:
                log_list_per_user.append(log)

        if log_list_per_user.__len__() == 0:
            entry = member["user_surname"] + " " + member["user_name"] + ";" + member["user_email"] + ";No entries"  + '\n\r'
        else:
            entry = '\n\r' + get_all_days(log_list_per_user)   + '\n\r'

        lines = lines + entry

    if do_generate_excel:
        lines = generate_excel(lines)

    return  lines

#data = db.get_logs_per_group(4, '202402301010', '20240220074919', '46')
#print(create_group_report(data))


