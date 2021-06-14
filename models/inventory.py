from main import db
from sqlalchemy import func 

class InventoryModel(db.Model):
    __tablename__="inventories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    inventory_type = db.Column(db.String(80), nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default= func.now())
    sales = db.relationship('SalesModel', backref='the_inventory', lazy=True)
    stock = db.relationship('StockModel', backref='inventory', lazy=True)

    def insertRecord(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetchAllInventories(cls):
        return cls.query.all()

        #return InventoryModel.query.all() - returns the same

    @classmethod
    def fetch_inventory_by_id(cls, inventory_id):
        record = cls.query.filter_by(id=inventory_id).first()

        if record:
            return record

        else:
            return False

    @classmethod
    def updateInventoryById(cls, inventory_id, name, inventory_type, buying_price, selling_price):
        record = InventoryModel.query.filter_by(id=inventory_id).first()
        if record:
            record.name=name
            record.inventory_type=inventory_type
            record.buying_price=buying_price
            record.selling_price=selling_price
            db.session.commit()
            return True

        else:
            return False
