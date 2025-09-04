#!/usr/bin/env python3
"""
Add test data for lunch order functionality
"""

from app import app, db
from lunch_models import Orderer, Menu

def add_test_data():
    with app.app_context():
        # Add test menus
        if Menu.query.count() == 0:
            menus = [
                Menu(name="唐揚げ弁当", price_excl_tax=500.00),
                Menu(name="ハンバーグ弁当", price_excl_tax=550.00),
                Menu(name="鮭弁当", price_excl_tax=480.00),
                Menu(name="野菜炒め弁当", price_excl_tax=450.00),
                Menu(name="カレー弁当", price_excl_tax=520.00)
            ]
            
            for menu in menus:
                db.session.add(menu)
            
            print(f"Added {len(menus)} test menus")
        
        # Add test orderers
        if Orderer.query.count() == 0:
            orderers = [
                Orderer(name="田中太郎", email="tanaka@example.com", 
                       item_1="", item_2="", item_3="", item_4="", item_5=""),
                Orderer(name="佐藤花子", email="sato@example.com",
                       item_1="", item_2="", item_3="", item_4="", item_5=""),
                Orderer(name="鈴木一郎", email="suzuki@example.com",
                       item_1="", item_2="", item_3="", item_4="", item_5="")
            ]
            
            for orderer in orderers:
                db.session.add(orderer)
            
            print(f"Added {len(orderers)} test orderers")
        
        # Add some test orders
        orderer1 = Orderer.query.filter_by(name="田中太郎").first()
        if orderer1 and not orderer1.item_1:
            orderer1.item_1 = "唐揚げ弁当"
            orderer1.item_2 = "カレー弁当"
            print("Added test order for 田中太郎")
        
        orderer2 = Orderer.query.filter_by(name="佐藤花子").first()
        if orderer2 and not orderer2.item_1:
            orderer2.item_1 = "ハンバーグ弁当"
            print("Added test order for 佐藤花子")
        
        db.session.commit()
        print("Test data added successfully!")

if __name__ == "__main__":
    add_test_data()