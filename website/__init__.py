import datetime

import markdown
from flask import (
    Flask,
    current_app,
    session,
    request,
    g
)
from .config import SESSION_TIMEOUT


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    from .site import site_bp
    app.register_blueprint(site_bp)

    @app.before_request
    def setup_request():
        if not session.permanent:
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=SESSION_TIMEOUT)
        g.theme = request.args.get("theme", session.get("theme", "default"))
        session['theme'] = g.theme
        g.user = None
        if request.headers.get('X-Forwarded-For', None) is not None:
            g.forwarders = str(request.headers.get('X-Forwarded-For')).split(',')
            g.remote_addr = g.forwarders[:1]
        else:
            g.remote_addr = request.remote_addr
        g.web_host = request.headers.get('Host', 'localhost')
        g.user_agent = request.headers.get('User-Agent', '')
        g.accept_language = request.headers.get('Accept-Language', '')
        g.lang = g.accept_language

    @app.context_processor
    def inject_template_scope():
        injections = dict()

        def cookies_check():
            value = request.cookies.get('cookie_consent')
            return value == 'true'

        injections.update(cookies_check=cookies_check, current_time=datetime.datetime.utcnow())
        return injections

    @app.template_filter('md')
    def md(text):
        return markdown.markdown(text) if text is not None else ''

    @app.template_filter('dt')
    def dt(date: str, format='%Y/%m/%d %H:%M'):
        val = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%f')
        return val.strftime(format)

    return app
