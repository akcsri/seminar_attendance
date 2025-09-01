#!/usr/bin/env python3
"""
データベースポリシー検証スクリプト
Database Policy Validation Script

このスクリプトは、データベース構造が変更されていないことを確認します。
This script verifies that the database structure has not been modified.
"""

import hashlib
import os
import sys

def calculate_file_hash(filepath):
    """ファイルのハッシュ値を計算"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'rb') as f:
        content = f.read()
        return hashlib.sha256(content).hexdigest()

def check_models_structure():
    """models.py の構造をチェック"""
    models_path = 'models.py'
    
    if not os.path.exists(models_path):
        print("❌ models.py ファイルが見つかりません")
        return False
    
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 必要なクラスが存在することを確認
    required_classes = ['Recipient', 'Seminar', 'Attendance']
    required_fields = {
        'Recipient': ['id', 'name', 'email', 'affiliation', 'phone'],
        'Seminar': ['id', 'title', 'date', 'venue', 'speaker', 'topic', 'contact'],
        'Attendance': ['id', 'recipient_id', 'seminar_id', 'status', 'comment']
    }
    
    missing_elements = []
    
    # クラスの存在確認
    for class_name in required_classes:
        if f'class {class_name}(' not in content:
            missing_elements.append(f'クラス {class_name}')
    
    # フィールドの存在確認
    for class_name, fields in required_fields.items():
        for field in fields:
            if f'{field} = db.Column(' not in content:
                missing_elements.append(f'{class_name}.{field}')
    
    if missing_elements:
        print("❌ 以下の必要な要素が見つかりません:")
        for element in missing_elements:
            print(f"   - {element}")
        return False
    
    print("✅ models.py の基本構造は正常です")
    return True

def check_forbidden_patterns():
    """禁止されたパターンをチェック"""
    models_path = 'models.py'
    
    if not os.path.exists(models_path):
        return False
    
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 禁止されたパターン
    forbidden_patterns = [
        'ALTER TABLE',
        'DROP TABLE', 
        'ADD COLUMN',
        'DROP COLUMN',
        'MODIFY COLUMN',
        'alembic',
        'migrate',
        'db.create_all()',  # models.py 内での実行は禁止
    ]
    
    found_patterns = []
    for pattern in forbidden_patterns:
        if pattern.lower() in content.lower():
            found_patterns.append(pattern)
    
    if found_patterns:
        print("❌ 禁止されたパターンが検出されました:")
        for pattern in found_patterns:
            print(f"   - {pattern}")
        return False
    
    print("✅ 禁止されたパターンは検出されませんでした")
    return True

def main():
    print("🔍 データベースポリシー検証を開始します...")
    print("🔍 Starting database policy validation...")
    print()
    
    all_checks_passed = True
    
    # models.py の構造チェック
    if not check_models_structure():
        all_checks_passed = False
    
    # 禁止パターンチェック
    if not check_forbidden_patterns():
        all_checks_passed = False
    
    print()
    if all_checks_passed:
        print("🎉 全ての検証が成功しました！")
        print("🎉 All validations passed!")
        print("✅ データベース構造は適切に保護されています")
        print("✅ Database structure is properly protected")
        return 0
    else:
        print("💥 検証に失敗しました")
        print("💥 Validation failed")
        print("❌ データベースポリシーに違反している可能性があります")
        print("❌ Possible violation of database policy")
        return 1

if __name__ == '__main__':
    sys.exit(main())