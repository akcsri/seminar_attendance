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
    venue = db.Column(db.String(200))
    speaker = db.Column(db.String(100))
    topic = db.Column(db.String(200))
    contact = db.Column(db.String(100))

from sqlalchemy.orm import relationship

class Attendance(db.Model):
    # 既存のカラム定義
    id = db.Column(db.Integer, primary_key=True)  # 🔑 主キーを追加
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'))
    seminar_id = db.Column(db.Integer, db.ForeignKey('seminar.id'))
    status = db.Column(db.String(20))
    
    # 🔽 追加するリレーション
    recipient = relationship("Recipient", backref="attendances")
