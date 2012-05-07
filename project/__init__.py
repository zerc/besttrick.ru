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

scripts_names = ('js/underscore.js', 'js/backbone.js', 'js/ejs.js',)
project_scripts = ('js/tricks.js', 'js/users.js', 'js/app.js')
final_script_name = 'js/main.js'

if (app.config['DEBUG']):
    scripts_names = scripts_names + project_scripts
else:
    scripts_names = scripts_names + (final_script_name,)

js = Bundle(*scripts_names, filters='jsmin', output='js/main_min.js')
assets.register('js_all', js)


mail = Mail(app)
def log_message(message, app):
    app.logger.debug(u'\n'.join([message.subject, message.body]))
email_dispatched.connect(log_message)
