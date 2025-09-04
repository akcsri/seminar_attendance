from models import db

class Orderer(db.Model):
    __tablename__ = 'orderers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    item_1 = db.Column(db.String(100))
    item_2 = db.Column(db.String(100))
    item_3 = db.Column(db.String(100))
    item_4 = db.Column(db.String(100))
    item_5 = db.Column(db.String(100))

class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_excl_tax = db.Column(db.Numeric(10, 2), nullable=False)