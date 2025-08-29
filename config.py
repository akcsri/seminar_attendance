# app.py または config.py の先頭で
from dotenv import load_dotenv
load_dotenv()

import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'akanekocsri@gmail.com'       # ご自身のGmailアドレスに置き換えてください
    MAIL_PASSWORD = 'oqdyyhickkkwfgjx'         # アプリパスワードを使用（通常のパスワード不可）