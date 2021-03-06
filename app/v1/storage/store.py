from ...exceptions import DuplicationError, DataNotFoundError, PermissionDeniedError
class StoreHelper ():
    def __init__ (self):
        ...

    @staticmethod
    def extract_business_data (business):
        business_data = {}
        fields = ["name", "owner_id", "location", "mobile", "id"]
        for field in fields:
            business_data[field] = getattr (business, field)

        return business_data

    @staticmethod
    def update_business (target_business, update_data):
        for key, value in update_data.items():
            setattr(target_business, key, update_data[key])


    @staticmethod
    def extract_review_info (review):
        review_info = {}
        fields = ["heading", "body", "author_id", "business_id", "id"]
        for field in fields:
            review_info[field] = getattr (review, field)

        return review_info

class Storage ():
    '''
    Simulates a database:
    Implemented with dicts for constant time access to data
        params: None
        fields:
            users: a dict of users (key:value) equivalent (username: user_obj)
            businesses: a dict o businesses (key:value) equivalent (businessname: business_obj)
            reviews: a dict o reviews (key:value) equivalent (reviewid: review_obj)
            tokens: a dict of tokens (key:value) equivalent (token_string: bearer_name)
        methods:
            add: adds any class of object
                params: obj
            add_user:
                params: user_obj
            add_business:
                params: business_obj
            add_review:
                params: review_obj

    '''
    users = {}
    businesses = {}
    reviews = {}
    counts = {
        'users': 0,
        'businesses': 0,
        'reviews': 0
    }
    tokens = {}

    def __init__ (self):
        self.clerk = StoreHelper ()


    def add (self, obj):
        obj_class = obj.__class__.__name__

        # get appropriate method to call: a switch-like dict operation
        _add = {
            "User": self.add_user,
            "Business": self.add_business,
            "Review": self.add_review
        }[obj_class]

        # call method with argument and return it's output
        return _add (obj)

    def add_review (self, review_obj):
        review_id = review_obj.id
        self.__class__.reviews[review_id] = review_obj
        # increment count of reviews ever stored
        self.__class__.counts['reviews'] += 1
        new_review = self.__class__.reviews[review_id]
        return 'SUCCESS: review heading:[{}] created!'.format(new_review.heading)


    def add_user (self, user_obj):
        users = self.__class__.users
        username = user_obj.username
        email = user_obj.email

        user_names = [name.lower() for name in users.keys()]
        emails = []
        for user in users.values():
            emails.append(user.email.lower())

        username_exists = username.lower() in user_names
        email_exists = email.lower() in emails

        if username_exists:
            raise DuplicationError ('Storage::add_user',
                'Username already exists')
        if email_exists:
            raise DuplicationError("Storage::add_user",
                'Email already exists')

        self.__class__.users[username.lower()] = user_obj
        # increment the cont of users ever stored
        self.__class__.counts['users'] += 1
        return 'SUCCESS: user {} created!'.format(username)


    def add_business (self, business_obj):
        businesses = self.__class__.businesses
        businessname = business_obj.name

        business_names = [name.lower() for name in businesses.keys()]

        if businessname.lower() in business_names:
            raise DuplicationError ('Storage::add_business',
                'Duplicate business name not allowed')

        self.__class__.businesses[businessname.lower()] = business_obj
        # increment the count of businesses ever stored
        self.__class__.counts['businesses'] += 1
        return 'SUCCESS: business {} created!'.format(businessname)

    def add_token (self, token, bearer_name):
        self.__class__.tokens [token] = bearer_name

    def get_business_index (self):
        index = self.__class__.counts['businesses']
        return index

    def get_user_index (self):
        index = self.__class__.counts['users']
        return index

    def get_review_index (self):
        index = self.__class__.counts['reviews']
        return index


    def get_businesses_info (self):
        businesses_info = []
        for business in self.__class__.businesses.values():
            business_data = self.clerk.extract_business_data (business)
            businesses_info.append (business_data)

        return businesses_info

    def find_by_id (self, _id, iterable_list):
        target_obj = None
        for obj in iterable_list:
            if obj.id == _id:
                target_obj = obj
        return target_obj

    def get_reviews_info (self, business_id):
        businesses = [business for business in self.__class__.businesses.values ()]
        target_business = self.find_by_id (business_id, businesses)
        reviews_info = []
        if target_business:
            target_id = target_business.id
            for review in self.__class__.reviews.values():
                if review.business_id == target_id:
                    review_info = self.clerk.extract_review_info (review)
                    reviews_info.append (review_info)

            return reviews_info
        msg = "UNSUCCESSFUL: Could not find the requested information"
        expression = "Storage::get_reviews_info ({})".format (business_id)
        raise DataNotFoundError (expression, msg)

    def get_business_info (self, business_id):
        businesses = [business for business in self.__class__.businesses.values ()]
        target_business = self.find_by_id (business_id, businesses)

        if target_business:
            business_info = self.clerk.extract_business_data (target_business)
            return business_info

        msg = "UNSUCCESSFUL: Could not find the requested information"
        expression = "Storage::get_business_info ({})".format (business_id)
        raise DataNotFoundError (expression, msg)

    def update_business (self, business_id, update_data, issuer_id):
        new_name = str(update_data.get ('name', ''))
        businesses = [business for business in self.__class__.businesses.values()]
        business_names = [name.lower() for name in self.__class__.businesses.keys()]

        is_same = False
        target_business = self.find_by_id (business_id, businesses)
        business_by_name = self.__class__.businesses.get(new_name.lower())

        if business_by_name and target_business:
            is_same = business_by_name.id == target_business.id

        if new_name and target_business:
            if new_name.lower() in business_names:
                # check if target business and the stored key are same
                if not is_same:
                    raise DuplicationError ("Storage::update_business",
                        'Duplicate business name not allowed')

        if target_business:
            issuer_is_owner = target_business.owner_id == issuer_id
            if issuer_is_owner:
                return self._do_update_business(target_business, update_data, is_same)
            # if instruction issuer is not owner
            msg = "UNSUCCESSFUL: The business is registered to another user"
            expression = "Storage::get_business_info ({}, {})".format (business_id, issuer_id)
            raise PermissionDeniedError (expression, msg)
        # if a business with the business_id is not found
        msg = "UNSUCCESSFUL: Could not find the requested information"
        expression = "Storage::get_business_info ({})".format (business_id)
        raise DataNotFoundError (expression, msg)


    def _do_update_business(self, target_business, update_data, is_same):
        new_name = update_data.get('name')
        old_key = target_business.name.lower()
        self.clerk.update_business (target_business, update_data)
        if new_name:
            self.__class__.businesses[new_name.lower()] = target_business
            if not is_same:
                del self.__class__.businesses[old_key]
        return "Changes recorded successfully"


    def delete_business (self, business_id, issuer_id):
        businesses = [business for business in self.__class__.businesses.values ()]
        target_business = self.find_by_id (business_id, businesses)
        if target_business:
            issuer_is_owner = target_business.owner_id == issuer_id
            if issuer_is_owner:
                # delete the business
                key = target_business.name.lower()
                del self.__class__.businesses[key]
                return "SUCCESS: business deleted"

            msg = "UNSUCCESSFUL: The business is registered to another user"
            expression = "Storage::delete_business ({}, {})".format(business_id, issuer_id)
            raise PermissionDeniedError (expression, msg)

        msg = "UNSUCCESSFUL: Could not find the requested information"
        expression = "Storage::delete_business ({}, {})".format(business_id, issuer_id)
        raise DataNotFoundError (expression, msg)


    def clear (self):
        self.__class__.users.clear ()
        self.__class__.businesses.clear ()
        self.__class__.reviews.clear ()
        self.__class__.counts['users'] = 0
        self.__class__.counts['businesses'] = 0
        self.__class__.counts['reviews'] = 0
        return 'cleared'
