from models import db

class Orderer(db.Model):
    __tablename__ = 'orderers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    item1 = db.Column(db.String(100))
    item2 = db.Column(db.String(100))
    item3 = db.Column(db.String(100))
    item4 = db.Column(db.String(100))
    item5 = db.Column(db.String(100))

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_excl_tax = db.Column(db.Numeric(10, 2), nullable=False)