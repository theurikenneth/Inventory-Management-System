from main import db
from sqlalchemy import func 
from main import login_manager
from flask_login import UserMixin
import hashlib
import os


@login_manager.user_loader
def load_user(user_id):
    return UsersModel.query.get(int(user_id))

class UsersModel(db.Model, UserMixin):
    __tablename__="users"

    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(80), nullable=False)
    emailAddress = db.Column(db.String(80), unique=True, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    phoneNumber = db.Column(db.Integer, unique=True, nullable=False)
    role = db.Column(db.String(80),nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default= func.now())
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    @classmethod
    def fetch_user_by_email(cls, emailAddress):
        record = cls.query.filter_by(emailAddress=emailAddress).first()

        if record:
            return True

        else:
            return False

    @classmethod
    def fetch_user_by_phoneNumber(cls, phoneNumber):
        record = cls.query.filter_by(phoneNumber=phoneNumber).first()

        if record:
            return True

        else:
            return False


