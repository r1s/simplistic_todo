import unittest
from datetime import datetime
import peewee
from common import BaseTest
from models import Task, db

from utils import convert_date_to_str


class TestTask(BaseTest):

    def login(self):
        user_method_func = self._get_base_method('post')
        login_url = '/login'
        create_url = '/users'

        user_data = {'login': 'Test', 'password': 'Test'}
        user_method_func(create_url, params=user_data)
        user_method_func(login_url, params=user_data)

    def logout(self):
        user_method_func = self._get_base_method('post')
        logout_url = '/logout'
        user_method_func(logout_url)

    def create_task(self):
        self.login()
        method_func = self._get_base_method('post')
        url = '/tasks'
        resp = method_func(url, params={'title': 'Test', 'description': 'Test'})
        return resp.json.get('id')

    def test_task_list(self):
        method_func = self._get_base_method('get', False)
        url = '/tasks'

        self.logout()
        resp = method_func(url)
        self.assertEqual(resp.status_int, 401)

        self.login()
        resp = method_func(url)
        self.assertEqual(resp.status_int, 200)
        resp = self._get_base_method('delete')(url)
        self.assertEqual(resp.status_int, 405)

    def test_create_task(self):
        method_func = self._get_base_method('post')

        url = '/tasks'

        self.logout()

        resp = method_func(url, params={'title': 'Test'})
        self.assertEqual(resp.status_int, 401)

        self.login()

        resp = method_func(url, params={'title': 'Test'})
        self.assertEqual(resp.status_int, 201)
        self.assertIn('id', resp.json)
        self.assertIn('location', resp.json)

        resp = method_func(url, params={})
        self.assertEqual(resp.status_int, 400)
        self.assertIn('errors', resp.json)
        self.assertListEqual([u'Field required.'], resp.json.get('errors', {}).get('fields').get('title'))

        resp = method_func(url, params={'title': 'Test', 'status': ''})
        self.assertEqual(resp.status_int, 400)
        self.assertIn('errors', resp.json)
        self.assertListEqual([u'Invalid choice.'], resp.json.get('errors', {}).get('fields').get('status'))

        resp = method_func(url, params={'title': 'T' * 4096})
        self.assertEqual(resp.status_int, 400)
        self.assertIn('errors', resp.json)
        self.assertListEqual([u'Invalid length.'], resp.json.get('errors', {}).get('fields').get('title'))

        resp = method_func(url, params={'title': 'Test', 'deadline': 'asdf'})
        self.assertEqual(resp.status_int, 400)
        self.assertIn('errors', resp.json)
        self.assertListEqual([u'Invalid datetime format.'], resp.json.get('errors', {}).get('fields').get('deadline'))

        resp = method_func(url, params={'title': 'Test', 'status': 'close', 'description': 'description',
                                        'deadline': convert_date_to_str(datetime.now())})
        self.assertEqual(resp.status_int, 201)

        resp = method_func(url, params={'title': 4096})
        self.assertEqual(resp.status_int, 201)

        resp = method_func(url, params={'title': 'Test', 'qwerty': 'some'})
        self.assertEqual(resp.status_int, 201)

        method_func = self._get_base_method('post_json')
        resp = method_func(url, params={'title': ['1', '2', '3']})
        self.assertEqual(resp.status_int, 400)

    def test_delete_task(self):
        method_func = self._get_base_method('delete')

        task_id = self.create_task()
        url = '/tasks/{0}'.format(task_id)

        self.logout()
        resp = method_func(url)
        self.assertEqual(resp.status_int, 401)

        self.login()
        resp = method_func(url)
        self.assertEqual(resp.status_int, 200)
        self.assertRaises(peewee.DoesNotExist, lambda: Task.get(Task.id == task_id))

        resp = method_func('/tasks/qwerty')
        self.assertEqual(resp.status_int, 404)

    def test_update_task(self):
        method_func = self._get_base_method('put')

        task_id = self.create_task()
        url = '/tasks/{0}'.format(task_id)
        not_found_url = '/tasks/0'

        self.logout()
        resp = method_func(url)
        self.assertEqual(resp.status_int, 401)

        self.login()
        title = 'Some another'
        resp = method_func(url, params={'title': title})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(Task.get(Task.id == task_id).title, title)

        description = 'Qwerty'
        resp = method_func(url, params={'description': description})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(Task.get(Task.id == task_id).description, description)

        description = description * 10
        resp = method_func(url, params={'description': description})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(Task.get(Task.id == task_id).description, description)

        resp = method_func(url, params={'status': Task.STATUS_CLOSE})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(Task.get(Task.id == task_id).status, Task.STATUS_CLOSE)

        resp = method_func(url, params={'status': Task.STATUS_OPEN})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(Task.get(Task.id == task_id).status, Task.STATUS_OPEN)

        resp = method_func(not_found_url, params={'title': 'Some another'})
        self.assertEqual(resp.status_int, 404)

    def test_show_task(self):
        method_func = self._get_base_method('get', False)

        task_id = self.create_task()
        url = '/tasks/{0}'.format(task_id)

        self.logout()
        resp = method_func(url)
        self.assertEqual(resp.status_int, 401)

        self.login()
        resp = method_func(url)
        self.assertEqual(resp.status_int, 200)
        self.assertTrue(resp.json.get('data', {}).get('title'))


if __name__ == '__main__':
    unittest.main()
