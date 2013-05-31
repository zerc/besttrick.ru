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
static['js'] = (
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
)

static['css'] = (
    'backbone-forms.css',
    'base.css',
    'skeleton.css',
    'layout.css',
    'styles.css',
    'jquery.reject.css',
    #'reset.css',
)

def make_bundles(bundle_type=''):
    if bundle_type: bundle_type = '/%s' % bundle_type
    for k in static.keys():
        filenames = ['%s%s/%s' % (k, bundle_type, x) for x in static[k]]
        filter_name = '%smin' % k
        output = '%s/main.min.%s' % (k, k)
        assets.register(k+bundle_type+'_all', Bundle(*filenames, filters=filter_name, output=output))

make_bundles()
#make_bundles('dev')


def log_message(message, app):
    app.logger.debug(u'\n'.join([message.subject, message.body]))

if Mail:
    email_dispatched.connect(log_message)
    mail = Mail(app)


# signals
checkin_signal = signal('checkin')
