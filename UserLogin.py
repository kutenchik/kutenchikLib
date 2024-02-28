class UserLogin():
    def fromDb(self,user_id,db):
        self.__user=db.getUser(user_id)
        return self
    def create(self,user):
        self.__user=user
        return self
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.__user[0])
    def get_username(self):
        return str(self.__user[1])
    def get_profilePic(self):
        if str(self.__user[4])=='None':
            return 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Circle-icons-profile.svg/1200px-Circle-icons-profile.svg.png'
        else:
            return str(self.__user[4])
    def get_description(self):
        return str(self.__user[5])
    def get_status(self):
        return str(self.__user[6])
    def get_exp(self):
        return str(self.__user[7])