from flask import Flask
app = Flask(__name__)
from app import routes

# For jinja template testing purposes
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.run(debug=True, host='0.0.0.0')
