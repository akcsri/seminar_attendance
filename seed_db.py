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
        # Add the specific seminar mentioned in the issue (ID: 4)
        seminar3 = Seminar(
            title="Future Technologies",
            date=datetime(2024, 12, 20, 15, 30),
            venue="Osaka Innovation Center",
            speaker="Prof. Tanaka",
            topic="Emerging technologies for 2025",
            contact="seminar@osaka.tech"
        )
        seminar4 = Seminar(
            title="Advanced Machine Learning",
            date=datetime(2025, 9, 2, 12, 2),
            venue="Tokyo Tech University",
            speaker="Dr. Sato",
            topic="Deep learning advancements",
            contact="seminar@tokyo.tech"
        )
        db.session.add_all([seminar1, seminar2, seminar3, seminar4])
        print("Added seminars")
    
    db.session.commit()
    
    # Add attendance data if it doesn't exist
    if Attendance.query.first() is None:
        # Get seminars and recipients
        seminars = Seminar.query.all()
        recipients = Recipient.query.all()
        
        if seminars and recipients:
            # セミナー1に参加者1が出席
            attendance1 = Attendance(seminar_id=seminars[0].id, recipient_id=recipients[0].id, status="attend")
            # セミナー4（問題のセミナー）に参加者1が出席予定
            if len(seminars) >= 4:
                attendance4 = Attendance(seminar_id=seminars[3].id, recipient_id=recipients[0].id, status="attend")
                db.session.add_all([attendance1, attendance4])
            else:
                db.session.add(attendance1)
            db.session.commit()
            print("Added attendance data")
    
    print("Database setup completed successfully.")