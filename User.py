import tagdbmysql

db = tagdbmysql.tagdbmysql()
class User():

    def __init__(self, uniqueRef, user_name ='', user_surname='', user_picture_url=''):

        if (type(uniqueRef) is str):
            if uniqueRef.isnumeric():
                uniqueRef = int(uniqueRef)

        self.ID = -1
        self.id = ''
        self.name = ''
        self.surname = ''
        self.is_authenticated = False
        self.session_ID = -1
        self.is_admin = False
        self.user_entry_date = 0
        self.user_session_ID = -1
        self.is_active = True
        self.is_anonymous = False
        self.external_ID = ''
        self.user_picture_url = user_picture_url

        if (type(uniqueRef) is str):
            sql_string = 'SELECT  * FROM users WHERE user_email="' + uniqueRef + '"'
            result = db.selectDict(sql_string)

            if result:
                result = result[0];
                self.ID = result.get('ID')
                self.name = result.get('user_name')
                self.surname = result.get('user_surname')
                self.user_entry_date = result.get('user_entry_date')
                self.is_authenticated = True
                self.ID = result.get('ID')
                self.external_ID = result.get('user_external_ID')
                self.email = uniqueRef

            else:
                self.entry_date = db.get_gmt_ts()
                sql_string = 'INSERT INTO users (user_name, user_surname, user_email, user_entry_date, user_picture_url) ' \
                             'VALUES ("' +  \
                                user_name + '","' + user_surname + '","' + uniqueRef + '", ' + str(self.entry_date) + ',"' + user_picture_url + '")'
                self.name = user_name
                self.surname = user_surname

                res = db.execute(sql_string)
                sql_string = 'SELECT  ID FROM users WHERE user_email="' + uniqueRef + '"'
                result = db.selectDict(sql_string)
                result = result[0];
                self.is_authenticated = True
                self.ID = result.get('ID')

        else:
            sql_string = "SELECT  * FROM users WHERE ID=" + str(uniqueRef)
            result = db.selectDict(sql_string)

            if result:
                result = result[0];
                self.ID = result.get('ID')
                self.name = result.get('user_name')
                self.surname = result.get('user_surname')
                self.surname = result.get('user_surname')
                self.user_entry_date = result.get('user_entry_date')
                self.is_authenticated = True
                self.ID = result.get('ID')
                self.external_ID = result.get('user_external_ID')
                self.email = result.get('user_email')

        self.is_admin = False
        self.can_edit_users = False
        self.can_assign_devices = False
        self.is_god = False


        sql_string = 'SELECT * FROM admins WHERE admin_user_ID=' + str(self.ID)
        result = db.selectDict(sql_string)
        if len(result) > 0:
            result = result[0];
            self.is_admin = True
            if result["admin_can_edit_users"] == 1:
                self.can_edit_users = True
            if result["admin_can_assign_devices"] == 1:
                self.can_assign_devices = True
            if result["admin_is_god"] == 1:
                self.is_god = True

    def __str__(self):
        return self.email + ' - ' + self.name + ' ' + self.surname + ' - ' + str(self.user_entry_date)

    def set_user_session_ID(self, session_ID):
        self.session_ID = session_ID

    def get_id(self):
        return str(self.ID)

    def email(self):
        return str(self.email)

    def name(self):
        return str(self.name)

    def surname(self):
        return str(self.surname)

    def is_anonymous(self):
        return self.is_anonymous

    def is_authenticated(self):
        return self.is_authenticated

    def is_active(self):
        return self.is_active

    def external_ID(self):
        return self.external_ID

    def is_admin(self):
        return self.is_admin()

    def get_JSON(self):
        return self.__dict__



#newUser = User('marc.geraerts@gmail.com','Marc','Geraerts')
#print(newUser)