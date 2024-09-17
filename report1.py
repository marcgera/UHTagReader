

from datetools import *
from datetime import datetime, timedelta



def report_all_users(data, include_not_badging_days = True, do_generate_excel = False):

    if len(data) == 0:
        return("Query contains no data, please adjust query parameters")

    lines = []
    out = ''

    lines.append(data[0])

    for i in range(len(data) - 1):
        if (data[i].get('user_email') == data[i+1].get('user_email')) :
            lines.append(data[i+1])
        else:
            if len(lines)> 1:
                out = out + get_all_days(lines)
                out = out + '\n\r'
                lines = []

    if len(lines)>0:
        out = out + get_all_days(lines)

    if do_generate_excel:
        out = generate_excel(out)

    return(out)




#data = db.get_logs(-1, '202402301010', '20240220074919', '46')
#out = report_all_users(data, True, True)
#print(out)










