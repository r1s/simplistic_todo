import os
import sys

PY2 = sys.version_info[0] == 2

APP_CONFIG = {
    'autojson': False,
}

APP_DIR = os.path.dirname(os.path.realpath(__file__))

SERVER_HOST = 'localhost'
SERVER_PORT = 8080
DEBUG = False

DATABASE_NAME = '.task.db'

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

MAX_LEN_PASSWORD = 128

SESSION_OPTS = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './.data',
    'session.auto': True
}

AUTH_SESSION_KEY = '_auth_user_id'
