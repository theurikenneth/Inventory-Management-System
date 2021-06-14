from main import db
from sqlalchemy import func 

class ContactsalesModel(db.Model):
    __tablename__="contactsales"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    companyname = db.Column(db.String(80), nullable=False)
    companysize = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(80), nullable=False)
    salesteamhelp= db.Column(db.String(80), nullable=False)
    textarea = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default= func.now())
  

    def insertRecord(self):
        db.session.add(self)
        db.session.commit()
        return self