#!/usr/bin/env python3
"""
Test script for lunch admin fixes
Tests CSS display and form validation fixes
"""
import requests
import sys
import re

def test_css_display_fix():
    """Test that CSS is properly wrapped in style tags"""
    try:
        response = requests.get('http://127.0.0.1:5000/lunch_admin', timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to access lunch admin page: {response.status_code}")
            return False
        
        html = response.text
        
        # Check that CSS is wrapped in <style> tags
        if '<style>' not in html or '</style>' not in html:
            print("❌ CSS is not properly wrapped in <style> tags")
            return False
        
        # Check that CSS properties are not displayed as plain text outside style tags
        # Look for the specific CSS that was problematic (should be in style tags now)
        lines = html.split('\n')
        in_style_block = False
        css_outside_style = False
        
        for line in lines:
            line_stripped = line.strip()
            if '<style>' in line_stripped:
                in_style_block = True
            elif '</style>' in line_stripped:
                in_style_block = False
            elif not in_style_block and re.search(r'table\s*{', line_stripped, re.IGNORECASE):
                # Found CSS outside of style tags
                css_outside_style = True
                break
        
        if css_outside_style:
            print("❌ CSS properties found outside of style tags")
            return False
        
        print("✅ CSS display fix verified")
        return True
        
    except Exception as e:
        print(f"❌ CSS display test failed: {e}")
        return False

def test_form_structure():
    """Test that orderer checkboxes are within the form"""
    try:
        response = requests.get('http://127.0.0.1:5000/lunch_admin', timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to access lunch admin page: {response.status_code}")
            return False
        
        html = response.text
        
        # Check that the form contains orderer checkboxes
        form_pattern = r'<form[^>]*send_lunch_order_email_selected[^>]*>.*?</form>'
        form_match = re.search(form_pattern, html, re.DOTALL | re.IGNORECASE)
        
        if not form_match:
            print("❌ Email sending form not found")
            return False
        
        form_content = form_match.group(0)
        
        # Check that orderer checkboxes are inside the form
        if 'name="selected_orderers"' not in form_content:
            print("❌ Orderer checkboxes not found within form")
            return False
        
        print("✅ Form structure fix verified")
        return True
        
    except Exception as e:
        print(f"❌ Form structure test failed: {e}")
        return False

def test_validation_logic():
    """Test that validation works with correct field names"""
    try:
        # Test with no orderers selected (should fail validation)
        response = requests.post(
            'http://127.0.0.1:5000/send_lunch_order_email_selected',
            data={
                'session_title': 'Test Session',
                'deadline': '2024-12-31T12:00'
            },
            allow_redirects=False,
            timeout=10
        )
        
        # Should redirect back to lunch_admin on validation error
        if response.status_code != 302:
            print(f"❌ Expected redirect on validation error, got: {response.status_code}")
            return False
        
        if '/lunch_admin' not in response.headers.get('Location', ''):
            print(f"❌ Expected redirect to lunch_admin, got: {response.headers.get('Location')}")
            return False
        
        print("✅ Validation logic fix verified")
        return True
        
    except Exception as e:
        print(f"❌ Validation logic test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing lunch admin fixes...")
    
    tests = [
        ("CSS Display Fix", test_css_display_fix),
        ("Form Structure Fix", test_form_structure),  
        ("Validation Logic Fix", test_validation_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📝 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())