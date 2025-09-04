import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'akanekocsri@gmail.com'       # ご自身のGmailアドレスに置き換えてください
    MAIL_PASSWORD = 'oqdyyhickkkwfgjx'         # アプリパスワードを使用（通常のパスワード不可）
    
    # APScheduler configuration
    SCHEDULER_API_ENABLED = True
    
    # Base URL for lunch order emails (Render URL)
    BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')