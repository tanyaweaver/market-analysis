from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode,
    DateTime,
    Boolean,
)

from .meta import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode, unique=True)
    first_name = Column(Unicode)
    last_name = Column(Unicode)
    email = Column(Unicode)
    email_verified = Column(Boolean)
    date_joined = Column(DateTime)
    date_last_logged = Column(DateTime)
    pass_hash = Column(Unicode)
    value = Column(Integer)


# Index('my_index', Users.username, unique=True, mysql_length=255)
