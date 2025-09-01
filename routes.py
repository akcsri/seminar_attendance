from flask import request, render_template, redirect, url_for, flash, make_response
from app import app, db
from models import Recipient, Seminar, Attendance
from mailer import send_invitation_email, send_confirmation_email
import csv
import io

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
    """
    Handle confirmation button clicks from confirmation emails.
    This is the ONLY endpoint that should change attendance status to 'confirmed'.
    Email sending functions should never modify attendance status.
    """
    seminar_id = request.args.get('seminar_id')
    recipient_id = request.args.get('recipient_id')
    attendance = Attendance.query.filter_by(seminar_id=seminar_id, recipient_id=recipient_id).first()
    if attendance:
        # Only change status when user explicitly confirms via button click
        attendance.status = "confirmed"
        db.session.commit()
    return "参加確認を受け付けました。"

@app.route('/admin')
def admin_dashboard():
    recipients = Recipient.query.all()
    seminars = Seminar.query.order_by(Seminar.id.desc()).all()
    attendances = Attendance.query.all()
    latest_seminar_id = seminars[0].id if seminars else None
    return render_template('admin_dashboard.html', recipients=recipients, seminars=seminars, attendances=attendances, latest_seminar_id=latest_seminar_id)

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

@app.route('/send_invitation_emails', methods=['POST'])
def send_invitation_emails():
    """Send invitation emails to selected recipients for a specific seminar"""
    try:
        seminar_id = request.form.get('seminar_id')
        recipient_ids = request.form.getlist('recipient_ids')
        
        if not seminar_id:
            flash('セミナーを選択してください。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        if not recipient_ids:
            flash('送信対象の登録者を選択してください。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        seminar = Seminar.query.get(seminar_id)
        if not seminar:
            flash('指定されたセミナーが見つかりません。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        sent_count = 0
        error_count = 0
        
        for recipient_id in recipient_ids:
            recipient = Recipient.query.get(recipient_id)
            if recipient:
                try:
                    send_invitation_email(recipient, seminar)
                    sent_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error sending email to {recipient.email}: {e}")
        
        if sent_count > 0:
            flash(f'{sent_count}件の案内メールを送信しました。', 'success')
        if error_count > 0:
            flash(f'{error_count}件のメール送信でエラーが発生しました。', 'warning')
            
    except Exception as e:
        flash(f'メール送信中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/import_csv', methods=['POST'])
def import_csv():
    """Import recipients from CSV file"""
    try:
        if 'csv_file' not in request.files:
            flash('CSVファイルが選択されていません。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('CSVファイルが選択されていません。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        if not file.filename.lower().endswith('.csv'):
            flash('CSVファイルを選択してください。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Read and process CSV file
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
        csv_reader = csv.reader(stream)
        
        # Skip header row if it exists
        first_row = next(csv_reader, None)
        if not first_row:
            flash('CSVファイルが空です。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Check if first row is header (contains 'name', 'email', etc.)
        if not any(col.lower() in ['name', 'email', 'affiliation', 'phone'] for col in first_row):
            # First row is data, process it
            stream.seek(0)
            csv_reader = csv.reader(stream)
        
        added_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=1):
            if len(row) < 2:  # At least name and email are required
                errors.append(f'行{row_num}: 必要な列が不足しています')
                error_count += 1
                continue
            
            name = row[0].strip() if len(row) > 0 else ''
            email = row[1].strip() if len(row) > 1 else ''
            affiliation = row[2].strip() if len(row) > 2 else ''
            phone = row[3].strip() if len(row) > 3 else ''
            
            if not name or not email:
                errors.append(f'行{row_num}: 名前とメールアドレスは必須です')
                error_count += 1
                continue
            
            # Check if email already exists
            existing_recipient = Recipient.query.filter_by(email=email).first()
            if existing_recipient:
                errors.append(f'行{row_num}: メールアドレス {email} は既に登録されています')
                error_count += 1
                continue
            
            try:
                recipient = Recipient(
                    name=name,
                    email=email,
                    affiliation=affiliation,
                    phone=phone
                )
                db.session.add(recipient)
                added_count += 1
            except Exception as e:
                errors.append(f'行{row_num}: データベースエラー - {str(e)}')
                error_count += 1
        
        if added_count > 0:
            db.session.commit()
            flash(f'{added_count}件の登録者を追加しました。', 'success')
        
        if error_count > 0:
            flash(f'{error_count}件のエラーがありました。', 'warning')
            for error in errors[:5]:  # Show first 5 errors
                flash(error, 'error')
            if len(errors) > 5:
                flash(f'他に{len(errors) - 5}件のエラーがあります。', 'error')
                
    except Exception as e:
        db.session.rollback()
        flash(f'CSVインポート中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/send_confirmation_emails', methods=['POST'])
def send_confirmation_emails():
    """Send confirmation emails to selected recipients for a specific seminar"""
    try:
        recipient_ids = request.form.getlist('recipient_ids')
        seminar_id = request.form.get('seminar_id')
        
        if not recipient_ids:
            flash('送信対象の登録者を選択してください。', 'warning')
            return redirect(url_for('admin_dashboard'))
            
        if not seminar_id:
            flash('送信対象のセミナーを選択してください。', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        seminar = Seminar.query.get(seminar_id)
        if not seminar:
            flash('指定されたセミナーが見つかりません。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        sent_count = 0
        error_count = 0
        
        for recipient_id in recipient_ids:
            recipient = Recipient.query.get(recipient_id)
            if recipient:
                try:
                    send_confirmation_email(recipient, seminar)
                    sent_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error sending confirmation email to {recipient.email}: {e}")
        
        if sent_count > 0:
            flash(f'{sent_count}件の確認メールを送信しました。', 'success')
        if error_count > 0:
            flash(f'{error_count}件のメール送信でエラーが発生しました。', 'warning')
            
    except Exception as e:
        flash(f'確認メール送信中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/export_recipients_csv')
def export_recipients_csv():
    """Export recipients list as CSV"""
    try:
        recipients = Recipient.query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['name', 'email', 'affiliation', 'phone'])
        
        # Write data
        for recipient in recipients:
            writer.writerow([
                recipient.name or '',
                recipient.email or '',
                recipient.affiliation or '',
                recipient.phone or ''
            ])
        
        output.seek(0)
        
        # Add BOM for Excel compatibility with Japanese characters
        csv_content = '\ufeff' + output.getvalue()
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = 'attachment; filename=recipients.csv'
        
        return response
        
    except Exception as e:
        flash(f'CSVエクスポート中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/export_attendance_csv')
def export_attendance_csv():
    """Export attendance information as CSV for a specific seminar"""
    try:
        seminar_id = request.args.get('seminar_id')
        
        if not seminar_id:
            flash('セミナーIDが指定されていません。', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Join attendance data with recipient and seminar information
        attendances = db.session.query(
            Attendance, Recipient, Seminar
        ).join(
            Recipient, Attendance.recipient_id == Recipient.id
        ).join(
            Seminar, Attendance.seminar_id == Seminar.id
        ).filter(
            Attendance.seminar_id == seminar_id
        ).all()
        
        if not attendances:
            flash('指定されたセミナーの出欠データが見つかりません。', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['seminar_title', 'recipient_name', 'status', 'comment'])
        
        # Write data
        for attendance, recipient, seminar in attendances:
            writer.writerow([
                seminar.title or '',
                recipient.name or '',
                attendance.status or '',
                attendance.comment or ''
            ])
        
        output.seek(0)
        
        # Get seminar title for filename
        seminar = Seminar.query.get(seminar_id)
        seminar_title = seminar.title if seminar else 'seminar'
        filename = f'attendance_{seminar_title}.csv'
        
        # Add BOM for Excel compatibility with Japanese characters
        csv_content = '\ufeff' + output.getvalue()
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        flash(f'出欠CSVエクスポート中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))