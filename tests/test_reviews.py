import unittest, json
from . import BaseAPITestSetUp
from .dummies import (user_data, user_data2, business_data,
                        login_data, login_data2,
                        review_data)
import re


class TestAPICase (BaseAPITestSetUp):
    def test_users_can_make_a_review (self):
        self.testHelper.register_user (user_data)
        self.testHelper.register_user (user_data2)
        # login the first user
        self.testHelper.login_user (login_data)
        self.testHelper.register_business (business_data)
        self.testHelper.logout_user ()
        # login second user
        self.testHelper.login_user (login_data2)
        # second user make a review
        resp = self.testHelper.make_review (1, review_data[0])
        msg = (json.loads(resp.data.decode("utf-8")))["msg"]
        #extract posted review heading from message
        pattern = r"\w+:\[(?P<heading>.+)\] "
        match = re.search (pattern, msg)
        posted_review_heading = match.group ("heading")
        self.assertEqual (posted_review_heading, review_data[0]['heading'])
        self.testHelper.logout_user ()
    #
    # @pytest.mark.run(order = 15)
    def test_user_can_get_reviews (self):
        self.testHelper.register_user (user_data)
        self.testHelper.register_user (user_data2)
        self.testHelper.login_user (login_data)
        self.testHelper.register_business (business_data)
        self.testHelper.make_review (1, review_data[0])
        self.testHelper.logout_user ()
        #login another user
        self.testHelper.login_user (login_data2)
        self.testHelper.make_review (1, review_data[1])
        resp = self.testHelper.get_all_reviews (1)
        reviews_info = (json.loads(resp.data.decode("utf-8")))['info']
        resp_review_headings = [review_info['heading'] for review_info in reviews_info]
        # check that all review heading have been returned
        for data in review_data:
            self.assertIn (data['heading'], resp_review_headings)


    def test_users_cannot_retrieve_reviews_for_non_existent_businesses(self):
        raw_id = 1000000
        responses = [self.testHelper.get_business(raw_id),
                     self.testHelper.get_all_reviews(raw_id)]
        for resp in responses:
            res_msg = (json.loads(resp.data.decode("utf-8")))["msg"]
            # test message to match regex
            pattern = r"^UNSUCCESSFUL:.+$"
            self.assertRegexpMatches(res_msg, pattern)


if __name__ == "__main__":
    unittest.main (module = __name__)
