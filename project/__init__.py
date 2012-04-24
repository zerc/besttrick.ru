from mongokit import Connection

from flask import Flask
from flaskext.mail import Mail, email_dispatched
from flask.ext.assets import Environment, Bundle


app = Flask(__name__)
app.root_path = '/'.join(app.root_path.split('/')[:-1])
app.config.from_object('project.settings')

connection = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])
db = connection.besttrick

assets = Environment(app)
js = Bundle('js/underscore.js','js/backbone.js','js/ejs.js','js/main.js',
            filters='jsmin', output='js/main_min.js')
assets.register('js_all', js)


mail = Mail(app)
def log_message(message, app):
    app.logger.debug(u'\n'.join([message.subject, message.body]))
email_dispatched.connect(log_message)
