from app import app, db
from models import Recipient, Seminar, Attendance
from datetime import datetime

with app.app_context():
    # Check if recipients and seminars exist
    recipients_exist = Recipient.query.first() is not None
    seminars_exist = Seminar.query.first() is not None
    
    if not recipients_exist:
        # 参加者データ
        recipient1 = Recipient(name="金子明彦", email="akihiko.kaneko@csri-japan.com", affiliation="CSRI", phone="080-1234-5678")
        recipient2 = Recipient(name="Bob Suzuki", email="bob@example.com", affiliation="Kyoto Institute", phone="080-2345-6789")
        db.session.add_all([recipient1, recipient2])
        print("Added recipients")
    
    if not seminars_exist:
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
        db.session.add_all([seminar1, seminar2])
        print("Added seminars")
    
    db.session.commit()
    
    # Add attendance data if it doesn't exist
    if Attendance.query.first() is None:
        # Get the first seminar and recipient
        seminar1 = Seminar.query.first()
        recipient1 = Recipient.query.first()
        if seminar1 and recipient1:
            attendance1 = Attendance(seminar_id=seminar1.id, recipient_id=recipient1.id, status="attend")
            db.session.add(attendance1)
            db.session.commit()
            print("Added attendance data")
    
    print("Database setup completed successfully.")