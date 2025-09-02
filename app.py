from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
import os

load_dotenv()

from models import db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail = Mail(app)
scheduler = APScheduler()
scheduler.init_app(app)

# Import routes
from routes import *

# Start scheduler after everything is set up
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Import scheduler tasks after app context is available
        import scheduler as scheduler_tasks
        scheduler.start()
    app.run(debug=True)
else:
    # For production/testing, import scheduler tasks and start scheduler
    with app.app_context():
        import scheduler as scheduler_tasks
        scheduler.start()