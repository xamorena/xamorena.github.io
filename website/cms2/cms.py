import logging
import os

from flask import g

from .managers import ContentManager

logger = logging.getLogger(__name__)

DEFAULT_CONTENTS_FOLDER = 'contents'


class CMS(object):
    def __init__(self, app=None):
        self.app = app
        self.content_manager = None

    def setup_content_manager(self, app):

        @app.context_processor
        def inject_cms_template_scope():
            injections = dict()

            def get_theme() -> str:
                cm = self.content_manager
                return cm.get_theme() if cm is not None else {}

            def get_site() -> str:
                cm = self.content_manager
                return cm.get_site() if cm is not None else {}

            def get_site_styles() -> str:
                cm = self.content_manager
                return cm.get_site().get('styles', '') if cm is not None else ''

            def get_site_scripts() -> str:
                cm = self.content_manager
                return cm.get_site().get('scripts', '') if cm is not None else ''

            def get_site_seo() -> dict:
                cm = self.content_manager
                return cm.get_site().get('seo') if cm is not None else {}

            def get_site_brand() -> dict:
                cm = self.content_manager
                return cm.get_site().get('brand') if cm is not None else {}

            def get_site_meta(name: str) -> dict:
                cm = self.content_manager
                md = cm.get_item('meta', name) if cm is not None else None
                return md.get('data', name) if md is not None else name

            def get_site_link(name: str) -> dict:
                cm = self.content_manager
                return cm.get_item('link', name) if cm is not None else {}

            def get_site_menu(name: str) -> dict:
                cm = self.content_manager
                return cm.get_item('menu', name) if cm is not None else {}

            def get_user_menu(name: str) -> dict:
                cm = self.content_manager
                role = 'guest'
                if g.user is not None:
                    role = 'admin' if g.user.get('role', '') == 'admin' else 'users'
                menu = cm.get_user_menu(name, role) if cm is not None else {}
                return menu

            def get_site_node(name: str) -> dict:
                cm = self.content_manager
                return cm.get_item('node', name) if cm is not None else {}

            def get_site_page(name: str) -> dict:
                cm = self.content_manager
                return cm.get_item('page', name) if cm is not None else {}

            injections.update(
                cms_theme=get_theme,
                cms_site=get_site,
                cms_site_styles=get_site_styles,
                cms_site_scripts=get_site_scripts,
                cms_site_seo=get_site_seo,
                cms_site_menu=get_site_menu,
                cms_site_brand=get_site_brand,
                cms_meta=get_site_meta,
                cms_link=get_site_link,
                cms_menu=get_user_menu,
                cms_node=get_site_node,
                cms_page=get_site_page
            )
            return injections

        return app

    def init_app(self, app):
        if hasattr(app, 'cms'):
            return
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['cms'] = self
        self.app = app
        app.teardown_appcontext(self.teardown)
        app.config.setdefault('CMS_HOST', 'localhost')
        app.config.setdefault('CMS_CONTENTS_FOLDER', DEFAULT_CONTENTS_FOLDER)
        app.config.setdefault('CMS_DESIGN_THEMES', ["default"])
        contents_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), app.config['CMS_CONTENTS_FOLDER'])
        default_theme = app.config['CMS_DESIGN_THEMES']
        self.content_manager = ContentManager(contents_path,
                                              default_theme,
                                              app.config['CMS_HOST'])
        setattr(app, 'cms', self)
        self.setup_content_manager(app)

    def teardown(self, _exception):
        from flask import _app_ctx_stack
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'content_manager'):
            ctx.content_manager.close()

    def get_content_manager(self):
        from flask import _app_ctx_stack
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'content_manager'):
                ctx.content_manager = self.content_manager
                return ctx.content_manager

        return self.content_manager
