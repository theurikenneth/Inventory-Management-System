from main import db
from sqlalchemy import func 

class ContactModel(db.Model):
    __tablename__="contact"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    textarea = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default= func.now())


    def insertRecord(self):
        db.session.add(self)
        db.session.commit()
        return self