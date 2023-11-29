from sqlalchemy import Column, Integer, String, Text, DateTime
from models.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(128), unique=True)
    salt = Column(String(128))
    hashed_password = Column(String(128))

    def __init__(self, user_name=None, hashed_password=None, salt=None):
        self.user_name = user_name
        self.salt = salt
        self.hashed_password = hashed_password

    def __repr__(self):
        return '<Name %r>' % (self.user_name)