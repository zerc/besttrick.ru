#!venv/bin/python
# coding: utf-8
from mongokit import Connection

from flask import Flask
from flask.ext.assets import Environment, Bundle
from flaskext.markdown import Markdown

try:
    from flaskext.script import Manager
except ImportError: # Fix this
    from flask.ext.script import Manager
    
from blinker import signal

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
command_manager = Manager(app)

assets = Environment(app)
static = {}
static['js'] = map(lambda x: 'js/%s' % x, (
    'jquery.min.js',
    'underscore.js',
    'backbone.js',
    'backbone-forms.js',
    'ejs.js',
    'jquery.form.js',
    'bootstrap-tooltip.js',
    'jquery.reject.js',
    'jquery.cookie.js',
    'date.format.js',

    'common.js',
    'tricks.js',
    'users.js',
    'achives.js',
    'app.js',
))

static['css'] = map(lambda x: 'css/%s' % x, (
    'backbone-forms.css',
    'base.css',
    'skeleton.css',
    'layout.css',
    'styles.css',
    'jquery.reject.css',
    #'reset.css',
))

## temp
static['js_dev'] =  map(lambda x: 'js/dev/%s.js' % x, (
    'libs/json2',
    'libs/underscore',
    'libs/backbone',
    'libs/backbone.babysitter',
    'libs/backbone.wreqr',
    'libs/backbone.marionette',
    'libs/kickstart',
))
static['js_dev'].insert(0, 'js/jquery.min.js')
static['js_dev'].insert(1, 'js/jquery.reject.js')

static['css_dev'] = map(lambda x: 'css/dev/%s.css' % x, (
    'kickstart/kickstart',
    'kickstart/kickstart-forms',
    'kickstart/kickstart-grid',
    'kickstart/prettify',
    'kickstart/jquery.fancybox-1.3.4',
    'kickstart/kickstart-menus',
    'kickstart/tiptip',
    'kickstart/kickstart-buttons',
    'kickstart/kickstart-slideshow',

    'common',
    'tricks',
    'users',
))

assets.register('js_all', Bundle(*static['js'], filters='jsmin', output='js/main.min.js'))
assets.register('js_dev', Bundle(*static['js_dev'], filters='jsmin', output='js/dev/main.min.js'))

assets.register('css_all', Bundle(*static['css'], filters='cssmin', output='css/dev/main.min.css'))
assets.register('css_dev', Bundle(*static['css_dev'], filters='cssmin', output='css/dev/main.min.css'))


def log_message(message, app):
    app.logger.debug(u'\n'.join([message.subject, message.body]))

if Mail:
    email_dispatched.connect(log_message)
    mail = Mail(app)


# signals
checkin_signal = signal('checkin')
