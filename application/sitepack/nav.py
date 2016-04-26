from flask_nav import Nav
from dominate import tags
from flask_nav.elements import NavigationItem, View
from flask_bootstrap.nav import BootstrapRenderer, sha1
from flask import url_for, current_app, g, request
from .babel_by_url import get_language_code

class LocalizedView(View):
    def __init__(self, text, endpoint, language_code=None, *args, **kwargs):
        self.language_code = language_code
        super(LocalizedView, self).__init__(text, endpoint, *args, **kwargs)

    def get_url(self):
          return '/{}{}'.format(self.language_code or get_language_code(),
              super(LocalizedView, self).get_url())

    @property
    def active(self):
        # middleware has already trimmed the language_code prefix,
        # so [unless it's a language switcher], consult our ancestors :)
        return (
            (not self.language_code or
                self.language_code==get_language_code()) and
            request.path==super(LocalizedView, self).get_url())


class ExtendedNavbar(NavigationItem):
    def __init__(self, title, root_class='navbar navbar-default', items=[], right_items=[]):
        self.title = title
        self.root_class = root_class
        self.items = items
        self.right_items = right_items

class CustomBootstrapRenderer(BootstrapRenderer):

    def visit_ExtendedNavbar(self, node):
        # create a navbar id that is somewhat fixed, but do not leak any
        # information about memory contents to the outside
        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        root = tags.nav() if self.html5 else tags.div(role='navigation')
        root['class'] = node.root_class

        cont = root.add(tags.div(_class='container-fluid'))

        # collapse button
        header = cont.add(tags.div(_class='navbar-header'))
        btn = header.add(tags.button())
        btn['type'] = 'button'
        btn['class'] = 'navbar-toggle collapsed'
        btn['data-toggle'] = 'collapse'
        btn['data-target'] = '#' + node_id
        btn['aria-expanded'] = 'false'
        btn['aria-controls'] = 'navbar'

        btn.add(tags.span('Toggle navigation', _class='sr-only'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))

        # title may also have a 'get_url()' method, in which case we render
        # a brand-link
        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                header.add(tags.a(node.title.text, _class='navbar-brand',
                                  href=node.title.get_url()))
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = cont.add(tags.div(
            _class='navbar-collapse collapse',
            id=node_id,
        ))
        bar_list = bar.add(tags.ul(_class='nav navbar-nav'))
        for item in node.items:
            bar_list.add(self.visit(item))

        if node.right_items:
            right_bar_list = bar.add(tags.ul(_class='nav navbar-nav navbar-right'))
            for item in node.right_items:
                right_bar_list.add(self.visit(item))

        return root

def init_custom_nav_renderer(app):
    # For some reason, this didn't seem to do anything...
    app.extensions['nav_renderers']['bootstrap'] = (__name__, 'CustomBootstrapRenderer')
    # ... but this worked. Weird.
    app.extensions['nav_renderers'][None] = (__name__, 'CustomBootstrapRenderer')

nav = Nav()
