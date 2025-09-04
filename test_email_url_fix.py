#!/usr/bin/env python3
"""
Test the email template URL generation
"""

from app import app
from flask import render_template
from lunch_models import Orderer, Menu
from datetime import datetime

def test_email_template():
    with app.app_context():
        # Get test data
        orderer = Orderer.query.first()
        if not orderer:
            print("No orderer found, please run add_test_data.py first")
            return
        
        menus = Menu.query.all()
        if not menus:
            print("No menus found, please run add_test_data.py first")
            return
        
        # Test data for email template
        session_title = "テスト注文"
        deadline_dt = datetime(2024, 12, 31, 12, 0)
        deadline_formatted = deadline_dt.strftime("%Y年%m月%d日 %H時%M分")
        base_url = 'http://127.0.0.1:5000'
        
        # Create order form URL like the actual code does
        order_form_url = f"{base_url}/lunch_order_form?session={session_title}&orderer_id={orderer.id}&deadline={deadline_dt.isoformat()}"
        
        print(f"Generated order form URL: {order_form_url}")
        
        # Format menus for template
        formatted_menus = []
        for menu in menus[:3]:  # Test with first 3 menus
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
        
        # Render the email template with app context and request context
        try:
            with app.test_request_context():
                html_content = render_template('lunch_order_email_template.html',
                                             session_title=session_title,
                                             orderer=orderer,
                                             menus=formatted_menus,
                                             deadline_formatted=deadline_formatted,
                                             deadline_iso=deadline_dt.isoformat(),
                                             order_form_url=order_form_url,
                                             base_url=base_url)
            
            print("✅ Email template rendered successfully!")
            
            # Check if the URL appears in the rendered content
            if order_form_url in html_content:
                print("✅ Order form URL correctly included in email template!")
            else:
                print("❌ Order form URL not found in email template")
            
            # Check if hardcoded URL is gone
            if "seminar-attendance.onrender.com" in html_content:
                print("❌ Still contains hardcoded URL!")
            else:
                print("✅ Hardcoded URL successfully removed!")
                
            return True
                
        except Exception as e:
            print(f"❌ Error rendering email template: {e}")
            return False

if __name__ == "__main__":
    test_email_template()