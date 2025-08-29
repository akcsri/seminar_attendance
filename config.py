class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:csri2025@localhost/seminar_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'akanekocsri@gmail.com'       # ご自身のGmailアドレスに置き換えてください
    MAIL_PASSWORD = 'oqdyyhickkkwfgjx'         # アプリパスワードを使用（通常のパスワード不可）