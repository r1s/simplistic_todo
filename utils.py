from datetime import datetime
from bottle import request, HTTPResponse, abort
import peewee
import config
from models import User, Task


def convert_date_to_str(date):
    return date.strftime(config.DATE_FORMAT)


def convert_str_to_date(str_date):
    return datetime.strptime(str_date, config.DATE_FORMAT)

def load_request_data(request):
    try:
        data = dict(request.json)
    except (ValueError, TypeError) as e:
        data = request.forms

    return data


def make_auth_session(request, user):
    session = request.environ.get('beaker.session')
    session[config.AUTH_SESSION_KEY] = user.get_id()
    session.save()


def remove_auth_session(request):
    session = request.environ.get('beaker.session')
    session.pop(config.AUTH_SESSION_KEY)
    session.save()


def get_current_user(request):
    session = request.environ.get('beaker.session')
    user_id = session.get(config.AUTH_SESSION_KEY)
    user = None
    if user_id:
        try:
            user = User.get(User.id == user_id)
        except (peewee.DoesNotExist, ) as e:
            pass

    return user


def auth_required(view_func):

    def wrapper(*args, **kwargs):
        current_user = get_current_user(request)

        if current_user:
            return view_func(current_user, *args, **kwargs)
        else:
            return HTTPResponse({}, status=401)


    return wrapper

def get_task_or_404(task_id, user):
    try:
        return Task.select().where(Task.id == task_id, Task.owner == user).get()
    except (peewee.DoesNotExist, ) as e:
        abort(404, 'Task not found.')
