from main import db
from sqlalchemy import func 

class SalesModel(db.Model):
    __tablename__="sales"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default= func.now())
    inv_id = db.Column(db.Integer, db.ForeignKey("inventories.id"), nullable=False)

    def insertRecord(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetchAllSales(cls):
        return cls.query.all()
   