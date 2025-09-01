from flask import Flask
from models import Recipient, Seminar, Attendance, db
from config import Config
from flask_mail import Mail
from mailer import send_confirmation_email  # Use the consistent version from mailer.py

app = Flask(__name__)
app.config.from_object(Config)

# 拡張の初期化
db.init_app(app)
mail = Mail(app)  # これが current_app.extensions['mail'] に登録される

@app.route('/test_confirmation_email')
def test_confirmation_email():
    """
    確認メール送信テスト
    注意: この関数はメール送信のみを行い、Attendance.statusを変更しません
    """
    with app.app_context():
        seminar_id = 2
        seminar = db.session.get(Seminar, seminar_id)
        if not seminar:
            return "セミナーID 2 が見つかりませんでした。"

        attendances = Attendance.query.filter_by(seminar_id=seminar_id, status='attend').all()
        if not attendances:
            return "出席者が見つかりませんでした。"

        count = 0
        for attendance in attendances:
            # 確認: メール送信前のステータス
            original_status = attendance.status
            
            recipient = db.session.get(Recipient, attendance.recipient_id)
            if recipient:
                # メール送信（ステータスは変更されないはず）
                send_confirmation_email(recipient, seminar)
                
                # 確認: メール送信後もステータスが変わっていないことを検証
                db.session.refresh(attendance)
                if attendance.status != original_status:
                    return f"エラー: メール送信時にステータスが {original_status} から {attendance.status} に変更されました"
                
                count += 1

        return f"{count} 件の確認メールを送信しました。ステータスは変更されていません。"

if __name__ == '__main__':
    app.run(debug=True)