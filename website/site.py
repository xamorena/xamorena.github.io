import logging

from flask import (
    Blueprint,
    current_app,
    render_template,
    jsonify)

logger = logging.getLogger(__name__)

site_bp = Blueprint("site", __name__, url_prefix="/")


@site_bp.route("/")
def site_home():
    cm = current_app.cms.get_content_manager()
    content, template = cm.get_content('home', 'home.html')
    return render_template(template, **content), 200, {'Content-Type': 'text/html; charset=utf-8'}


@site_bp.route("/pages/<path:topic>")
def site_topic(topic):
    logger.warning(f'render site topic {topic}')
    cm = current_app.cms.get_content_manager()
    content, template = cm.get_content(f'{topic}', 'page.html')
    content['page']['path'] = f'/pages/{topic}'
    return render_template(template, **content), 200, {'Content-Type': 'text/html; charset=utf-8'}


@site_bp.route("/pages/<path:topic>/<name>")
def site_topic_page(topic, name):
    logger.warning(f'render site topic page {topic} {name}')
    cm = current_app.cms.get_content_manager()
    content, template = cm.get_content(f'{topic}_{name}', 'page.html')
    content['page']['path'] = f'/pages/{topic}/{name}'
    return render_template(template, **content), 200, {'Content-Type': 'text/html; charset=utf-8'}
