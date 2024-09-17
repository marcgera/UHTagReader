from datetime import datetime, timedelta
import xlsxwriter
def is_date_the_same(entry0, entry1):

    tsCurrent = str(entry0.get('tag_timestamp'))
    tsNext = str(entry1.get('tag_timestamp'))

    date0 = tsCurrent[0:8]
    date1 = tsNext[0:8]

    if date0 == date1:
        return True
    else:
        return False

def get_date_str(timestamp):
    months_dict = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    if type(timestamp) == int:
        timestamp = str(timestamp)

    year = timestamp[0:4]
    month = months_dict.get(int(timestamp[4:6]))
    day = timestamp[6:8]

    date_str = day + '-' + month + '-' + year

    return date_str

def get_time_str(timestamp, include_seconds = False):

    if type(timestamp) == int:
        timestamp = str(timestamp)

    hh = timestamp[8:10]
    mm = timestamp[10:12]
    ss = timestamp[12:14]

    if include_seconds:
        time_str = hh + ':' + mm + ':' + ss
    else:
        time_str = hh + ':' + mm

    return time_str

def get_day_of_the_week(timestamp):
    date_str = get_date_str(timestamp)
    date_obj = datetime.strptime(date_str, '%d-%b-%Y')
    day_of_week = date_obj.strftime('%A')
    return  day_of_week

def is_same_day(date_time, time_stamp):
    if type(time_stamp) == int:
        time_stamp = str(time_stamp)

    daystr = get_date_str(time_stamp)
    date_str = 'dd-mmm-yyyy'  # Replace with your actual date string
    date_format = '%d-%b-%Y'
    date1 = datetime.strptime(daystr, date_format)
    same_day = (date1.year == date_time.year and
                date1.month == date_time.month and
                date1.day == date_time.day)
    return same_day

def get_all_days(data, col_sep_char = ';'):

    if len(data)>0:
        header_string = (data[0].get('user_name') + ' ' + data[0].get('user_surname') +
                         col_sep_char + data[0].get('user_email') + '\n\r')
    else:
        return ''
    date_str = 'dd-mmm-yyyy'  # Replace with your actual date string
    date_format = '%d-%b-%Y'
    epoch = datetime(1970, 1, 1)

    start_day = get_date_str(data[0].get('tag_timestamp'))
    end_day = get_date_str(data[-1].get('tag_timestamp'))
    date_start = datetime.strptime(start_day, date_format)
    date_end = datetime.strptime(end_day, date_format)

    current_date = date_start

    days_string = ''
    total_nr_of_days = 0
    while current_date <= date_end:

        formatted_date = current_date.strftime('%Y%m%d')
        lines = []
        for line in data:
            ts = line.get('tag_timestamp')
            if is_same_day(current_date, ts):
                lines.append(line)
        if len(lines) > 0:
            days_string = days_string + (get_ticks(lines) + '\n\r')
            total_nr_of_days = total_nr_of_days +1
        else:
            days_string = days_string + current_date.strftime('%A') + ';' + current_date.strftime('%d-%b-%Y') + '\n\r'

        current_date += timedelta(days=1)
    header_string = header_string + 'Number of scan days: ' + str(total_nr_of_days) + '\n\r'

    return header_string + days_string


def get_tick_days(data, col_sep_char = ';'):

    if len(data)>0:
        header_string = (data[0].get('user_name') + ' ' + data[0].get('user_surname') +
                         col_sep_char + data[0].get('user_email') + '\n\r')
    else:
        return ''

    i = 0
    days_string = ''

    total_nr_of_days = 0
    while i<len(data)-1:
        total_nr_of_days = total_nr_of_days + 1
        lines_list = [];
        line = data[i]
        lines_list.append(line)
        same_day_found = False
        for j in range(i+1,len(data)):
            if is_date_the_same(line, data[j]):
                lines_list.append(data[j])
                same_day_found = True
                i = j;
            else:
                i = j;
                break
        if not same_day_found:
            i=i+1
        days_string = days_string + get_ticks(lines_list, col_sep_char) + '\n\r'
    header_string = header_string + 'Number of scan days; ' + str(total_nr_of_days) + '\n\r'
    return header_string + days_string

def generate_excel(out_string):

        now = datetime.now()
        timestamp = now.strftime('%Y%m%d%H%M%S')

        filename = f'static/downloads/{timestamp}_report.xlsx'

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, 0, 35)
        worksheet.set_column(0, 0, 40)

        bold = workbook.add_format({'bold': True})
        gray = workbook.add_format({'font_color': 'blue'})

        row_nr = 0
        lines = out_string.split('\n\r')

        for line in lines:

            do_bold = False
            do_gray = False

            if '@' in line:
                do_bold = True

            if 'Saturday' in line:
                do_gray = True

            if 'Sunday' in line:
                do_gray = True

            cells = line.split(';')
            col_nr = 0
            for cell in cells:
                if do_bold:
                    worksheet.write(row_nr, col_nr, cell, bold)
                elif do_gray:
                    worksheet.write(row_nr, col_nr, cell, gray)
                else:
                    worksheet.write(row_nr, col_nr, cell)
                col_nr += 1

            row_nr += 1

        workbook.close()

        return (filename)


def get_ticks(lines_list, col_sep_char = ';'):

    ts = lines_list[0].get('tag_timestamp')
    out = get_day_of_the_week(ts) + ';' + get_date_str(ts)
    for line in lines_list:
        out = out + col_sep_char + get_time_str(line.get('tag_timestamp'))
    return out