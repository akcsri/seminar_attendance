from app import app  # app.py から Flask アプリをインポート
from models import Seminar, Recipient
from mailer import send_invitation_email

with app.app_context():  # Flask アプリのコンテキストを明示的に使用
    seminar = Seminar.query.order_by(Seminar.date.desc()).first()

    if seminar:
        recipients = Recipient.query.all()
        for recipient in recipients:
            send_invitation_email(recipient, seminar)
        print(f"{len(recipients)} 件の案内メールを送信しました（セミナー: {seminar.title}）")
    else:
        print("セミナー情報が見つかりませんでした。")