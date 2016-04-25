import flask_babel
from flask import request, url_for, current_app, g, session
from flask_nav.elements import View

class LanguageCodeFromPathMiddleware(object):
    def __init__(self, app, babel_by_url):
        self.app = app
        self.babel_by_url = babel_by_url

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        language_code = self.babel_by_url.language_code_from_path(path)
        if language_code:
            environ['PATH_INFO'] = path[1+len(language_code):]
        environ['LANGUAGE_CODE_FROM_URL'] = language_code
        return self.app(environ, start_response)

class BabelByUrl(object):
    app = None
    babel = None
    default_locale = None
    locales = []
    locale_map = {}

    def __init__(self, app=None, *args, **kwargs):
        if app is not None:
            self.init_app(app)

    def get_language_code(self):
        try:
            return session['language_code']
        except:
            return self.default_locale.language

    def set_language_code(self, language_code):
        session['language_code'] = language_code
        session['language_direction'] = \
            self.lookup_locale().character_order=='right-to-left' and 'rtl' \
                or 'ltr'

    def lookup_locale(self, language_code=None):
        return self.locale_map.get(
            language_code or self.get_language_code(),
            self.default_locale)

    def init_app(self, app, *args, **kwargs):
        self.app = app
        app.wsgi_app = LanguageCodeFromPathMiddleware(app.wsgi_app, self)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['babel_by_url'] = self
        self.babel = app.extensions.get('babel',
            flask_babel.Babel(app, *args, **kwargs))
        self.default_locale = self.babel.default_locale
        locales = set(self.babel.list_translations())
        locales.add(self.default_locale)
        self.locale_map = dict([(l.language, l) for l in locales])
        
        @self.babel.localeselector
        def get_locale():
            return self.lookup_locale()

        @app.before_request
        def init_request_locale():
            language_code = request.environ.get('LANGUAGE_CODE_FROM_URL')
            if language_code and language_code!=self.get_language_code():
                self.set_language_code(language_code)
                flask_babel.refresh()

        app.context_processor(self.context_processor)

    def language_code_from_path(self, path):
        for l in self.locale_map.keys():
            if path.startswith('/{}/'.format(l)):
               return l
        return None

    def babel_config(self, key, babel_language=None):
        babel_language = babel_language or self.get_language_code()
        return self.app.config.get(
            '{}_{}'.format(key,babel_language.upper()),
            self.app.config.get(key))

    def context_processor(self):
        return {
            'babel_config': self.babel_config,
        }

def get_language_code():
    return current_app.extensions['babel_by_url'].get_language_code()

def babel_config(key, babel_language=None):
    return current_app.extensions['babel_by_url'].babel_config(key, babel_language)
