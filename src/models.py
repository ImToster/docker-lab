from . import db
from sqlalchemy import Column, Integer, String

# Create the User model to represent the users table
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)