from collections import defaultdict
from peewee import PrimaryKeyField
import peewee
import six
import config
from models import Task, User
from utils import convert_str_to_date


class BaseValidator(object):

    model = None
    validators_prefix = 'validate_'
    error_messages = {'required': 'Field required.', 'long_str': 'Invalid length.', 'invalid_type': 'Invalid type.'}
    
    def __init__(self, create=True):
        super(BaseValidator, self).__init__()
        self.create = create

    def validate(self, data, ignore_field_names=(), ignore_pk=True, create=None):
        errors = defaultdict(list)

        create = create if create is not None else self.create

        for field in self.model._meta.get_fields():
            if ignore_pk and isinstance(field, PrimaryKeyField):
                continue
            elif field.name in ignore_field_names:
                continue
            elif field.null and data.get(field.name) is None:
                continue

            field_validator = getattr(self, '{0}{1}'.format(self.validators_prefix, field.name), None)

            if create and field.name not in data and field.default is None:
                errors[field.name].append(self.error_messages['required'])

            elif field_validator is not None and callable(field_validator):
                field_errors = field_validator(data.get(field.name))
                if field_errors:
                    errors[field.name].extend(field_errors)

        errors = self.common_validate(data, errors)

        return errors

    def common_validate(self, data, errors):
        return errors

    def type_str_validator(self, value):
        if config.PY2:
            return isinstance(value, (str, unicode))
        else:
            return isinstance(value,  (str, ))


class TaskDataValidator(BaseValidator):

    model = Task

    def validate_title(self, value):
        errors = []

        if value is not None and not self.type_str_validator(value):
            errors.append(self.error_messages['invalid_type'])
        elif value is not None and len(value) > self.model.title.max_length:
            errors.append(self.error_messages['long_str'])

        return errors

    def validate_description(self, value):
        errors = []

        if value is not None and not self.type_str_validator(value):
            errors.append(self.error_messages['invalid_type'])
        return errors

    def validate_status(self, value):
        errors = []

        if value is not None and value not in dict(self.model.STATUSES):
            errors.append('Invalid choice.')
        return errors

    def validate_deadline(self, value):
        errors = []

        if value is not None:
            try:
                convert_str_to_date(value)
            except (ValueError, ) as e:
                errors.append('Invalid datetime format.')

        return errors


class UserDataValidator(BaseValidator):

    model = User

    def validate_login(self, value):
        errors = []

        if value is not None:
            if not self.type_str_validator(value):
                errors.append(self.error_messages['invalid_type'])
            elif len(value) > self.model.login.max_length:
                errors.append(self.error_messages['long_str'])
            elif list(filter(lambda v: not v.isalnum(), value)):
                errors.append('Login incorrect.')
            elif self.create and self.model.select().where(self.model.login == value).count():
                errors.append('Login exist.')

        return errors

    def validate_password(self, value):
        errors = []

        if value is not None and not self.type_str_validator(value):
            errors.append(self.error_messages['invalid_type'])
        elif value is not None and len(value) > config.MAX_LEN_PASSWORD:
            errors.append(self.error_messages['long_str'])

        return errors
    

class LoginUserValidator(UserDataValidator):

    def __init__(self, create=False):
        super(LoginUserValidator, self).__init__(create)
    
    def validate_login(self, value):
        errors = super(LoginUserValidator, self).validate_login(value)

        if not errors:
            try:
                User.get(User.login == value)
            except (peewee.DoesNotExist, ) as e:
                errors.append('Login not found.')

        return errors

    def common_validate(self, data, errors):
        errors = super(LoginUserValidator, self).common_validate(data, errors)
        if not errors:
            user = User.get(User.login == data.get('login'))
            if not user.check_password(data.get('password')):
                errors['password'].append('Password incorrect.')

        return errors
