import tagdb

db = tagdb.tagdb()
class User:

    def __init__(self, email, user_name, user_surname):
        self.ID = ''
        self.name = ''
        self.surname = ''
        self.email= email
        self.profile_picture = ''
        self.is_authenticated = True
        self.session_ID = -1
        self.is_admin = False
        self.user_entry_date = 0
        self.user_session_ID = -1

        sql_string = 'SELECT  * FROM users WHERE user_email="' + email + '"'
        result = db.selectDict(sql_string)

        if result:
            result = result[0];
            self.ID = result.get('ID')
            self.name = result.get('user_name')
            self.surname = result.get('user_surname')
            self.profile_picture = ''
            self.user_entry_date = result.get('user_entry_date')

            self.ID = result.get('ID')

            sql_string = 'SELECT  * FROM users WHERE user_email="' + email + '"'
            result = db.selectDict(sql_string)


        else:
            self.entry_date = db.get_gmt_ts()
            sql_string = 'INSERT INTO users (user_name, user_surname, user_email, user_entry_date) ' \
                         'VALUES ("' +  \
                            user_name + '","' + user_surname + '","' + email + '", ' + str(self.entry_date) + ')'
            self.name = user_name
            self.surname = user_surname

            db.execute(sql_string)
            sql_string = 'SELECT  ID FROM users WHERE user_email="' + email + '"'
            result = db.selectDict(sql_string)
            result = result[0];
            self.ID = result.get('ID')

        sql_string = 'SELECT * FROM admins WHERE admin_user_ID=' + str(self.ID)
        result = db.selectDict(sql_string)
        if len(result) > 0:
            result = result[0];
            self.is_admin = True


    def __str__(self):
        return self.email + ' - ' + self.name + ' ' + self.surname + ' - ' + str(self.user_entry_date)

    def set_user_session_ID(self, session_ID):
        self.session_ID = session_ID




#newUser = User('marc.geraerts@gmail.com','Marc','Geraerts')
#print(newUser)