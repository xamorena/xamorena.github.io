import json
import logging
import os

import jsonschema.exceptions
from flask import session
from jsonschema import validate

from .schemas import (
    LinkSchema,
    MenuSchema,
    MetaSchema,
    ItemSchema,
    NodeSchema,
    PageSchema,
    SiteSchema,
)

logger = logging.getLogger('step04')


class JsonFileManager:

    def __init__(self, root_folder: str = None):
        if root_folder is None:
            root_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'contents')
        if not os.path.exists(root_folder):
            os.makedirs(root_folder)
        self.root_folder = root_folder

    def get_content_path(self, content_type: str, content_id: str or None):
        if content_type is None:
            return self.root_folder

        if content_id is None:
            return os.path.join(self.root_folder, f"{content_type}s")

        return os.path.join(self.root_folder, f"{content_type}s", content_id)

    def list_contents(self, content_type: str):
        files = []
        if content_type is None:
            return files
        path = self.get_content_path(content_type, None)
        if path is not None:
            with os.scandir(path) as it:
                for entry in it:
                    files.append(dict(name=entry.name, path=entry.path))
        return files

    def load_contents(self, _schema: dict, content_type: str) -> dict or None:
        contents = []
        files = self.list_contents(content_type)
        for file in files:
            content = self.load_content(_schema, content_type, file['name'])
            contents.append(content)

        return contents

    def load_content(self, _schema: dict, content_type: str, content_id: str) -> dict or None:
        if content_id is None or content_type is None:
            return None

        path = self.get_content_path(content_type, content_id)
        logger.debug(f"Loading content {path}")
        if os.path.exists(path):
            with open(path, mode="r") as f:
                try:
                    item = json.load(f)
                    validate(item, _schema)
                    return item
                except jsonschema.exceptions.ValidationError as ve:
                    logger.error(f"{content_type} {content_id} {ve}")
                except jsonschema.exceptions.SchemaError as se:
                    logger.error(f"{content_type} {content_id} {se}")

        return None

    def save_content(self, _schema: dict, content_type: str, content_id: str, content_data: dict) -> dict or None:
        if content_type is None or content_id is None or content_data is None:
            return

        path = self.get_content_path(content_type, content_id)
        if os.path.exists(os.path.dirname(path)):
            with open(path, mode="w") as f:
                try:
                    validate(content_data, _schema)
                    json.dump(f, content_data)
                    return content_data
                except jsonschema.exceptions.ValidationError as e:
                    logger.error(f"{e}")

        return None

    def delete_content(self, _schema: dict, content_type: str, content_id: str):
        if content_type is None or content_id is None:
            return

        path = self.get_content_path(content_type, content_id)
        if os.path.exists(path):
            os.remove(path)

        return None


class ContentManager(JsonFileManager):
    schema_switcher = {
        'meta': MetaSchema,
        'link': LinkSchema,
        'menu': MenuSchema,
        'item': ItemSchema,
        'node': NodeSchema,
        'page': PageSchema,
        'site': SiteSchema
    }

    def __init__(self, contents_folder: str = None, design_themes: dict = None, host: str = 'localhost'):
        super(ContentManager, self).__init__(root_folder=contents_folder)
        self.design_themes = design_themes
        self.zones = ['main', 'util', 'side', 'info']
        self.host = host
        self.cache = {}
        self.reload_cache()

    def reload_cache(self):
        logger.info(f"Reloading cache ...")
        cached_content = {
            'sites': self.get_items('site'),
            'metas': self.get_items('meta'),
            'links': self.get_items('link'),
            'menus': self.get_items('menu'),
            'items': self.get_items('item'),
            'nodes': self.get_items('node'),
            'pages': self.get_items('page')
        }
        logger.info(f"Cached contents: {cached_content}")

    def close(self):
        logger.info(f"Closed")

    def load_items(self, content_type: str) -> list:
        _schema = self.schema_switcher.get(content_type, None)
        if _schema is not None:
            logger.debug(f"Loading items {content_type}")
            return self.load_contents(_schema, content_type)

        return []

    def load_item(self, content_type: str, content_id: str) -> dict:
        _schema = self.schema_switcher.get(content_type, None)
        logger.debug(f"Loading item {content_type} {content_id}")
        if _schema is not None:
            return self.load_content(_schema, content_type, content_id)

        return dict()

    def save_item(self, content_type: str, content_id: str, data: dict):
        key = f'{content_type}s'
        _schema = self.schema_switcher.get(content_type, None)
        logger.debug(f"Loading item {content_type} {content_id}")
        if _schema is not None:
            self.save_content(_schema, content_type, content_id, data)

    def get_items(self, content_type: str):
        key = f'{content_type}s'
        if self.cache.get(key, None) is None:
            self.cache[key] = {}
            items = self.load_items(content_type)
            for item in items:
                logger.debug(f"Adding item: {item}")
                if item is not None:
                    if item.get('name') is not None:
                        self.cache[key][item['name']] = item

        return self.cache[key]

    def get_item(self, content_type: str, content_id: str) -> dict:
        key = f'{content_type}s'
        if self.cache.get(key, None) is not None:
            if self.cache[key].get(content_id, None) is None:
                item = self.load_item(content_type, content_id)
                self.cache[key][content_id] = item

            return self.cache[key][content_id]

        return {}

    def set_item(self, content_type: str, content_id: str, data: dict):
        key = f'{content_type}s'
        if self.cache.get(key, None) is not None:
            self.save_item(content_type, content_id, data)
            self.cache[key][content_id] = data

        return {}

    def del_item(self, content_type: str, content_id: str):
        key = f'{content_type}s'
        if self.cache.get(key, None) is not None:
            _schema = self.schema_switcher.get(content_type, None)
            logger.debug(f"Deleting item {content_type} {content_id}")
            if _schema is not None:
                self.delete_content(_schema, content_type, content_id)
                del self.cache[key][content_id]

    def set_theme(self, theme):
        if theme in self.design_themes:
            session['theme'] = theme

    def get_theme(self):
        return session.get('theme', 'default')

    def get_site(self):
        return self.cache['sites'][self.host]

    def get_site_meta(self, name: str):
        return self.cache['metas'].get(name, {'name': name, 'data': ''})

    def get_site_link(self, name: str):
        return self.cache['links'].get(name, {'name': name, 'icon': 'fa fa-file', 'text': name, 'link': '#'})

    def get_site_menu(self, name: str):
        return self.cache['menus'].get(name, {'name': name})

    def get_user_menu(self, name: str, role: str):
        menu = self.cache['menus'].get(f'{name}@{role}', None)
        if menu is None:
            menu = self.cache['menus'].get(f'{name}', None)
        else:
            menu['name'] = name
        return menu

    def get_site_node(self, name: str):
        return self.cache['nodes'].get(name, {'name': name})

    def get_site_page(self, name: str):
        return self.cache['pages'].get(name, {'name': name})

    def get_content(self, page: str, template: str):
        content = {
            # use cms jinja functions instead
            # 'site': self.get_item('site', 'localhost'),
            # 'metas': self.get_items('meta'),
            # 'links': self.get_items('link'),
            # 'menus': self.get_items('menu'),
            # 'nodes': self.get_items('node'),
            'page': self.get_item('page', page)
        }
        default_page = {
            'name': page
        }
        if content['page'] is None:
            content['page'] = default_page
        content['page']['path'] = f'/pages/{page}' if page not in ['home'] else f'/{page}'
        content['template'] = content['page'].get('template', template)
        return content, template
