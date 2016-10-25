import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from config import DB_ENGINE

engine = create_engine(DB_ENGINE)

Base = declarative_base()

Session = sessionmaker(bind=engine)


class WEBM(Base):
    __tablename__ = 'WEBM'
    md5 = Column(String(32), primary_key=True)
    size = Column(Integer())
    time_created = Column(DateTime(), server_default=func.now())
    screamer_chance = Column(Float(), nullable=True)

    # TODO: Define to_dictionary for JSON serialization

    def __init__(self, md5, size, screamer_chance=None):
        self.md5 = md5
        self.size = size
        self.screamer_chance = screamer_chance

    def __repr__(self):
        return "<WEBM(md5={}, size={}, time_created={}, screamer_chance={})>".format(self.md5, self.size,
                                                                                     self.time_created,
                                                                                     self.screamer_chance)
