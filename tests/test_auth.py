import re, unittest, json
from . import BaseAPITestSetUp
from .dummies import (user_data, user_data2,
                        invalid_credentials, login_data, login_data2)

class TestAPICase (BaseAPITestSetUp):
    # @pytest.mark.run(order = 1)
    def test_a_user_can_register (self):
        res = self.testHelper.register_user (user_data)
        msg = (json.loads(res.data.decode("utf-8")))['msg']
        pattern = r"^SUCCESS[: a-z]+ (?P<username>.+) [a-z!]+$"
        self.assertRegexpMatches (msg, pattern)
        # extract username from regular expression
        match = re.search (pattern, msg)
        user_in_response_msg = match.group ('username')
        # assert same as username in data sent
        self.assertEqual (user_in_response_msg, user_data['username'])

    def test_user_cannot_register_with_invalid_username(self):
        invalid_names = ['000', '90jdj', 'axc']
        for invalid_name in invalid_names:
            # make a copy of valid user_data by unpacking and replace username with invalid_name
            invalid_user_data = {**user_data, "username": invalid_name}
            # send request with invalid_user_data
            res = self.testHelper.register_user(invalid_user_data)
            msg = (json.loads(res.data.decode("utf-8")))['msg']
            self.assertEqual(msg, 'Invalid username!')

    # @pytest.mark.run(order = 2)
    def test_duplicate_username_disallowed (self):
        res = self.testHelper.register_user (user_data)
        # register user with similar data as used above
        res = self.testHelper.register_user (user_data)
        msg = (json.loads(res.data.decode("utf-8")))['msg']
        self.assertEqual (msg, 'Username already exists')
    #
    # @pytest.mark.run(order = 3)
    def test_user_can_login (self):
        res = self.testHelper.register_user (user_data)
        res = self.testHelper.login_user (login_data)
        msg = (json.loads(res.data.decode("utf-8")))['msg']

        pattern = r"Logged in (?P<username>.+)"
        self.assertRegexpMatches (msg, pattern)
        # extract username from regular expression
        match = re.search(pattern, msg)
        logged_user = match.group ('username')
        self.assertEqual (login_data['username'], logged_user)
    #
    # @pytest.mark.run(order = 4)
    def test_invalid_credentials_fail (self):
        res = self.testHelper.login_user (invalid_credentials)
        msg = (json.loads(res.data.decode("utf-8")))['msg']
        self.assertEqual (msg, 'Invalid username or password')
    #
    # @pytest.mark.run(order = 5)
    def test_user_can_logout (self):
        # register user
        self.testHelper.register_user (user_data)
        # login user
        self.testHelper.login_user (login_data)
        # logout user
        res = self.testHelper.logout_user ()
        msg = (json.loads(res.data.decode("utf-8")))['msg']
        self.assertEqual (msg, "Logged out successfully!")


    def test_users_can_reset_password (self):
        self.testHelper.register_user (user_data)
        # use username to send password reset request
        username = user_data['username']
        reset_data = {"username": username}
        resp = self.testHelper.reset_password (reset_data)
        token = (json.loads(resp.data.decode ('utf-8')))['t']
        # supply a new password
        reset_data = {'new_password': "changed"}
        resp = self.testHelper.reset_password (reset_data, token)
        msg = (json.loads (resp.data.decode ('utf-8')))['msg']
        self.assertEqual (msg, "Password updated successfully")
        # login with new password
        resp = self.testHelper.login_user ({"username": username,
                                        "password": "changed"})
        msg = (json.loads (resp.data.decode('utf-8')))['msg']
        pattern = r"Logged in (?P<username>.+)"
        self.assertRegexpMatches (msg, pattern)
        # test users cannot use an invalid token
        token = r"aquitelongstringrepresentingatokentoresetpassword"
        resp = self.testHelper.reset_password (reset_data, token)
        msg = (json.loads (resp.data.decode ('utf-8')))['msg']
        self.assertEqual (msg, "Invalid token")


if __name__ == "__main__":
    unittest.main (module = __name__)
