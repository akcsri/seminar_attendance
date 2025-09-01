from flask import Flask
from models import Recipient, Seminar, Attendance, db
from mailer import send_confirmation_email
from config import Config
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

# 拡張の初期化
db.init_app(app)
mail = Mail(app)  # ← これが current_app.extensions['mail'] に登録される

@app.route('/test_confirmation_email')
def test_confirmation_email():
    with app.app_context():
        seminar_id = 2
        seminar = Seminar.query.get(seminar_id)
        if not seminar:
            return "セミナーID 2 が見つかりませんでした。"

        attendances = Attendance.query.filter_by(seminar_id=seminar_id, status='attend').all()
        if not attendances:
            return "出席者が見つかりませんでした。"

        count = 0
        for attendance in attendances:
            recipient = Recipient.query.get(attendance.recipient_id)
            if recipient:
                send_confirmation_email(recipient, seminar)
                count += 1

        return f"{count} 件の確認メールを送信しました。"

if __name__ == '__main__':
    app.run(debug=True)

app = Flask(__name__)
app.config.from_object(Config)  # ← Configクラスを適用
db.init_app(app)

@app.route('/test_confirmation_email')
def test_confirmation_email():
    with app.app_context():
        seminar_id = 2
        seminar = Seminar.query.get(seminar_id)
        if not seminar:
            return "セミナーID 2 が見つかりませんでした。"

        attendances = Attendance.query.filter_by(seminar_id=seminar_id, status='attend').all()
        if not attendances:
            return "出席者が見つかりませんでした。"

        count = 0
        for attendance in attendances:
            recipient = Recipient.query.get(attendance.recipient_id)
            if recipient:
                send_confirmation_email(recipient, seminar)
                count += 1

        return f"{count} 件の確認メールを送信しました。"

if __name__ == '__main__':
    app.run(debug=True)