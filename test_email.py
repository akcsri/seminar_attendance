from app import app
from models import Seminar, Recipient
from mail_utils import send_invitation_email
from datetime import datetime

# テスト用セミナーと参加者
sample_seminar = Seminar(
    id=1,
    title="AIと社会",
    date=datetime(2024, 5, 20, 10, 0),
    venue="東京会議センター",
    speaker="山田博士",
    topic="AIの社会的影響",
    contact="seminar@tokyo.ai"
)

sample_recipient = Recipient(
    id=1,
    name="金子 明彦",
    email="akihiko.kaneko@csri-japan.com",
    affiliation="東京大学",
    phone="080-1234-5678"
)

# Flaskアプリのコンテキスト内でメール送信
with app.app_context():
    try:
        send_invitation_email(sample_recipient, sample_seminar)
        print("Test invitation email sent to akihiko.kaneko@csri-japan.com.")
    except Exception as e:
        print("メール送信失敗:", e)