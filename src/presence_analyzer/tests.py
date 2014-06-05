# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest
from lxml import html

from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)
TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
)
TEST_CACHE_SERVER = '127.0.0.1:11211'
TEST_CACHE_APP_KEY = '_presence_analyzer_testing'


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})
        main.app.config.update({'CACHE_APP_KEY': TEST_CACHE_APP_KEY})
        main.app.config.update({'CACHE_SERVER': TEST_CACHE_SERVER})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[1], {
            u'user_id': 10,
            u'name': u'Maciej Z.',
            u'avatar': 'https://intranet.stxnext.pl:443/api/images/users/10',
        })

    def test_api_mean_time_weekday(self):
        """
        Test mean weekday for given user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEquals(len(data), 7)
        self.assertEquals(data, [
            [u'Mon', 0],
            [u'Tue', 30047.0],
            [u'Wed', 24465.0],
            [u'Thu', 23705.0],
            [u'Fri', 0],
            [u'Sat', 0],
            [u'Sun', 0]])
        resp = self.client.get('/api/v1/mean_time_weekday/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)

    def test_api_presence_weekday(self):
        """
        Test if total presence of a given user is correctly computed.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertEquals(data, [
            [u'Weekday', u'Presence (s)'],
            [u'Mon', 0],
            [u'Tue', 30047],
            [u'Wed', 24465],
            [u'Thu', 23705],
            [u'Fri', 0],
            [u'Sat', 0],
            [u'Sun', 0]])
        resp = self.client.get('/api/v1/presence_weekday/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)

    def test_api_mean_start_end(self):
        """
        Test if mean arrival/leave data are correctly returned by API.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(data, [
            [u'Mon', 0, 0],
            [u'Tue', 34745, 64792],
            [u'Wed', 33592, 58057],
            [u'Thu', 38926, 62631],
            [u'Fri', 0, 0],
            [u'Sat', 0, 0],
            [u'Sun', 0, 0]])

    def test_presence_weekday_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/presence_weekday.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')
        source = html.fromstring(resp.data)
        text = source.xpath('//li[@id="selected"]/a')[0].text
        self.assertEqual(text, 'Presence by weekday')

    def test_presence_mean_view(self):
        """
        Test presence mean view.
        """
        resp = self.client.get('/presence_mean_time.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')
        source = html.fromstring(resp.data)
        text = source.xpath('//li[@id="selected"]/a')[0].text
        self.assertEqual(text, 'Presence mean time')

    def test_presence_start_end_view(self):
        """
        Test presence arrival/leave view.
        """
        resp = self.client.get('/presence_start_end.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')
        source = html.fromstring(resp.data)
        text = source.xpath('//li[@id="selected"]/a')[0].text
        self.assertEqual(text, 'Presence start-end')


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})
        main.app.config.update({'CACHE_APP_KEY': TEST_CACHE_APP_KEY})
        main.app.config.update({'CACHE_SERVER': TEST_CACHE_SERVER})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """
        Test if function correctly groups by weekdays.
        """
        data = utils.get_data()
        test = {0: [], 1: [30047], 2: [24465], 3: [23705], 4: [], 5: [], 6: []}
        self.assertDictEqual(utils.group_by_weekday(data[10]), test)

    def test_group_by_start_end(self):
        """
        Test grouping by mean arrival/leave hours.
        """
        data = utils.get_data()
        test = {
            0: {'start': 0, 'end': 0},
            1: {'start': 34745, 'end': 64792},
            2: {'start': 33592, 'end': 58057},
            3: {'start': 38926, 'end': 62631},
            4: {'start': 0, 'end': 0},
            5: {'start': 0, 'end': 0},
            6: {'start': 0, 'end': 0},
        }
        grouped_data = utils.group_by_weekday_start_end(data[10])
        self.assertDictEqual(grouped_data, test)

    def test_seconds_since_midnight(self):
        """
        Test if seconds are computed correctly.
        """
        time = datetime.time(1, 1, 1)
        seconds = utils.seconds_since_midnight(time)
        self.assertEquals(seconds, 3661)

        # more complicated case
        time = datetime.time(6, 10, 1)
        seconds = utils.seconds_since_midnight(time)
        self.assertEquals(seconds, 6 * 3600 + 10 * 60 + 1)

    def test_interval(self):
        """
        Test if interval is computed correctly.
        """
        start_time = datetime.time()
        end_time = datetime.time(1, 1, 1)
        self.assertEqual(utils.interval(start_time, end_time), 3661)

        # second case
        start_time = datetime.time(2, 3, 4)
        end_time = datetime.time(5, 6, 7)
        self.assertEqual(utils.interval(start_time, end_time), 10983)

    def test_mean(self):
        """
        Test calculation of arithmetic mean.
        """
        self.assertEqual(utils.mean([0]), 0)
        self.assertEqual(utils.mean(range(1, 10)), 5.)
        self.assertEqual(utils.mean(range(5, 11)), 7.5)
        self.assertIsInstance(utils.mean([0]), float)

    def test_get_additional_data(self):
        data = utils.get_user_additional_data()
        test = {
            '11': {
                'url': 'https://intranet.stxnext.pl:443/api/images/users/11',
                'name': 'Maciej D.',
                },
            '10': {
                'url': 'https://intranet.stxnext.pl:443/api/images/users/10',
                'name': 'Maciej Z.',
                }
            }
        self.assertDictEqual(data, test)


def suite():
    """
    Default test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    test_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.main()
