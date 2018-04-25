from .. import store
from ...exceptions import InvalidUserInputError, MissingDataError
from ...helpers import inspect_data
import re

class User ():
    '''
    '''
    user_index = 0
    required_fields = ['username', 'mobile', 'first_name',
        'last_name', 'gender', 'email', 'password']

    @classmethod
    def create_user (cls, data):
        # inspect_data raises a MissingDataError for blank fields
        cleaned_data = inspect_data(cls.required_fields, data)
        new_user = cls (data)
        # assign to property fields
        cls.user_index = store.get_user_index()
        new_user.id = cls.user_index + 1
        new_user.username = data['username']
        new_user.mobile = data['mobile']
        new_user.email = data['email']
        return new_user

    def __init__ (self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.gender = data['gender']
        self._email = data['email']
        self._mobile = None
        self._id = None
        self._username = None
        self.password = data['password']

    @property
    def mobile (self):
        return self._mobile

    @mobile.setter
    def mobile (self, num):
        # should raise InvalidUserInputError with invalid chars in mobille numbers
        pattern = r"^[0-9]{12}$"
        match = re.match (pattern, num)
        if match:
            self._mobile = num
        else:
            raise InvalidUserInputError ("User::mobile.setter", "Invalid mobile number")

    # user id property
    @property
    def id (self):
        return self._id

    @id.setter
    def id (self, id):
        '''generates an 8-character commnet id e.g. USR00001
        '''
        # self.__class__.user_count += 1
        self._id = 'USR{:0>5}'.format(id)
        return

    @property
    def username (self):
        return self._username

    @username.setter
    def username (self, name):
        pattern = r'^[a-zA-Z_]+[\d\w]{3,}'
        match = re.search (pattern, name)
        if match:
            self._username = name
            return
        # assert 0, 'Invalid username'
        raise InvalidUserInputError ("User::namesetter", "Invalid username!")

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        email_pattern = r'^([\w\d_\.]+)@([\w\d]+)\.([\w\d]+\.?[\w\d]+)$'
        match = re.search(email_pattern, email)
        if match:
            self._email = email
            return
        raise InvalidUserInputError(msg='Invalid email')
