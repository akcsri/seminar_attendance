from flask import request, render_template, redirect, url_for, flash
from app import app, db
from models import Recipient, Seminar, Attendance
from lunch_models import Orderer, MenuItem
import csv
import io
import json
from datetime import datetime

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

@app.route('/delete_menu_item/<int:id>', methods=['POST'])
def delete_menu_item(id):
    """メニュー項目削除"""
    menu_item = Seminar.query.filter_by(id=id, topic='MENU_ITEM').first()
    if menu_item:
        db.session.delete(menu_item)
        db.session.commit()
        flash('メニュー項目を削除しました。', 'success')
    return redirect(url_for('lunch_admin'))

@app.route('/edit_menu_item/<int:id>', methods=['POST'])
def edit_menu_item(id):
    """メニュー項目編集"""
    menu_item = Seminar.query.filter_by(id=id, topic='MENU_ITEM').first()
    if menu_item:
        menu_item.title = request.form['menu_name']
        menu_item.contact = str(request.form['price'])  # 税抜き価格をcontactフィールドに保存
        db.session.commit()
        flash('メニュー項目を更新しました。', 'success')
    else:
        flash('メニュー項目が見つかりません。', 'error')
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
        
        # Check if first row is header
        if not any(col.lower() in ['name', 'price', 'メニュー', '価格'] for col in first_row):
            # First row is data, process it
            stream.seek(0)
            csv_reader = csv.reader(stream)
        
        added_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=1):
            if len(row) < 2:  # At least name and price are required
                errors.append(f'行{row_num}: メニュー名と価格が必要です')
                error_count += 1
                continue
            
            name = row[0].strip() if len(row) > 0 else ''
            price = row[1].strip() if len(row) > 1 else ''
            
            if not name or not price:
                errors.append(f'行{row_num}: メニュー名と価格は必須です')
                error_count += 1
                continue
            
            try:
                # Validate price is a number
                float(price)
                
                menu_item = Seminar(
                    title=name,
                    contact=str(price),  # 税抜き価格をcontactフィールドに保存
                    topic='MENU_ITEM',   # メニュー項目の識別子
                    venue='メニュー項目',
                    speaker='システム',
                    date=None
                )
                db.session.add(menu_item)
                added_count += 1
            except ValueError:
                errors.append(f'行{row_num}: 価格は数値である必要があります')
                error_count += 1
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

@app.route('/edit_orderer/<int:id>', methods=['POST'])
def edit_orderer(id):
    """注文者編集"""
    orderer = Recipient.query.get(id)
    if orderer:
        orderer.name = request.form['name']
        orderer.email = request.form['email']
        orderer.affiliation = request.form.get('affiliation', '注文者')
        db.session.commit()
        flash('注文者情報を更新しました。', 'success')
    else:
        flash('注文者が見つかりません。', 'error')
    return redirect(url_for('lunch_admin'))

@app.route('/delete_orderer/<int:id>', methods=['POST'])
def delete_orderer(id):
    """注文者削除"""
    orderer = Recipient.query.get(id)
    if orderer:
        db.session.delete(orderer)
        db.session.commit()
        flash('注文者を削除しました。', 'success')
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
    """ランチ注文状況表示"""
    # Get all lunch sessions
    lunch_sessions = Seminar.query.filter_by(topic='LUNCH_SESSION').all()
    
    # Get all orders for these sessions
    all_orders = []
    for session in lunch_sessions:
        orders = Attendance.query.filter_by(seminar_id=session.id, status='ordered').all()
        
        for order in orders:
            try:
                # Parse order data from comment field
                order_data = json.loads(order.comment) if order.comment else {}
                selected_items = order_data.get('items', [])
                
                # Get recipient info
                recipient = Recipient.query.get(order.recipient_id)
                
                # Get menu details and calculate total
                item_details = []
                total_price = 0
                for item_id in selected_items:
                    menu_item = Seminar.query.filter_by(id=item_id, topic='MENU_ITEM').first()
                    if menu_item:
                        price = float(menu_item.contact) if menu_item.contact else 0
                        item_details.append({
                            'name': menu_item.title,
                            'price': price
                        })
                        total_price += price
                
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