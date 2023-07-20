import tagdbmysql

db = tagdbmysql.tagdb()
class Admin:

    def __init__(self):
        self.id = ''
        self.name = ''
        self.surname = ''
        self.email= ''
        self.profile_picture = ''
        self.is_active = False
        self.is_authenticated = False
        self.session_ID = ""

    def get_admin(self, email):
        sql_string = 'SELECT  * FROM admins WHERE admin_email="' + email + '"'
        result = db.selectDict(sql_string)

        if result:
            result = result[0];
            self.name = result.get('admin_name')
            self.surname = result.get('admin_surname')
            self.profile_picture = ''
            self.is_active = True
            self.is_authenticated = True
            self.ID = result.get('ID')

            return self
        else:
            self.is_active = False
            return self

    def is_active(self):
        return self.is_active
    def get_id(self):
        return self.ID
    def email(self):
        return self.email
    def name(self):
        return self.name


    def get_user_by_ID(self, ID):
        sql_string = 'SELECT  * FROM admins WHERE ID=' + str(ID)
        result = db.selectDict(sql_string)

        if result:
            result = result[0];
            self.name = result.get('admin_name')
            self.surname = result.get('admin_surname')
            self.profile_picture = ''
            self.email = result.get('admin_email')
            self.is_active = True
            self.is_authenticated = True
            self.ID = result.get('ID')

            return self
        else:
            self.is_active = False
            return self
    def is_authenticated(self):
        return self.is_authenticated
