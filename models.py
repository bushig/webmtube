import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from config import DB_ENGINE

engine = create_engine(DB_ENGINE)

Base = declarative_base()

# TODO: Use scoped_session
Session = sessionmaker(bind=engine)


class WEBM(Base):
    __tablename__ = 'WEBM'
    # __table_args__ = (CheckConstraint(func.length('md5')==32),)
    md5 = Column(String(32), primary_key=True)
    time_created = Column(DateTime(), server_default=func.now())
    screamer_chance = Column(Float(), nullable=True)
    views = Column(Integer(), default=0)
    likes = Column(Integer(), default=0)
    dislikes = Column(Integer(), default=0)

    # TODO: Define to_dictionary for JSON serialization
    def to_dict(self):
        return {'md5': self.md5, 'time_created': self.time_created.isoformat(),
                'screamer_chance': self.screamer_chance, 'views': self.views, 'likes': self.likes,
                'dislikes': self.dislikes}

    def __init__(self, md5, screamer_chance=None):
        self.md5 = md5
        self.screamer_chance = screamer_chance

    def __repr__(self):
        return "<WEBM(md5={}, time_created={}, screamer_chance={}, views={}, likes={}, dislikes={})>".format(self.md5,
                                                                                                             self.time_created,
                                                                                                             self.screamer_chance,
                                                                                                             self.views,
                                                                                                             self.likes,
                                                                                                             self.dislikes)
