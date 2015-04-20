import unittest
from bottle import request
from common import BaseTest

import config
from utils import get_current_user
from models import User


class TestUser(BaseTest):

    def test_create_user(self):
        method_func = self._get_base_method('post')
        url = '/users'


        resp = method_func(url, params={'login': 'Test0', 'password': 'Test'})
        self.assertEqual(resp.status_int, 201)

        resp = method_func(url, params={})
        self.assertEqual(resp.status_int, 400)
        self.assertIn('errors', resp.json)
        self.assertListEqual(['Field required.'], resp.json.get('errors', {}).get('fields').get('login'))
        self.assertListEqual(['Field required.'], resp.json.get('errors', {}).get('fields').get('password'))

        resp = method_func(url, params={'login': 'T' * 4096})
        self.assertEqual(resp.status_int, 400)
        self.assertIn('errors', resp.json)
        self.assertListEqual(['Invalid length.'], resp.json.get('errors', {}).get('fields').get('login'))

        resp = method_func(url, params={'password': 'T' * (config.MAX_LEN_PASSWORD + 1)})
        self.assertEqual(resp.status_int, 400)
        self.assertIn('errors', resp.json)
        self.assertListEqual(['Invalid length.'], resp.json.get('errors', {}).get('fields').get('password'))

        resp = method_func(url, params={'login': 4096, 'password': 'Test'})
        self.assertEqual(resp.status_int, 201)

        resp = method_func(url, params={'login': 'Test0', 'password': 'Test'})
        self.assertEqual(resp.status_int, 400)

        method_func = self._get_base_method('post_json')
        resp = method_func(url, {'login': ['1', '2', '3'], 'password': 'Test'})
        self.assertEqual(resp.status_int, 400)

    def test_login_user(self):
        method_func = self._get_base_method('post')
        url = '/login'
        create_url = '/users'

        user_data = {'login': 'Test', 'password': 'Test'}
        method_func(create_url, params=user_data)

        resp = method_func(url, params=user_data)
        self.assertEqual(get_current_user(request).get_id(), User.get(User.login == user_data.get('login')).get_id())
        self.assertEqual(resp.status_int, 200)

        resp = method_func(url, params={'login': 'Test', 'password': 'Testtt'})
        self.assertEqual(resp.status_int, 400)
        self.assertListEqual(['Password incorrect.'], resp.json.get('errors', {}).get('fields').get('password'))

        resp = method_func(url, params={'login': 'qwerest', 'password': 'Test'})
        self.assertEqual(resp.status_int, 400)
        self.assertListEqual(['Login not found.'], resp.json.get('errors', {}).get('fields').get('login'))

    def test_logout_user(self):
        method_func = self._get_base_method('post')
        login_url = '/login'
        create_url = '/users'
        url = '/logout'

        user_data = {'login': 'Test', 'password': 'Test'}

        current_user = get_current_user(request)

        if current_user:
            resp = method_func(url, params=user_data)
            self.assertEqual(resp.status_int, 200)

        resp = method_func(url, params=user_data)
        self.assertEqual(resp.status_int, 401)

        method_func(create_url, params=user_data)
        method_func(login_url, params=user_data)

        resp = method_func(url)
        self.assertEqual(resp.status_int, 200)


if __name__ == '__main__':
    unittest.main()
