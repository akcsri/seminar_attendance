from flask import request, render_template, redirect, url_for
from app import app, db
from models import Recipient, Seminar, Attendance
from mailer import send_invitation_email

@app.route('/respond')
def respond():
    seminar_id = request.args.get('seminar_id')
    recipient_id = request.args.get('recipient_id')
    status = request.args.get('status')
    attendance = Attendance.query.filter_by(seminar_id=seminar_id, recipient_id=recipient_id).first()
    if attendance:
        attendance.status = status
    else:
        attendance = Attendance(seminar_id=seminar_id, recipient_id=recipient_id, status=status)
        db.session.add(attendance)
    db.session.commit()
    return render_template('confirm.html', seminar_id=seminar_id, recipient_id=recipient_id)

@app.route('/confirm')
def confirm():
    seminar_id = request.args.get('seminar_id')
    recipient_id = request.args.get('recipient_id')
    attendance = Attendance.query.filter_by(seminar_id=seminar_id, recipient_id=recipient_id).first()
    if attendance:
        attendance.status = "confirmed"
        db.session.commit()
    return "参加確認を受け付けました。"

@app.route('/admin')
def admin_dashboard():
    recipients = Recipient.query.all()
    seminars = Seminar.query.all()
    attendances = Attendance.query.all()
    return render_template('admin.html', recipients=recipients, seminars=seminars, attendances=attendances)

@app.route('/add_recipient', methods=['POST'])
def add_recipient():
    name = request.form['name']
    email = request.form['email']
    affiliation = request.form['affiliation']
    phone = request.form['phone']
    recipient = Recipient(name=name, email=email, affiliation=affiliation, phone=phone)
    db.session.add(recipient)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_recipient/<int:id>', methods=['POST'])
def edit_recipient(id):
    recipient = Recipient.query.get(id)
    if recipient:
        recipient.name = request.form['name']
        recipient.email = request.form['email']
        recipient.affiliation = request.form['affiliation']
        recipient.phone = request.form['phone']
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_recipient/<int:id>', methods=['POST'])
def delete_recipient(id):
    recipient = Recipient.query.get(id)
    if recipient:
        db.session.delete(recipient)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_seminar', methods=['POST'])
def add_seminar():
    title = request.form['title']
    date = request.form['date']
    venue = request.form['venue']
    speaker = request.form['speaker']
    topic = request.form['topic']
    contact = request.form['contact']
    seminar = Seminar(title=title, date=date, venue=venue, speaker=speaker, topic=topic, contact=contact)
    db.session.add(seminar)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_seminar/<int:id>', methods=['POST'])
def edit_seminar(id):
    seminar = Seminar.query.get(id)
    if seminar:
        seminar.title = request.form['title']
        seminar.date = request.form['date']
        seminar.venue = request.form['venue']
        seminar.speaker = request.form['speaker']
        seminar.topic = request.form['topic']
        seminar.contact = request.form['contact']
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_seminar/<int:id>', methods=['POST'])
def delete_seminar(id):
    seminar = Seminar.query.get(id)
    if seminar:
        db.session.delete(seminar)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_recipient/<int:id>', methods=['GET'])
def show_edit_recipient(id):
    recipient = Recipient.query.get_or_404(id)
    return render_template('edit_recipient.html', recipient=recipient)

@app.route('/edit_seminar/<int:id>', methods=['GET'])
def show_edit_seminar(id):
    seminar = Seminar.query.get_or_404(id)
    return render_template('edit_seminar.html', seminar=seminar)

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    seminar_id = request.form['seminar_id']
    recipient_id = request.form['recipient_id']
    comment = request.form['comment']

    attendance = Attendance.query.filter_by(seminar_id=seminar_id, recipient_id=recipient_id).first()
    if attendance:
        attendance.comment = comment
        db.session.commit()
        return "コメントを送信しました。ありがとうございました。"
    else:
        return "出欠情報が見つかりませんでした。"
    
from flask import request, render_template
from models import Seminar, Attendance, Recipient

@app.route('/attendance_status', methods=['GET'])
def attendance_status():
    seminars = Seminar.query.order_by(Seminar.date.desc()).all()
    latest_seminar_id = seminars[0].id if seminars else None

    seminar_id = request.args.get('seminar_id', latest_seminar_id, type=int)
    selected_seminar = Seminar.query.get(seminar_id) if seminar_id else None

    attendances = []
    if selected_seminar:
        attendances = Attendance.query.filter_by(seminar_id=seminar_id).all()

    return render_template(
        'attendance_status_template.html',
        seminars=seminars,
        latest_seminar_id=latest_seminar_id,
        selected_seminar=selected_seminar,
        attendances=attendances
    )