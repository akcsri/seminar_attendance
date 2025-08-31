from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
import os

load_dotenv()  # ← ここを追加！

from models import db  # models.py で定義された db を使う
from config import Config  # ← ここでConfigを読み込む

app = Flask(__name__)
app.config.from_object(Config)  # ← 文字列ではなくクラスを直接渡す

# 正しい初期化順序
db.init_app(app)
mail = Mail(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)