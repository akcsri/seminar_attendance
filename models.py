"""
🚫 データベース変更制限について / Database Change Restrictions

このファイルの変更は一切許可されていません。
Changes to this file are strictly prohibited.

理由 / Reasons:
- 既存の運用・連携システムとの整合性維持
- データ移行やマイグレーションによるリスク回避  
- 今後の機能追加は既存のDB構造を前提に行う方針

詳細は CONTRIBUTING.md をご確認ください。
For details, please see CONTRIBUTING.md.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    affiliation = db.Column(db.String(100))
    phone = db.Column(db.String(20))

class Seminar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    venue = db.Column(db.Text)
    speaker = db.Column(db.String(100))
    topic = db.Column(db.String(200))
    contact = db.Column(db.String(100))
    open_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    speaker_bio = db.Column(db.Text)

from sqlalchemy.orm import relationship

class Attendance(db.Model):
    # 既存のカラム定義
    id = db.Column(db.Integer, primary_key=True)  # 🔑 主キーを追加
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'))
    seminar_id = db.Column(db.Integer, db.ForeignKey('seminar.id'))
    status = db.Column(db.String(20))
    comment = db.Column(db.String(500))  # コメント欄を追加
    
    # 🔽 追加するリレーション
    recipient = relationship("Recipient", backref="attendances")
