from bottle import request, HTTPResponse, default_app

from models import db, Task, User
from utils import convert_str_to_date, load_request_data, auth_required, make_auth_session, remove_auth_session, \
    get_task_or_404
from validators import TaskDataValidator, UserDataValidator, LoginUserValidator


task_data_validator = TaskDataValidator()
user_data_validator = UserDataValidator()
login_user_validator = LoginUserValidator()


@auth_required
def task_list(user):
    return {'data': [task.serialize_item() for task in list(user.tasks)]}

@auth_required
def task_show(user, task_id):
    task = get_task_or_404(task_id, user)
    return {'data': task.serialize_item()}

@auth_required
def task_add(user):
    app = default_app()

    data = load_request_data(request)
    errors = task_data_validator.validate(data, ignore_field_names=('owner', ))

    if not errors:
        data = dict(request.forms)
        if data.get('deadline'):
            data['deadline'] = convert_str_to_date(data['deadline'])

        with db.transaction():
            task = Task.create(owner=user, **data)

        location = app.get_url('task_show', task_id=task.get_id())
        data = {'id': task.get_id(), 'location': location}

        response = HTTPResponse(data, status=201)

    else:
        data = {'errors': {'fields': errors}}
        response = HTTPResponse(data, status=400)

    return response

@auth_required
def task_delete(user, task_id):
    task = get_task_or_404(task_id, user)
    task.delete_instance()
    return HTTPResponse({}, status=200)

@auth_required
def task_update(user, task_id):
    task = get_task_or_404(task_id, user)

    data = load_request_data(request)
    errors = task_data_validator.validate(data, ignore_field_names=('owner', ), create=False)

    if not errors:
        data = dict(data)
        with db.transaction():
            Task.update(**data).where(Task.id == task_id).execute()
        response = HTTPResponse({}, status=200)
    else:
        data = {'errors': {'fields': errors}}
        response = HTTPResponse(data, status=400)

    return response


def user_add():
    data = load_request_data(request)
    errors = user_data_validator.validate(data)
    if not errors:
        data = dict(data)
        data['password'] = User.gen_password(data['password'])
        with db.transaction():
            User.create(**data)
        response = HTTPResponse({}, status=201)
    else:
        response = HTTPResponse({'errors': {'fields': errors}}, status=400)
    return response


def user_login():
    data = load_request_data(request)
    errors = login_user_validator.validate(data)
    if not errors:
        user = User.get(User.login == data.get('login'))
        make_auth_session(request, user)
        response = HTTPResponse({}, status=200)
    else:
        response = HTTPResponse({'errors': {'fields': errors}}, status=400)
    return response

@auth_required
def user_logout(user):
    remove_auth_session(request)
    return HTTPResponse({}, status=200)
