from app import app, db
import models  # モデルを読み込むことで SQLAlchemy が認識

# アプリケーションコンテキスト内でテーブル作成
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")