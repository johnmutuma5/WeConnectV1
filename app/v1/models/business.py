from .. import store
from ...exceptions import InvalidUserInputError
from ...helpers import inspect_data
import re

class Business ():
    '''
    Business template:
        methods:
            static:
                gen_id_string:
                    generates a valid business id given an integer
                    params: int::num
    '''
    business_index = 0
    required_fields = ["mobile", "name", "location"]


    @classmethod
    def create_business (cls, data, owner_id):
        # inspect_data raises a MissingDataError for blank fields
        cleaned_data = inspect_data(data, cls.required_fields)
        # assign to property fields
        cls.business_index = store.get_business_index ()
        new_business = cls (data, owner_id)
        new_business.mobile = data['mobile']
        new_business.name = data['name']
        new_business.id = cls.business_index + 1
        return new_business

    @staticmethod
    def gen_id_string (num):
        return 'BUS{:0>5}'.format(num)

    def __init__ (self, data, owner_id):
        self.owner_id = owner_id
        self.location = data ['location']
        self._id = None
        self._mobile = None
        self._name = None

    @property
    def mobile (self):
        return self._mobile

    @mobile.setter
    def mobile (self, contact):
        # should raise InvalidUserInputError with invalid chars in mobille numbers
        match = re.match (r"^[0-9]{12}$", contact)
        if match:
            self._mobile = contact
        else:
            raise InvalidUserInputError ("Business::mobile.setter",
                                            "Invalid mobile number")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, business_name):
        pattern = r'^([a-zA-Z]+( )?[\w\d_\.-]+( )?)+'
        match = re.match(pattern, business_name)
        if match:
            self._name = business_name
        else:
            raise InvalidUserInputError(msg='Invalid business name')

    @property
    def id (self):
        return self._id

    @id.setter
    def id (self, id):
        '''generates an 8-character commnet id e.g. BUS00001
        '''
        self._id = 'BUS{:0>5}'.format(id)
        return
