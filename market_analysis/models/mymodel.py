from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from .meta import Base


class Stocks(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    symbol = Column(Text)
    name = Column(Text)


# class User_stocks(Base):
#     __tablename__ = 'user_stocks'
#     id = Column(Integer, primary_key=True)
#     user = Column(Text)
#     stock = Column(Text)


Index('my_index', Stocks.name, mysql_length=255)
