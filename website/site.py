import logging

from flask import (
    Blueprint,
    render_template
)

logger = logging.getLogger(__name__)

site_bp = Blueprint("site", __name__, url_prefix="/")
site_ui = dict(site=dict(brand=dict(text='XAM', icon='fa fa-brain'),
                         seo=dict(title='XAM', description='', keywords='', robots=''),
                         metas=dict(login_label='Login'),
                         links=dict(home=dict(name='home', path='/', icon='fa fa-home', text='Home'),
                                    auth_login=dict(name='auth_login', path='/auth/login', icon='fa fa-sign-in', text='Login'),
                                    auth_register=dict(name='auth_register', path='/auth/register', icon='fa fa-sign-up', text='Register'),
                                    auth_logout=dict(name='auth_logout', path='/auth/logout', icon='fa fa-sign-out', text='Logout'),
                         ),
                         menus=dict(main=dict(name='main', children=[{'name': 'home'}])),
                         items=dict(),
                         nodes=dict(),
                         pages=dict()),
               page=dict(path=''))


@site_bp.route("/")
def site_home():
    content = site_ui.copy()
    return render_template('home.html', **content), 200, {'Content-Type': 'text/html; charset=utf-8'}


@site_bp.route("/pages/<path:topic>")
def site_topic(topic):
    logger.warning(f'render site topic {topic}')
    content = site_ui.copy()
    content['page']['path'] = f'/pages/{topic}'
    return render_template('page.html', **content), 200, {'Content-Type': 'text/html; charset=utf-8'}


@site_bp.route("/pages/<path:topic>/<name>")
def site_topic_page(topic, name):
    logger.warning(f'render site topic page {topic} {name}')
    content = site_ui.copy()
    content['page']['path'] = f'/pages/{topic}/{name}'
    return render_template('page.html', **content), 200, {'Content-Type': 'text/html; charset=utf-8'}
