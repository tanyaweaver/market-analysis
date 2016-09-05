from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode,
    DateTime,
    Boolean,
    ForeignKey,
    DateTime
)

from .meta import Base
from sqlalchemy.orm import relationship


class Association(Base):
    __tablename__ = 'association'
    #id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), primary_key=True)
    shares = Column(Integer)
    child = relationship('Stocks')


class Users(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    username = Column(Unicode)
    first_name = Column(Unicode)
    last_name = Column(Unicode)
    email = Column(Unicode)
    email_verified = Column(Boolean)
    date_joined = Column(DateTime)
    date_last_logged = Column(DateTime)
    pass_hash = Column(Unicode)
    phone_number = Column(Unicode)
    phone_number_verified = Column(Boolean)
    active = Column(Boolean)
    password_last_changed = Column(DateTime)
    password_expired = Column(Boolean)
    children = relationship('Association')


class Stocks(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    symbol = Column(Text)
    name = Column(Text)
    exchange = Column(Text)


# Index('my_index', Users.username, unique=True, mysql_length=255)
