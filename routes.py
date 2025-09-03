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
    
    # Get seminar and recipient information for context
    seminar = Seminar.query.get(seminar_id)
    recipient = Recipient.query.get(recipient_id)
    
    attendance = Attendance.query.filter_by(seminar_id=seminar_id, recipient_id=recipient_id).first()
    if attendance:
        attendance.status = status
    else:
        attendance = Attendance(seminar_id=seminar_id, recipient_id=recipient_id, status=status)
        db.session.add(attendance)
    db.session.commit()
    
    # Get formatted seminar info directly from new columns
    formatted_seminar = {}
    if seminar:
        formatted_seminar = {
            'open_time': seminar.open_time.strftime('%H:%M') if seminar.open_time else '',
            'end_time': seminar.end_time.strftime('%H:%M') if seminar.end_time else '',
            'speaker_bio': seminar.speaker_bio or '',
            'description': seminar.topic or ''
        }
    
    return render_template('confirm.html', 
                         seminar_id=seminar_id, 
                         recipient_id=recipient_id,
                         seminar=seminar,
                         recipient=recipient,
                         formatted_seminar=formatted_seminar,
                         status=status)

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
    
    # Format seminar information directly from new columns
    formatted_seminars = []
    for seminar in seminars:
        formatted_info = {
            'open_time': seminar.open_time.strftime('%H:%M') if seminar.open_time else '',
            'end_time': seminar.end_time.strftime('%H:%M') if seminar.end_time else '',
            'speaker_bio': seminar.speaker_bio or '',
            'description': seminar.topic or ''
        }
        formatted_seminars.append({
            'seminar': seminar,
            'formatted': formatted_info
        })
    
    return render_template('admin_dashboard.html', 
                         recipients=recipients, 
                         seminars=seminars,
                         formatted_seminars=formatted_seminars,
                         attendances=attendances, 
                         latest_seminar_id=latest_seminar_id)

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
    from datetime import datetime, time
    title = request.form['title']
    date_str = request.form['date']
    # Parse datetime string to datetime object
    date = datetime.fromisoformat(date_str) if date_str else None
    venue = request.form['venue']
    speaker = request.form['speaker']
    topic = request.form['topic']
    contact = request.form['contact']
    
    # Get new fields
    open_time_str = request.form.get('open_time', '').strip()
    end_time_str = request.form.get('end_time', '').strip()
    speaker_bio = request.form.get('speaker_bio', '').strip()
    
    # Parse time fields
    open_time = None
    end_time = None
    
    if open_time_str:
        try:
            open_time = datetime.strptime(open_time_str, '%H:%M').time()
        except ValueError:
            flash('開場時刻の形式が正しくありません (HH:MM)', 'error')
            return redirect(url_for('admin_dashboard'))
    
    if end_time_str:
        try:
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            flash('終了時刻の形式が正しくありません (HH:MM)', 'error')
            return redirect(url_for('admin_dashboard'))
    
    seminar = Seminar(
        title=title, 
        date=date, 
        venue=venue, 
        speaker=speaker, 
        topic=topic, 
        contact=contact,
        open_time=open_time,
        end_time=end_time,
        speaker_bio=speaker_bio
    )
    db.session.add(seminar)
    db.session.commit()
    flash('セミナーが正常に追加されました', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_seminar/<int:id>', methods=['POST'])
def edit_seminar(id):
    from datetime import datetime
    seminar = Seminar.query.get(id)
    if seminar:
        seminar.title = request.form['title']
        date_str = request.form['date']
        # Parse datetime string to datetime object
        seminar.date = datetime.fromisoformat(date_str) if date_str else None
        seminar.venue = request.form['venue']
        seminar.speaker = request.form['speaker']
        topic = request.form['topic']
        seminar.contact = request.form['contact']
        
        # Get new fields
        open_time_str = request.form.get('open_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        speaker_bio = request.form.get('speaker_bio', '').strip()
        
        # Parse time fields
        if open_time_str:
            try:
                seminar.open_time = datetime.strptime(open_time_str, '%H:%M').time()
            except ValueError:
                flash('開場時刻の形式が正しくありません (HH:MM)', 'error')
                return redirect(url_for('admin_dashboard'))
        else:
            seminar.open_time = None
        
        if end_time_str:
            try:
                seminar.end_time = datetime.strptime(end_time_str, '%H:%M').time()
            except ValueError:
                flash('終了時刻の形式が正しくありません (HH:MM)', 'error')
                return redirect(url_for('admin_dashboard'))
        else:
            seminar.end_time = None
        
        seminar.speaker_bio = speaker_bio if speaker_bio else None
        seminar.topic = topic
        db.session.commit()
        flash('セミナー情報が正常に更新されました', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_seminar/<int:id>', methods=['POST'])
def delete_seminar(id):
    seminar = Seminar.query.get(id)
    if seminar:
        # Delete related attendance records first to avoid foreign key constraint violation
        Attendance.query.filter_by(seminar_id=id).delete()
        # Then delete the seminar
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
                    
                    # Update attendance status to 'error' when email sending fails
                    attendance = Attendance.query.filter_by(seminar_id=seminar_id, recipient_id=recipient_id).first()
                    if attendance:
                        attendance.status = 'error'
                    else:
                        # Create new attendance record with error status
                        attendance = Attendance(seminar_id=seminar_id, recipient_id=recipient_id, status='error')
                        db.session.add(attendance)
                    db.session.commit()
        
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
                    
                    # Update attendance status to 'error' when email sending fails
                    attendance = Attendance.query.filter_by(seminar_id=seminar_id, recipient_id=recipient_id).first()
                    if attendance:
                        attendance.status = 'error'
                    else:
                        # Create new attendance record with error status
                        attendance = Attendance(seminar_id=seminar_id, recipient_id=recipient_id, status='error')
                        db.session.add(attendance)
                    db.session.commit()
        
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

@app.route('/get_attendance_data')
def get_attendance_data():
    """Get attendance data for a specific seminar (AJAX endpoint)"""
    seminar_id = request.args.get('seminar_id')
    
    if not seminar_id:
        return []
    
    # Get attendance records with recipient information
    attendances = db.session.query(Attendance, Recipient)\
        .join(Recipient, Attendance.recipient_id == Recipient.id)\
        .filter(Attendance.seminar_id == seminar_id)\
        .all()
    
    attendance_data = []
    for attendance, recipient in attendances:
        attendance_data.append({
            'id': attendance.id,
            'recipient_name': recipient.name,
            'recipient_email': recipient.email,
            'status': attendance.status,
            'comment': attendance.comment or ''
        })
    
    return attendance_data

@app.route('/update_attendance_status', methods=['POST'])
def update_attendance_status():
    """Update attendance status to 'confirmed' for selected attendances"""
    try:
        attendance_ids = request.form.getlist('attendance_ids')
        seminar_id = request.form.get('seminar_id')
        
        if not attendance_ids:
            flash('更新する登録者を選択してください。', 'warning')
            return redirect(url_for('admin_dashboard'))
            
        if not seminar_id:
            flash('対象セミナーを選択してください。', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        updated_count = 0
        
        for attendance_id in attendance_ids:
            attendance = Attendance.query.get(attendance_id)
            if attendance and attendance.seminar_id == int(seminar_id):
                # Only update if not already confirmed
                if attendance.status != 'confirmed':
                    attendance.status = 'confirmed'
                    updated_count += 1
        
        db.session.commit()
        
        if updated_count > 0:
            flash(f'{updated_count}件の登録者のステータスを「confirmed」に更新しました。', 'success')
        else:
            flash('更新対象がありませんでした（既に確認済みまたは無効なデータ）。', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash(f'ステータス更新中にエラーが発生しました: {str(e)}', 'error')

# ===============================
# ランチ等注文管理機能 / Lunch Order Management
# ===============================

@app.route('/lunch_admin')
def lunch_admin():
    """ランチ等注文管理画面"""
    # 注文者データ (Recipientテーブルを流用)
    orderers = Recipient.query.all()
    
    # メニューデータ (Seminarテーブルを流用、topicが"MENU_ITEM"のもの)
    menus = Seminar.query.filter_by(topic='MENU_ITEM').all()
    
    # 注文データ (Attendanceテーブルを流用、seminar_idがメニューセッションのもの)
    lunch_sessions = Seminar.query.filter_by(topic='LUNCH_SESSION').all()
    orders = []
    for session in lunch_sessions:
        session_orders = Attendance.query.filter_by(seminar_id=session.id).all()
        orders.extend(session_orders)
    
    return render_template('lunch_admin.html', 
                         orderers=orderers, 
                         menus=menus, 
                         orders=orders,
                         lunch_sessions=lunch_sessions)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    """メニュー項目追加"""
    menu_name = request.form['menu_name']
    price = request.form['price']
    
    # Seminarテーブルを使ってメニュー項目を保存
    menu_item = Seminar(
        title=menu_name,
        contact=str(price),  # 税抜き価格をcontactフィールドに保存
        topic='MENU_ITEM',   # メニュー項目の識別子
        venue='メニュー項目',
        speaker='システム',
        date=None
    )
    
    db.session.add(menu_item)
    db.session.commit()
    flash(f'メニュー項目「{menu_name}」を追加しました。', 'success')
    
    return redirect(url_for('lunch_admin'))

@app.route('/delete_menu_item/<int:id>', methods=['POST'])
def delete_menu_item(id):
    """メニュー項目削除"""
    menu_item = Seminar.query.filter_by(id=id, topic='MENU_ITEM').first()
    if menu_item:
        db.session.delete(menu_item)
        db.session.commit()
        flash('メニュー項目を削除しました。', 'success')
    return redirect(url_for('lunch_admin'))

@app.route('/import_menu_csv', methods=['POST'])
def import_menu_csv():
    """メニューCSVインポート"""
    try:
        if 'menu_csv_file' not in request.files:
            flash('CSVファイルが選択されていません。', 'error')
            return redirect(url_for('lunch_admin'))
        
        file = request.files['menu_csv_file']
        if file.filename == '':
            flash('CSVファイルが選択されていません。', 'error')
            return redirect(url_for('lunch_admin'))
        
        if not file.filename.lower().endswith('.csv'):
            flash('CSVファイルを選択してください。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Read and process CSV file
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
        csv_reader = csv.reader(stream)
        
        # Skip header row if it exists
        first_row = next(csv_reader, None)
        if not first_row:
            flash('CSVファイルが空です。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Check if first row is header (contains 'menu', 'price', etc.)
        if not any(col.lower() in ['menu', 'price', 'メニュー', '価格'] for col in first_row):
            # First row is data, process it
            stream.seek(0)
            csv_reader = csv.reader(stream)
        
        added_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=1):
            if len(row) < 2:  # At least menu name and price are required
                errors.append(f'行{row_num}: メニュー名と価格が必要です')
                error_count += 1
                continue
            
            menu_name = row[0].strip() if len(row) > 0 else ''
            price_str = row[1].strip() if len(row) > 1 else ''
            
            if not menu_name or not price_str:
                errors.append(f'行{row_num}: メニュー名と価格は必須です')
                error_count += 1
                continue
            
            # Validate price is numeric
            try:
                price = float(price_str)
            except ValueError:
                errors.append(f'行{row_num}: 価格は数値で入力してください')
                error_count += 1
                continue
            
            try:
                menu_item = Seminar(
                    title=menu_name,
                    contact=str(price),
                    topic='MENU_ITEM',
                    venue='メニュー項目',
                    speaker='システム',
                    date=None
                )
                db.session.add(menu_item)
                added_count += 1
            except Exception as e:
                errors.append(f'行{row_num}: データベースエラー - {str(e)}')
                error_count += 1
        
        if added_count > 0:
            db.session.commit()
            flash(f'{added_count}件のメニュー項目を追加しました。', 'success')
        
        if error_count > 0:
            flash(f'{error_count}件のエラーがありました。', 'warning')
            for error in errors[:5]:  # Show first 5 errors
                flash(error, 'error')
            if len(errors) > 5:
                flash(f'他に{len(errors) - 5}件のエラーがあります。', 'error')
                
    except Exception as e:
        db.session.rollback()
        flash(f'CSVインポート中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('lunch_admin'))

@app.route('/import_orderer_csv', methods=['POST'])
def import_orderer_csv():
    """注文者CSVインポート"""
    try:
        if 'orderer_csv_file' not in request.files:
            flash('CSVファイルが選択されていません。', 'error')
            return redirect(url_for('lunch_admin'))
        
        file = request.files['orderer_csv_file']
        if file.filename == '':
            flash('CSVファイルが選択されていません。', 'error')
            return redirect(url_for('lunch_admin'))
        
        if not file.filename.lower().endswith('.csv'):
            flash('CSVファイルを選択してください。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Read and process CSV file
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
        csv_reader = csv.reader(stream)
        
        # Skip header row if it exists
        first_row = next(csv_reader, None)
        if not first_row:
            flash('CSVファイルが空です。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Check if first row is header
        if not any(col.lower() in ['name', 'email', '氏名', 'メール'] for col in first_row):
            # First row is data, process it
            stream.seek(0)
            csv_reader = csv.reader(stream)
        
        added_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=1):
            if len(row) < 2:  # At least name and email are required
                errors.append(f'行{row_num}: 氏名とメールアドレスが必要です')
                error_count += 1
                continue
            
            name = row[0].strip() if len(row) > 0 else ''
            email = row[1].strip() if len(row) > 1 else ''
            
            if not name or not email:
                errors.append(f'行{row_num}: 氏名とメールアドレスは必須です')
                error_count += 1
                continue
            
            # Check if email already exists
            existing_orderer = Recipient.query.filter_by(email=email).first()
            if existing_orderer:
                errors.append(f'行{row_num}: メールアドレス {email} は既に登録されています')
                error_count += 1
                continue
            
            try:
                orderer = Recipient(
                    name=name,
                    email=email,
                    affiliation='注文者',
                    phone=''
                )
                db.session.add(orderer)
                added_count += 1
            except Exception as e:
                errors.append(f'行{row_num}: データベースエラー - {str(e)}')
                error_count += 1
        
        if added_count > 0:
            db.session.commit()
            flash(f'{added_count}件の注文者を追加しました。', 'success')
        
        if error_count > 0:
            flash(f'{error_count}件のエラーがありました。', 'warning')
            for error in errors[:5]:  # Show first 5 errors
                flash(error, 'error')
            if len(errors) > 5:
                flash(f'他に{len(errors) - 5}件のエラーがあります。', 'error')
                
    except Exception as e:
        db.session.rollback()
        flash(f'CSVインポート中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('lunch_admin'))

@app.route('/lunch_order_status')
def lunch_order_status():
    """ランチ等注文状況表示画面"""
    import json
    
    # Get all lunch sessions
    lunch_sessions = Seminar.query.filter_by(topic='LUNCH_SESSION').all()
    
    # Get all menu items
    menus = Seminar.query.filter_by(topic='MENU_ITEM').all()
    menu_dict = {str(menu.id): {'name': menu.title, 'price': float(menu.contact or 0)} for menu in menus}
    
    # Get orders for all sessions
    all_orders = []
    for session in lunch_sessions:
        orders = Attendance.query.filter_by(seminar_id=session.id).all()
        
        for order in orders:
            recipient = Recipient.query.get(order.recipient_id)
            if recipient and order.comment:
                try:
                    # Parse JSON data from comment field
                    order_data = json.loads(order.comment)
                    items = order_data.get('items', [])
                    
                    # Calculate total price
                    total_price = 0
                    item_details = []
                    for item_id in items:
                        if str(item_id) in menu_dict:
                            menu = menu_dict[str(item_id)]
                            item_details.append({
                                'name': menu['name'],
                                'price': menu['price']
                            })
                            total_price += menu['price']
                    
                    all_orders.append({
                        'orderer_name': recipient.name,
                        'ordered_items': item_details,
                        'total_price': total_price,
                        'session': session.title
                    })
                except json.JSONDecodeError:
                    continue
    
    # Calculate totals
    total_before_tax = sum(order['total_price'] for order in all_orders)
    tax_amount = total_before_tax * 0.10  # 10% tax
    total_with_tax = total_before_tax + tax_amount
    
    return render_template('lunch_order_status.html',
                         orders=all_orders,
                         total_before_tax=total_before_tax,
                         tax_amount=tax_amount,
                         total_with_tax=total_with_tax)

@app.route('/send_lunch_order_email', methods=['POST'])
def send_lunch_order_email():
    """ランチ等注文メール送信"""
    from datetime import datetime
    
    try:
        session_title = request.form['session_title']
        deadline = request.form['deadline']
        
        # Create lunch session entry
        deadline_dt = datetime.fromisoformat(deadline)
        
        lunch_session = Seminar(
            title=session_title,
            date=deadline_dt,
            topic='LUNCH_SESSION',
            venue='ランチセッション',
            speaker='システム',
            contact=f'注文期限: {deadline_dt.strftime("%Y年%m月%d日 %H時%M分")}'
        )
        
        db.session.add(lunch_session)
        db.session.commit()
        
        # Get all menu items
        menus = Seminar.query.filter_by(topic='MENU_ITEM').all()
        
        # Get all orderers (recipients)
        orderers = Recipient.query.all()
        
        sent_count = 0
        error_count = 0
        
        for orderer in orderers:
            try:
                # Send lunch order email with menu checkboxes
                send_lunch_order_email_to_recipient(orderer, lunch_session, menus)
                sent_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error sending lunch order email to {orderer.email}: {e}")
        
        if sent_count > 0:
            flash(f'{sent_count}件の注文メールを送信しました。', 'success')
        if error_count > 0:
            flash(f'{error_count}件のメール送信でエラーが発生しました。', 'warning')
    
    except Exception as e:
        db.session.rollback()
        flash(f'メール送信中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('lunch_admin'))

@app.route('/lunch_order_response')
def lunch_order_response():
    """ランチ注文レスポンス処理"""
    import json
    from datetime import datetime
    
    session_id = request.args.get('session_id')
    recipient_id = request.args.get('recipient_id')
    selected_items = request.args.getlist('items')  # Get list of selected menu item IDs
    
    if not session_id or not recipient_id:
        return "無効なリクエストです。", 400
    
    # Create or update order record
    existing_order = Attendance.query.filter_by(
        seminar_id=session_id, 
        recipient_id=recipient_id
    ).first()
    
    # Store selected items as JSON in comment field
    order_data = {
        'items': selected_items,
        'timestamp': datetime.now().isoformat()
    }
    
    if existing_order:
        existing_order.comment = json.dumps(order_data)
        existing_order.status = 'ordered'
    else:
        order = Attendance(
            seminar_id=session_id,
            recipient_id=recipient_id,
            status='ordered',
            comment=json.dumps(order_data)
        )
        db.session.add(order)
    
    db.session.commit()
    
    # Get session and recipient info for confirmation
    session = Seminar.query.get(session_id)
    recipient = Recipient.query.get(recipient_id)
    
    return render_template('lunch_order_confirmation.html',
                         session=session,
                         recipient=recipient,
                         selected_items=selected_items)

def send_lunch_order_email_to_recipient(recipient, lunch_session, menus):
    """Send lunch order email to a specific recipient"""
    # This would use the existing email infrastructure
    # For now, we'll create a placeholder that uses the existing mail_utils
    try:
        from mail_utils import send_email
        
        # Create HTML content with menu checkboxes
        menu_html = ""
        for menu in menus:
            menu_html += f"""
            <div style="margin: 10px 0;">
                <label style="display: flex; align-items: center; gap: 10px;">
                    <input type="checkbox" name="items" value="{menu.id}" style="width: 20px; height: 20px;">
                    <span>{menu.title} - ¥{menu.contact}</span>
                </label>
            </div>
            """
        
        # Create order form URL
        order_url = f"http://127.0.0.1:5001/lunch_order_form?session_id={lunch_session.id}&recipient_id={recipient.id}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>ランチ等注文のご案内</h2>
            <p>こんにちは、{recipient.name} 様</p>
            
            <p><strong>セッション:</strong> {lunch_session.title}</p>
            <p><strong>注文期限:</strong> {lunch_session.contact}</p>
            
            <h3>メニュー選択</h3>
            <p>以下のリンクをクリックして注文ページにアクセスしてください：</p>
            
            <a href="{order_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                注文ページを開く
            </a>
            
            <p>注文期限までにご選択ください。</p>
        </body>
        </html>
        """
        
        send_email(
            to_email=recipient.email,
            subject=f"【ランチ注文】{lunch_session.title}",
            html_content=html_content
        )
        
    except Exception as e:
        print(f"Error sending lunch order email: {e}")
        raise

@app.route('/lunch_order_form')
def lunch_order_form():
    """ランチ注文フォーム表示"""
    session_id = request.args.get('session_id')
    recipient_id = request.args.get('recipient_id')
    
    if not session_id or not recipient_id:
        return "無効なリクエストです。", 400
    
    session = Seminar.query.get(session_id)
    recipient = Recipient.query.get(recipient_id)
    menus = Seminar.query.filter_by(topic='MENU_ITEM').all()
    
    if not session or not recipient:
        return "セッションまたは注文者が見つかりません。", 404
    
    return render_template('lunch_order_form.html',
                         session=session,
                         recipient=recipient,
                         menus=menus)
    
    return redirect(url_for('admin_dashboard'))