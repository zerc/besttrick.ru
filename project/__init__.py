from mongokit import Connection

from flask import Flask
from flaskext.mail import Mail, email_dispatched
from flask.ext.assets import Environment, Bundle
from flaskext.markdown import Markdown
from flask_errormail import mail_on_500


app = Flask(__name__)
app.root_path = '/'.join(app.root_path.split('/')[:-1])
app.config.from_object('project.settings')

mail_on_500(app, app.config['ADMINS'])

markdown = Markdown(app)

connection = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])
db = connection.besttrick

assets = Environment(app)
JS_LIBS = (
    'js/jquery.min.js',
    'js/underscore.js',
    'js/backbone.js',
    'js/ejs.js',
    'js/jquery.form.js',
    'js/bootstrap-tooltip.js',
)
JS_PROJECT = (
    'js/tricks.js',
    'js/users.js',
    'js/app.js',
)
final_script_name = 'js/main.js'

if app.config['DEBUG']:
    JS_LIBS = JS_LIBS + JS_PROJECT
elif app.config['OPENED']:
    JS_LIBS = JS_LIBS + (final_script_name,)

js = Bundle(*JS_LIBS, filters='jsmin', output='js/main_min.js')
assets.register('js_all', js)


mail = Mail(app)
def log_message(message, app):
    app.logger.debug(u'\n'.join([message.subject, message.body]))
email_dispatched.connect(log_message)
