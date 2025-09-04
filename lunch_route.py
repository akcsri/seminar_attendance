from flask import request, render_template, redirect, url_for, flash
from app import app, db
from lunch_models import Orderer, Menu
import csv
import io
from datetime import datetime

# ===============================
# ランチ等注文管理機能 / Lunch Order Management
# ===============================

@app.route('/lunch_admin')
def lunch_admin():
    """ランチ等注文管理画面"""
    # 注文者データ (Ordererテーブルを使用)
    orderers = Orderer.query.all()
    
    # メニューデータ (Menuテーブルを使用)
    menus = Menu.query.all()
    
    return render_template('lunch_admin.html', 
                         orderers=orderers, 
                         menus=menus)

@app.route('/delete_menu_item/<int:id>', methods=['POST'])
def delete_menu_item(id):
    """メニュー項目削除"""
    menu_item = Menu.query.get(id)
    if menu_item:
        db.session.delete(menu_item)
        db.session.commit()
        flash('メニュー項目を削除しました。', 'success')
    return redirect(url_for('lunch_admin'))

@app.route('/edit_menu_item/<int:id>', methods=['POST'])
def edit_menu_item(id):
    """メニュー項目編集"""
    menu_item = Menu.query.get(id)
    if menu_item:
        menu_item.name = request.form['menu_name']
        menu_item.price_excl_tax = float(request.form['price'])
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
                price_value = float(price)
                
                menu_item = Menu(
                    name=name,
                    price_excl_tax=price_value
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
    orderer = Orderer.query.get(id)
    if orderer:
        orderer.name = request.form['name']
        orderer.email = request.form['email']
        # Update order items if provided
        orderer.item_1 = request.form.get('item_1', '')
        orderer.item_2 = request.form.get('item_2', '')
        orderer.item_3 = request.form.get('item_3', '')
        orderer.item_4 = request.form.get('item_4', '')
        orderer.item_5 = request.form.get('item_5', '')
        db.session.commit()
        flash('注文者情報を更新しました。', 'success')
    else:
        flash('注文者が見つかりません。', 'error')
    return redirect(url_for('lunch_admin'))

@app.route('/delete_orderer/<int:id>', methods=['POST'])
def delete_orderer(id):
    """注文者削除"""
    orderer = Orderer.query.get(id)
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
            existing_orderer = Orderer.query.filter_by(email=email).first()
            if existing_orderer:
                errors.append(f'行{row_num}: メールアドレス {email} は既に登録されています')
                error_count += 1
                continue
            
            try:
                orderer = Orderer(
                    name=name,
                    email=email,
                    item_1='',
                    item_2='',
                    item_3='',
                    item_4='',
                    item_5=''
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
    # Get all orderers with their orders
    orderers = Orderer.query.all()
    
    # Calculate order summary
    order_summary = []
    item_aggregation = {}  # Track item aggregation: {item_name: {'quantity': count, 'price': price}}
    
    for orderer in orderers:
        if any([orderer.item_1, orderer.item_2, orderer.item_3, orderer.item_4, orderer.item_5]):
            # Get menu details and calculate total
            ordered_items = []
            total_price = 0
            
            for item_name in [orderer.item_1, orderer.item_2, orderer.item_3, orderer.item_4, orderer.item_5]:
                if item_name:
                    menu_item = Menu.query.filter_by(name=item_name).first()
                    if menu_item:
                        ordered_items.append({
                            'name': menu_item.name,
                            'price': float(menu_item.price_excl_tax)
                        })
                        total_price += float(menu_item.price_excl_tax)
                        
                        # Update item aggregation
                        if item_name not in item_aggregation:
                            item_aggregation[item_name] = {
                                'quantity': 0,
                                'price': float(menu_item.price_excl_tax)
                            }
                        item_aggregation[item_name]['quantity'] += 1
            
            if ordered_items:
                order_summary.append({
                    'orderer_name': orderer.name,
                    'ordered_items': ordered_items,
                    'total_price': total_price
                })
    
    # Calculate totals
    total_before_tax = sum(order['total_price'] for order in order_summary)
    tax_amount = total_before_tax * 0.10  # 10% tax
    total_with_tax = total_before_tax + tax_amount
    
    # Format item aggregation for template
    item_summary = []
    for item_name, data in item_aggregation.items():
        subtotal = data['quantity'] * data['price']
        item_summary.append({
            'name': item_name,
            'quantity': data['quantity'],
            'price': data['price'],
            'subtotal': subtotal
        })
    
    # Sort by item name for consistent display
    item_summary.sort(key=lambda x: x['name'])
    
    return render_template('lunch_order_status.html',
                         orders=order_summary,
                         total_before_tax=total_before_tax,
                         tax_amount=tax_amount,
                         total_with_tax=total_with_tax,
                         item_summary=item_summary)

@app.route('/add_orderer', methods=['POST'])
def add_orderer():
    """注文者追加"""
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        
        if not name or not email:
            flash('氏名とメールアドレスは必須です。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Check if email already exists
        existing_orderer = Orderer.query.filter_by(email=email).first()
        if existing_orderer:
            flash(f'メールアドレス {email} は既に登録されています。', 'error')
            return redirect(url_for('lunch_admin'))
        
        orderer = Orderer(
            name=name,
            email=email,
            item_1='',
            item_2='',
            item_3='',
            item_4='',
            item_5=''
        )
        db.session.add(orderer)
        db.session.commit()
        flash('注文者を追加しました。', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'注文者の追加中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('lunch_admin'))

@app.route('/add_menu', methods=['POST'])
def add_menu():
    """メニュー追加"""
    try:
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        
        if not name or not price:
            flash('メニュー名と価格は必須です。', 'error')
            return redirect(url_for('lunch_admin'))
        
        try:
            price_value = float(price)
        except ValueError:
            flash('価格は数値である必要があります。', 'error')
            return redirect(url_for('lunch_admin'))
        
        menu = Menu(
            name=name,
            price_excl_tax=price_value
        )
        db.session.add(menu)
        db.session.commit()
        flash('メニューを追加しました。', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'メニューの追加中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('lunch_admin'))

@app.route('/send_lunch_order_email_selected', methods=['POST'])
def send_lunch_order_email_selected():
    """選択された注文者のみにランチ注文メール送信"""
    from datetime import datetime
    
    try:
        session_title = request.form.get('session_title', '').strip()
        deadline = request.form.get('deadline', '').strip()
        selected_orderer_ids = request.form.getlist('orderer_ids')
        
        if not session_title or not deadline:
            flash('セッション名と注文期限は必須です。', 'error')
            return redirect(url_for('lunch_admin'))
        
        if not selected_orderer_ids:
            flash('少なくとも1人の注文者を選択してください。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Parse deadline
        try:
            deadline_dt = datetime.fromisoformat(deadline)
        except ValueError:
            flash('注文期限の形式が正しくありません。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Get selected orderers
        selected_orderers = Orderer.query.filter(Orderer.id.in_(selected_orderer_ids)).all()
        
        if not selected_orderers:
            flash('選択された注文者が見つかりません。', 'error')
            return redirect(url_for('lunch_admin'))
        
        # Get all menu items
        menus = Menu.query.all()
        
        if not menus:
            flash('メニューが登録されていません。先にメニューを登録してください。', 'warning')
            return redirect(url_for('lunch_admin'))
        
        sent_count = 0
        error_count = 0
        
        for orderer in selected_orderers:
            try:
                # Send lunch order email to individual orderer
                send_lunch_order_email_to_orderer(orderer, session_title, deadline_dt, menus)
                sent_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error sending lunch order email to {orderer.email}: {e}")
        
        if sent_count > 0:
            flash(f'{sent_count}件の注文メールを送信しました。', 'success')
        if error_count > 0:
            flash(f'{error_count}件のメール送信でエラーが発生しました。', 'warning')
    
    except Exception as e:
        flash(f'メール送信中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('lunch_admin'))

def send_lunch_order_email_to_orderer(orderer, session_title, deadline_dt, menus):
    """個別の注文者にランチ注文メールを送信"""
    import logging
    
    # Set up logging for better error tracking
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        from flask_mail import Message
        from app import mail
        from flask import current_app, render_template
        
        logger.info(f"Preparing to send lunch order email to {orderer.email}")
        logger.info(f"Session: {session_title}, Deadline: {deadline_dt}")
        logger.info(f"Number of menus: {len(menus)}")
        
        # Get BASE_URL from config
        base_url = current_app.config.get('BASE_URL', 'http://127.0.0.1:5000')
        
        # Create order form URL with proper parameters using BASE_URL
        order_form_url = f"{base_url}/lunch_order_form?session={session_title}&orderer_id={orderer.id}&deadline={deadline_dt.isoformat()}"
        logger.info(f"Order form URL: {order_form_url}")
        
        # Format deadline for display
        deadline_formatted = deadline_dt.strftime("%Y年%m月%d日 %H時%M分")
        
        # Format menus for template
        formatted_menus = []
        for menu in menus:
            # Apply comma formatting in Python
            num = float(menu.price_excl_tax)
            if num == int(num):
                formatted_price = f"{int(num):,}"
            else:
                formatted_price = f"{num:,.2f}"
            
            formatted_menus.append({
                'id': menu.id,
                'name': menu.name,
                'price_excl_tax': menu.price_excl_tax,
                'price_formatted': formatted_price
            })
        
        # Use template to generate HTML content
        html_content = render_template('lunch_order_email_template.html',
                                     session_title=session_title,
                                     orderer=orderer,
                                     menus=formatted_menus,
                                     deadline_formatted=deadline_formatted,
                                     deadline_iso=deadline_dt.isoformat(),
                                     order_form_url=order_form_url,
                                     base_url=base_url)
        
        # Send email
        msg = Message(
            subject=f"{session_title} - ランチ注文のご案内",
            sender=current_app.config.get('MAIL_USERNAME', 'noreply@example.com'),
            recipients=[orderer.email]
        )
        msg.html = html_content
        
        logger.info("Attempting to send email...")
        
        # In development, we expect this to fail due to mail configuration
        # but the structure is correct for when SMTP is properly configured
        mail.send(msg)
        
        logger.info(f"✅ Email sent successfully to {orderer.email}")
        
    except Exception as e:
        # Enhanced error logging
        error_msg = f"メール送信エラー: {str(e)}"
        logger.error(f"❌ Failed to send email to {orderer.email}: {error_msg}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Re-raise the exception to be caught by the calling function
        raise Exception(error_msg)

@app.route('/lunch_order_form')
def lunch_order_form():
    """ランチ注文フォーム表示"""
    session_title = request.args.get('session', '')
    orderer_id = request.args.get('orderer_id', '')
    deadline = request.args.get('deadline', '')
    
    if not session_title or not orderer_id:
        return "無効なリクエストです。セッション名と注文者IDが必要です。", 400
    
    # Get orderer information
    orderer = Orderer.query.get(orderer_id)
    if not orderer:
        return "注文者が見つかりません。", 404
    
    # Get all menus
    menus = Menu.query.all()
    if not menus:
        return "メニューが登録されていません。", 404
    
    return render_template('lunch_order_form.html',
                         session_title=session_title,
                         orderer=orderer,
                         menus=menus,
                         deadline=deadline)

@app.route('/lunch_order_response')
def lunch_order_response():
    """ランチ注文レスポンス処理"""
    try:
        session_title = request.args.get('session_title', '')
        orderer_id = request.args.get('orderer_id', '')
        deadline = request.args.get('deadline', '')
        selected_items = request.args.getlist('items')  # Get list of selected menu item IDs
        
        if not session_title or not orderer_id:
            return "無効なリクエストです。", 400
        
        # Get orderer information
        orderer = Orderer.query.get(orderer_id)
        if not orderer:
            return "注文者が見つかりません。", 404
        
        # Clear existing orders
        orderer.item_1 = ''
        orderer.item_2 = ''
        orderer.item_3 = ''
        orderer.item_4 = ''
        orderer.item_5 = ''
        
        # Store selected items (up to 5)
        item_fields = ['item_1', 'item_2', 'item_3', 'item_4', 'item_5']
        ordered_menus = []
        
        for i, item_id in enumerate(selected_items[:5]):  # Limit to 5 items
            menu = Menu.query.get(item_id)
            if menu:
                setattr(orderer, item_fields[i], menu.name)
                ordered_menus.append(menu)
        
        db.session.commit()
        
        # Calculate total price
        total_price = sum(float(menu.price_excl_tax) for menu in ordered_menus)
        
        return render_template('lunch_order_confirmation.html',
                             session_title=session_title,
                             orderer=orderer,
                             ordered_menus=ordered_menus,
                             total_price=total_price,
                             deadline=deadline)
    
    except Exception as e:
        flash(f'注文処理中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('lunch_admin'))