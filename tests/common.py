import sys
import os
import test_config

sys.path.append(os.path.sep.join(os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1]))

from webtest import TestApp
from functools import partial
from inspect import ismethod
import unittest
from main import setup_app
from models import drop_db_tables, db


def get_test_app():
    drop_db_tables()
    db.database = test_config.DATABASE_NAME
    app = setup_app()
    return app


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.test_app = TestApp(get_test_app(), extra_environ={'SERVER_PORT': str(test_config.SERVER_PORT)})
        self.default_content_type = 'application/json'
        self.default_status = '*'

    def _get_base_method(self, method_name, with_contenttype=True):
        method_func = getattr(self.test_app, method_name)
        if ismethod(method_func):
            if with_contenttype:
                return partial(method_func, status=self.default_status, content_type=self.default_content_type)
            else:
                return partial(method_func, status=self.default_status)
        else:
            raise AttributeError()

    def tearDown(self):
        if test_config.REMOVE_DB:
            os.remove(test_config.DATABASE_NAME)
