import bottle
from bottle import run, Bottle

import config

from views import task_list, task_show, task_add, task_update, task_delete, user_add, user_login, user_logout
from models import setup_db
from beaker.middleware import SessionMiddleware

def setup_routing(app):
    app.route('/tasks', ['GET'], task_list, name='task_list')
    app.route('/tasks', ['POST'], task_add)
    app.route('/tasks/<task_id:int>', ['PUT'], task_update)
    app.route('/tasks/<task_id:int>', ['DELETE'], task_delete)
    app.route('/tasks/<task_id:int>', ['GET'], task_show, name='task_show')

    app.route('/users', ['POST'], user_add)
    app.route('/login', ['POST'], user_login)
    app.route('/logout', ['POST'], user_logout)


def setup_app():
    app = Bottle()
    app.config.update(config.APP_CONFIG)
    setup_routing(app)
    setup_db(app)
    bottle.app.push(app)
    app = SessionMiddleware(app, config.SESSION_OPTS)
    return app



def run_app():
    app = setup_app()
    run(app, host=config.SERVER_HOST, port=config.SERVER_PORT, reloader=True)


if __name__ == '__main__':
    run_app()
