#!venv/bin/python
# -*- coding: utf-8 -*-
from mongokit import Connection

from flask import Flask
from flask.ext.assets import Environment, Bundle
from flaskext.markdown import Markdown

try:
    from flaskext.mail import Mail, email_dispatched
    from flask_errormail import mail_on_500
except ImportError:
    Mail, email_dispatched, mail_on_500 = None, None, None

## {{{ http://code.activestate.com/recipes/576563/ (r1)
def cached_property(f):
    """returns a cached property that is calculated by function f"""
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x
        
    return property(get)
## end of http://code.activestate.com/recipes/576563/ }}}


class MyFlask(Flask):
    @cached_property
    def connection(self):
        return Connection(self.config['MONGODB_HOST'], self.config['MONGODB_PORT'])

    @cached_property
    def db(self):
        return getattr(self.connection, self.config['MONGODB_DB'])


app = MyFlask(__name__)
app.root_path = '/'.join(app.root_path.split('/')[:-1])
app.config.from_object('project.settings')


if mail_on_500: mail_on_500(app, app.config['ADMINS'])

markdown = Markdown(app)

assets = Environment(app)
JS_LIBS = (
    'js/jquery.min.js',
    'js/underscore.js',
    'js/backbone.js',
    'js/ejs.js',
    'js/jquery.form.js',
    'js/bootstrap-tooltip.js',
    'js/jquery.reject.js',
    'js/jquery.cookie.js',

    'js/common.js',
    'js/tricks.js',
    'js/users.js',
    'js/app.js',
)

js = Bundle(*JS_LIBS, filters='jsmin', output='js/main.min.js')
assets.register('js_all', js)


def log_message(message, app):
    app.logger.debug(u'\n'.join([message.subject, message.body]))

if Mail:
    email_dispatched.connect(log_message)
    mail = Mail(app)
