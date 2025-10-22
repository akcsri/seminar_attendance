"""Test for the clear orders functionality"""
import unittest
from app import app, db
from lunch_models import Orderer, Menu


class TestClearOrders(unittest.TestCase):
    """Test cases for clearing all order data"""
    
    def setUp(self):
        """Set up test database and test data"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Add test menus
            menu1 = Menu(name='ハンバーグ定食', price_excl_tax=800)
            menu2 = Menu(name='唐揚げ定食', price_excl_tax=750)
            db.session.add_all([menu1, menu2])
            
            # Add test orderers with orders
            orderer1 = Orderer(
                name='田中太郎',
                email='tanaka@example.com',
                item_1='ハンバーグ定食',
                item_2='唐揚げ定食',
                item_3='',
                item_4='',
                item_5=''
            )
            orderer2 = Orderer(
                name='佐藤花子',
                email='sato@example.com',
                item_1='唐揚げ定食',
                item_2='',
                item_3='',
                item_4='',
                item_5=''
            )
            orderer3 = Orderer(
                name='鈴木一郎',
                email='suzuki@example.com',
                item_1='',
                item_2='',
                item_3='',
                item_4='',
                item_5=''
            )
            db.session.add_all([orderer1, orderer2, orderer3])
            db.session.commit()
    
    def tearDown(self):
        """Clean up after test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_clear_orders_clears_all_items(self):
        """Test that clear_orders clears all item_1 to item_5 fields"""
        with self.app.app_context():
            # Verify initial state - some orderers have orders
            orderers_before = Orderer.query.all()
            orders_before = []
            for orderer in orderers_before:
                if any([orderer.item_1, orderer.item_2, orderer.item_3, 
                       orderer.item_4, orderer.item_5]):
                    orders_before.append(orderer.name)
            
            self.assertGreater(len(orders_before), 0, 
                             "Should have at least one orderer with orders")
        
        # Call clear_orders endpoint
        response = self.client.post('/clear_orders', follow_redirects=True)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn('注文データをクリアしました。'.encode('utf-8'), 
                     response.data)
        
        # Verify database state - all orders cleared
        with self.app.app_context():
            orderers_after = Orderer.query.all()
            for orderer in orderers_after:
                self.assertEqual(orderer.item_1, '', 
                               f"{orderer.name}'s item_1 should be empty")
                self.assertEqual(orderer.item_2, '', 
                               f"{orderer.name}'s item_2 should be empty")
                self.assertEqual(orderer.item_3, '', 
                               f"{orderer.name}'s item_3 should be empty")
                self.assertEqual(orderer.item_4, '', 
                               f"{orderer.name}'s item_4 should be empty")
                self.assertEqual(orderer.item_5, '', 
                               f"{orderer.name}'s item_5 should be empty")
    
    def test_clear_orders_preserves_orderer_info(self):
        """Test that clear_orders only clears orders, not orderer info"""
        with self.app.app_context():
            orderers_before = Orderer.query.all()
            orderer_count_before = len(orderers_before)
            orderer_names_before = {o.name for o in orderers_before}
            orderer_emails_before = {o.email for o in orderers_before}
        
        # Call clear_orders endpoint
        response = self.client.post('/clear_orders', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify orderer information is preserved
        with self.app.app_context():
            orderers_after = Orderer.query.all()
            orderer_count_after = len(orderers_after)
            orderer_names_after = {o.name for o in orderers_after}
            orderer_emails_after = {o.email for o in orderers_after}
            
            self.assertEqual(orderer_count_before, orderer_count_after,
                           "Number of orderers should remain the same")
            self.assertEqual(orderer_names_before, orderer_names_after,
                           "Orderer names should be preserved")
            self.assertEqual(orderer_emails_before, orderer_emails_after,
                           "Orderer emails should be preserved")
    
    def test_clear_orders_with_no_orders(self):
        """Test that clear_orders works even when no orders exist"""
        with self.app.app_context():
            # First clear all existing orders
            orderers = Orderer.query.all()
            for orderer in orderers:
                orderer.item_1 = ''
                orderer.item_2 = ''
                orderer.item_3 = ''
                orderer.item_4 = ''
                orderer.item_5 = ''
            db.session.commit()
        
        # Try to clear again
        response = self.client.post('/clear_orders', follow_redirects=True)
        
        # Should still succeed
        self.assertEqual(response.status_code, 200)
        self.assertIn('注文データをクリアしました。'.encode('utf-8'), 
                     response.data)


if __name__ == '__main__':
    unittest.main()
