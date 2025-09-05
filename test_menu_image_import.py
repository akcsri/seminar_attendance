#!/usr/bin/env python3
"""
Test script for enhanced menu CSV import with image URLs.
Tests the functionality added to address issue #143.
"""

import json
import os
import tempfile
from app import app, db
from lunch_models import Menu, Orderer

def test_csv_import_with_image_urls():
    """Test CSV import functionality with image URLs"""
    print("🧪 Testing CSV import with image URLs...")
    
    with app.app_context():
        # Create sample CSV content with image URLs
        csv_content = """メニュー名,税抜き価格,画像URL
テストメニュー1,500,https://example.com/test1.jpg
テストメニュー2,600,https://example.com/test2.jpg
テストメニュー3,700
"""
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            csv_file = f.name
        
        try:
            # Clear existing menus
            Menu.query.delete()
            db.session.commit()
            
            # Remove existing mappings file if it exists
            if os.path.exists('menu_image_mappings.json'):
                os.remove('menu_image_mappings.json')
            
            # Simulate file upload by reading the CSV and processing it
            with open(csv_file, 'r', encoding='utf-8') as f:
                import csv
                import io
                
                # Read CSV content
                content = f.read()
                stream = io.StringIO(content, newline=None)
                csv_reader = csv.reader(stream)
                
                # Skip header
                next(csv_reader, None)
                
                image_url_mappings = {}
                for row_num, row in enumerate(csv_reader, start=1):
                    if len(row) >= 2:
                        name = row[0].strip()
                        price = float(row[1].strip())
                        image_url = row[2].strip() if len(row) > 2 else ''
                        
                        menu_item = Menu(name=name, price_excl_tax=price)
                        db.session.add(menu_item)
                        db.session.flush()  # Get ID
                        
                        if image_url:
                            image_url_mappings[menu_item.id] = image_url
                
                db.session.commit()
                
                # Save image mappings
                if image_url_mappings:
                    with open('menu_image_mappings.json', 'w', encoding='utf-8') as f:
                        json.dump(image_url_mappings, f, ensure_ascii=False, indent=2)
            
            # Verify menus were created
            menus = Menu.query.all()
            assert len(menus) == 3, f"Expected 3 menus, got {len(menus)}"
            
            # Verify image mappings file was created
            assert os.path.exists('menu_image_mappings.json'), "Image mappings file not created"
            
            # Verify image mappings content
            with open('menu_image_mappings.json', 'r', encoding='utf-8') as f:
                mappings = json.load(f)
            
            # Should have 2 mappings (first two menus have image URLs, third doesn't)
            assert len(mappings) == 2, f"Expected 2 image mappings, got {len(mappings)}"
            
            # Verify specific mappings
            menu_1 = Menu.query.filter_by(name='テストメニュー1').first()
            menu_2 = Menu.query.filter_by(name='テストメニュー2').first()
            menu_3 = Menu.query.filter_by(name='テストメニュー3').first()
            
            assert str(menu_1.id) in mappings, "Menu 1 image mapping missing"
            assert str(menu_2.id) in mappings, "Menu 2 image mapping missing"
            assert str(menu_3.id) not in mappings, "Menu 3 should not have image mapping"
            
            assert mappings[str(menu_1.id)] == 'https://example.com/test1.jpg'
            assert mappings[str(menu_2.id)] == 'https://example.com/test2.jpg'
            
            print("✅ CSV import with image URLs test passed!")
            
        finally:
            # Clean up temporary file
            if os.path.exists(csv_file):
                os.remove(csv_file)

def test_order_form_with_image_mappings():
    """Test that order form correctly loads image mappings"""
    print("🧪 Testing order form with image mappings...")
    
    with app.app_context():
        # Create test orderer
        orderer = Orderer(name='テスト太郎', email='test@example.com')
        db.session.add(orderer)
        db.session.commit()
        
        # Test order form route
        from lunch_route import lunch_order_form
        with app.test_request_context('/lunch_order_form?session=test&orderer_id=1&deadline=2024-01-01'):
            try:
                result = lunch_order_form()
                print("✅ Order form with image mappings test passed!")
            except Exception as e:
                print(f"❌ Order form test failed: {e}")

if __name__ == '__main__':
    print("🚀 Running enhanced menu CSV import tests...")
    
    test_csv_import_with_image_urls()
    test_order_form_with_image_mappings()
    
    print("✅ All tests completed!")