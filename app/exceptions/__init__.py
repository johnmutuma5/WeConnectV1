class DuplicationError (Exception):
    '''
        class: DuplicationError
        raised: when storing duplicate data
    '''
    def __init__ (self, expression, msg):
        self.expression = expression
        self.msg = msg


class DataNotFoundError (Exception):
    '''
        class: DuplicationError
        raised: when storing duplicate data
    '''
    def __init__ (self, expression, msg):
        self.expression = expression
        self.msg = msg

class PermissionDeniedError (Exception):
    '''
        class: DuplicationError
        raised: when trying to read/write unauthorised data
    '''
    def __init__ (self, expression, msg):
        self.expression = expression
        self.msg = msg


class InvalidUserInputError (Exception):
    '''
        class: DuplicationError
        raised: when trying to read/write unauthorised data
    '''
    def __init__ (self, expression=None, msg=None):
        self.expression = expression
        self.msg = msg

class MissingDataError(InvalidUserInputError):
    '''
        class: MissingDataError
        raised: when there are blank fields in data
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
