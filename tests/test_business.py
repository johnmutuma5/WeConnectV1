import unittest, json
from app.v1.models import Business
from app.exceptions import InvalidUserInputError
from app.v1 import store
from . import BaseAPITestSetUp
from .dummies import (user_data, user_data2, business_data,
                        invalid_credentials, login_data, login_data2,
                        businesses_data, update_data, review_data)
import re


class TestBusinessCase (BaseAPITestSetUp):
    def test_user_can_register_business (self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        res = self.testHelper.register_business (business_data)
        msg = (json.loads(res.data.decode("utf-8")))['msg']

        pattern = r"^SUCCESS[: a-z]+ (?P<business>.+) [a-z!]+$"
        self.assertRegexpMatches (msg, pattern)

    def test_users_cannot_register_business_without_login_in(self):
        res = self.testHelper.register_business (business_data)
        resp_dict = json.loads(res.data.decode("utf-8"))
        msg = resp_dict['msg']
        self.assertEqual(msg, 'You need to log in to perform this operation')



    def test_handles_blank_business_name(self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        data_lacking_name = {**business_data, "name": ""}
        res = self.testHelper.register_business (data_lacking_name)
        resp_dict = json.loads(res.data.decode('utf-8'))
        msg = resp_dict.get("msg")
        self.assertEqual(msg, "Please provide name")


    def test_handles_invalid_business_name(self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        data_having_bad_name = {**business_data, "name": "...fjfj.."}
        res = self.testHelper.register_business (data_having_bad_name)
        resp_dict = json.loads(res.data.decode('utf-8'))
        msg = resp_dict.get("msg")
        self.assertEqual(msg, "Invalid business name")


    def test_duplicate_businessname_disallowed (self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        self.testHelper.register_business (business_data)
        res = self.testHelper.register_business (business_data)
        msg = (json.loads(res.data.decode("utf-8")))['msg']
        self.assertEqual (msg, 'Duplicate business name not allowed')
    # #
    # @pytest.mark.run(order = 8)
    def test_users_retrieve_all_businesses (self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        # register a number of businesses
        for business_data in businesses_data:
            self.testHelper.register_business (business_data)
        # get all businesses info
        res = self.testHelper.get_businesses ()
        res_businesses = (json.loads(res.data.decode("utf-8")))["businesses"]
        res_business_names = [business_info['name'] for business_info in res_businesses]
        # assert that every piece of information we have sent has been returned
        for data in businesses_data:
            self.assertIn (data['name'], res_business_names)
    #
    # @pytest.mark.run(order = 9)
    def test_users_retrieve_one_business (self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        # register a number of businesses
        self.testHelper.register_business (business_data)
        raw_id = 1
        res = self.testHelper.get_business (raw_id)
        res_business_info = (json.loads(res.data.decode("utf-8")))["info"]
        res_business_id = res_business_info['id']
        # assert that the response business id equals the url variable
        sent_id = Business.gen_id_string (raw_id)
        self.assertEqual (res_business_id, sent_id)
    #
    # @pytest.mark.run(order = 10)
    def test_users_retrieve_only_avail_business (self):
        raw_id = 1000000
        res = self.testHelper.get_business (raw_id)
        res_msg= (json.loads(res.data.decode("utf-8")))["msg"]
        # test message to match regex
        pattern = r"^UNSUCCESSFUL:.+$"
        self.assertRegexpMatches (res_msg, pattern)


    def test_users_update_a_business (self):
        raw_id = 1
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        self.testHelper.register_business (business_data)
        self.testHelper.update_business (raw_id, update_data)
        # get the business's info in it's new state
        res = self.testHelper.get_business (raw_id)
        res_business_info = (json.loads(res.data.decode("utf-8")))["info"]

        for key, value in update_data.items():
            self.assertEqual (update_data[key], res_business_info[key])


    def test_users_cannot_update_with_existing_business_names (self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        self.testHelper.register_business (business_data)
        # register another businesses
        self.testHelper.register_business (businesses_data[1])
        name_update_data = {"name": "Google"}
        resp = self.testHelper.update_business(1, name_update_data)
        msg = (json.loads(resp.data.decode('utf-8')))['msg']
        self.assertEqual (msg, "Duplicate business name not allowed")


    def test_users_cannot_update_with_blank_name(self):
        self.testHelper.register_user (user_data)
        self.testHelper.login_user (login_data)
        self.testHelper.register_business (business_data)
        # register another businesses
        self.testHelper.register_business (businesses_data[1])
        name_update_data = {"name": "  "}
        resp = self.testHelper.update_business(1, name_update_data)
        resp_dict = json.loads(resp.data.decode('utf-8'))
        msg = resp_dict.get('msg')
        self.assertEqual(msg, 'Please provide name')


    def test_users_can_delete_business(self):
        self.testHelper.register_user(user_data)
        # login the first user
        self.testHelper.login_user (login_data)
        self.testHelper.register_business (business_data)
        # delete business
        resp = self.testHelper.delete_business (1)
        msg = (json.loads(resp.data.decode("utf-8")))["msg"]
        self.assertEqual (msg, "SUCCESS: business deleted")


    def test_users_can_only_update_their_business(self):
        self.testHelper.register_user(user_data)
        self.testHelper.login_user(login_data)
        self.testHelper.register_business(business_data)
        # logout the current user
        self.testHelper.logout_user()
        # create a second user`
        self.testHelper.register_user(user_data2)
        self.testHelper.login_user(login_data2)
        # try to update a business created by the just logged out user
        resp = self.testHelper.update_business(1, update_data)
        self.assertEqual(resp.status_code, 403)


    def test_users_can_only_delete_their_business(self):
        self.testHelper.register_user(user_data)
        self.testHelper.login_user(login_data)
        self.testHelper.register_business(business_data)
        # logout the current user
        self.testHelper.logout_user()
        # create a second user`
        self.testHelper.register_user(user_data2)
        self.testHelper.login_user(login_data2)
        # try to delete a business created by the just logged out user
        resp = self.testHelper.delete_business(1)
        self.assertEqual(resp.status_code, 403)


    def test_handles_updating_unavailble_business_id(self):
        self.testHelper.register_user(user_data)
        res = self.testHelper.login_user(login_data)
        # update with an unavailable id
        name_update_data = {"name": "Google"}
        resp = self.testHelper.update_business(10001, name_update_data)
        res_msg = (json.loads(resp.data.decode("utf-8")))["msg"]
        # test message to match regex
        pattern = r"^UNSUCCESSFUL:.+$"
        self.assertRegexpMatches(res_msg, pattern)


    def test_handles_deleting_unavailble_business_id(self):
        self.testHelper.register_user(user_data)
        res = self.testHelper.login_user(login_data)
        # update with an unavailable id
        name_update_data = {"name": "Google"}
        resp = self.testHelper.delete_business(10001)
        res_msg = (json.loads(resp.data.decode("utf-8")))["msg"]
        # test message to match regex
        pattern = r"^UNSUCCESSFUL:.+$"
        self.assertRegexpMatches(res_msg, pattern)



if __name__ == "__main__":
    unittest.main (module = __name__)
