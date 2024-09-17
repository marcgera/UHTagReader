import tagdbmysql
db = tagdbmysql.tagdbmysql()

import xlrd

workbook = xlrd.open_workbook(r"C:\Users\lucp2284\Downloads\lijst 1stemaster 2024.xls")
sheet = workbook.sheet_by_index(0)  # Access first sheet


first_row = 1
cols = 4
group_id = 22

now_nr = first_row

cell_value = sheet.cell_value(now_nr, 0)  # Access cell A1

while cell_value:
    user_external_ID = sheet.cell_value(now_nr, 0)
    user_surname = sheet.cell_value(now_nr, 1)
    user_name = sheet.cell_value(now_nr, 2)
    user_email = sheet.cell_value(now_nr, 3)
    db.add_group_member_by_email(group_id, user_email, user_name, user_surname, user_external_ID )
    print(str(now_nr) + ' ' + user_email)

    now_nr = now_nr + 1



