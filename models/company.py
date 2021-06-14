from main import db
from sqlalchemy import func 

class CompanyModel(db.Model):
    __tablename__="companies"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(80), nullable=False)
    company_location = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default= func.now())
    users = db.relationship('UsersModel', backref='user', lazy=True)