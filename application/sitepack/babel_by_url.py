import flask_babel
from flask import request, url_for, current_app, g
from flask_nav.elements import View

class NotSupported(Exception):
    pass

class BabelByUrl(object):
    app = None
    babel = None
    default_locale = None
    translations = []
    language = []
    locale = None

    def __init__(self, app=None, *args, **kwargs):
        if app is not None:
            self.init_app(app)

    def init_app(self, app, *args, **kwargs):
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['babel_by_url'] = self
        self.babel = app.extensions.get('babel',
            flask_babel.Babel(app, *args, **kwargs))
        self.default_locale = self.babel.default_locale
        self.translations = self.babel.list_translations()
        self.languages = [l.language for l in self.translations]
        if not self.default_locale.language in self.languages:
            self.loanguages.insert(0, self.default_locale.language)
        self.locale = self.default_locale
        
        @self.babel.localeselector
        def get_locale():
            return self.locale

        @app.before_request
        def before_request():
            self.set_locale_from_url()
            g.languages = self.languages
            g.default_language = self.default_locale.language
            g.language = self.locale.language
            g.is_rtl = self.locale.character_order=='right-to-left'

        app.context_processor(self.context_processor)

    def set_locale_from_url(self):
        l = self._locale_from_url()
        if l!=self.locale:
            self.locale = l
            flask_babel.refresh()

    def _locale_from_url(self):
        try:
            path = request.path
        except:  # not in a request context
            return self.locale
        for tr in self.translations:
            if path.startswith('/{}/'.format(tr.language)):
                return tr
        return self.babel.default_locale

    def _language_code_or_nothing(self, language=None):
        if language is None:
            language=self.locale.language
        if language==self.default_locale.language:
            return ''
        return language

    def babel_url_for(self, endpoint, babel_language=None, **values):
        try:
            blueprint, view = endpoint.split('.')
        except:
            raise NotSupported('Endpoint should be of the explicit form "blueprint.view"')
        babel_language = self._language_code_or_nothing(babel_language)
        url = url_for(endpoint, **values)
        if babel_language:
            return('/{}{}'.format(babel_language, url))
        return url

    def babel_config(self, key, babel_language=None):
        babel_language = self._language_code_or_nothing(babel_language)
        if babel_language:
            return self.app.config.get(
                '{}_{}'.format(key,babel_language.upper()),
                self.app.config.get(key))
        return self.app.config.get(key)

    def context_processor(self):
        return {
            'babel_url_for': self.babel_url_for,
            'babel_config': self.babel_config,
        }

    def register_blueprint(self, blueprint, **options):
        try:
            url_prefix=options.pop('url_prefix')
        except:
            url_prefix=''
        self.app.register_blueprint(blueprint, url_prefix=url_prefix, **options)
        locales=set(self.translations)
        locales.add(self.default_locale)
        for l in locales:
            self.app.register_blueprint(blueprint,
                url_prefix='{}/{}'.format(url_prefix, l.language),
                **options)

### helper functions

def babel_url_for(endpoint, babel_language=None, **values):
    return current_app.extensions['babel_by_url'].babel_url_for(
        endpoint, babel_language, **values)

def babel_config(key, babel_language=None):
    return current_app.extensions['babel_by_url'].babel_config(key, babel_language)
