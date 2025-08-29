from app import app, db
from models import Recipient, Seminar, Attendance
from datetime import datetime

with app.app_context():
    # 参加者データ
    recipient1 = Recipient(name="金子明彦", email="akihiko.kaneko@csri-japan.com", affiliation="CSRI", phone="080-1234-5678")
    recipient2 = Recipient(name="Bob Suzuki", email="bob@example.com", affiliation="Kyoto Institute", phone="080-2345-6789")

    # セミナーデータ
    seminar1 = Seminar(
        title="AI and Society",
        date=datetime(2024, 5, 20, 10, 0),
        venue="Tokyo Conference Center",
        speaker="Dr. Yamada",
        topic="Impact of AI on modern society",
        contact="seminar@tokyo.ai"
    )
    seminar2 = Seminar(
        title="Quantum Computing Basics",
        date=datetime(2024, 5, 22, 14, 0),
        venue="Kyoto Tech Hall",
        speaker="Prof. Nakamura",
        topic="Introduction to Quantum Computing",
        contact="seminar@kyoto.qc"
    )

    db.session.add_all([recipient1, recipient2, seminar1, seminar2])
    db.session.commit()

    # 出欠データ
    attendance1 = Attendance(seminar_id=seminar1.id, recipient_id=recipient1.id, status="attend", comment="Looking forward to it.")
    attendance2 = Attendance(seminar_id=seminar2.id, recipient_id=recipient2.id, status="pending", comment="Will confirm soon.")

    db.session.add_all([attendance1, attendance2])
    db.session.commit()

    print("Sample data inserted successfully.")