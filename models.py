import hashlib
import random
import string
from peewee import Model, CharField, TextField, DateTimeField, ForeignKeyField, SqliteDatabase
import config

db = SqliteDatabase(config.DATABASE_NAME)



class User(Model):
    login = CharField(unique=True, max_length=64)
    password = CharField(max_length=48)

    class Meta:
        database = db

    @classmethod
    def gen_password(cls, password):
        method = 'sha1'
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        password = password + salt
        pass_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()

        return '{method}${pass_hash}${salt}'.format(method=method, pass_hash=pass_hash, salt=salt)

    def check_password(self, password):
        method, pass_hash, salt = self.password.split('$', 2)
        method_func = getattr(hashlib, method)
        password = password + salt
        return method_func(password.encode('utf-8')).hexdigest() == pass_hash


class Task(Model):

    STATUS_OPEN = 'open'
    STATUS_CLOSE = 'close'
    STATUSES = ((STATUS_OPEN, 'open'), (STATUS_CLOSE, 'close'))

    title = CharField(max_length=1024)
    description = TextField(null=True)
    deadline = DateTimeField(null=True)
    status = CharField(max_length=32, choices=STATUSES, default=STATUS_OPEN)
    owner = ForeignKeyField(User, related_name='tasks', null=True)

    class Meta:
        database = db

    def serialize_item(self):
        return {'title': self.title, 'description': self.description, 'status': self.status,
                'deadline': self.serialized_deadline}

    @property
    def serialized_deadline(self):
        from utils import convert_date_to_str
        return convert_date_to_str(self.deadline) if self.deadline else None


def setup_db(app):
    db.create_tables([User, Task], safe=True)

def drop_db_tables():
    db.connect()
    db.drop_tables([User, Task], safe=True)
    db.close()
