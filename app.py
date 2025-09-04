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

from flask_migrate import Migrate

migrate = Migrate(app, db)

# Initialize extensions
db.init_app(app)
mail = Mail(app)
scheduler = APScheduler()
scheduler.init_app(app)

# Import routes
from routes import *
from lunch_route import *

# Add custom Jinja2 filters for date formatting
@app.template_filter('japanese_date')
def japanese_date_filter(date):
    """Format date in Japanese style with day of week"""
    if not date:
        return '日時未定'
    
    # Japanese day names
    japanese_days = {
        'Monday': '月',
        'Tuesday': '火', 
        'Wednesday': '水',
        'Thursday': '木',
        'Friday': '金',
        'Saturday': '土',
        'Sunday': '日'
    }
    
    # Format: 9月2日（火）
    month = date.month
    day = date.day
    day_name = japanese_days.get(date.strftime('%A'), date.strftime('%a'))
    
    return f'{month}月{day}日（{day_name}）'

@app.template_filter('japanese_time')  
def japanese_time_filter(date):
    """Format time in Japanese style"""
    if not date:
        return ''
    return date.strftime('%H:%M')

# Start scheduler after everything is set up
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Import scheduler tasks after app context is available
        import scheduler as scheduler_tasks
        scheduler.start()
    # Set use_reloader=False to prevent duplicate APScheduler instances
    app.run(debug=True, use_reloader=False)
else:
    # For production/testing, import scheduler tasks and start scheduler
    with app.app_context():
        import scheduler as scheduler_tasks
        scheduler.start()