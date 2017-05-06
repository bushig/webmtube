from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.sql import func

from webmtube.config import DB_ENGINE

engine = create_engine(DB_ENGINE)

Base = declarative_base()

# TODO: Use scoped_session
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class WEBM(Base):
    __tablename__ = 'WEBM'
    # __table_args__ = (CheckConstraint(func.length('md5')==32),)
    id = Column(String(32), primary_key=True)
    time_created = Column(DateTime(), server_default=func.now())
    screamer_chance = Column(Float(), nullable=True)
    views = Column(Integer(), default=0)
    likes = Column(Integer(), default=0)
    dislikes = Column(Integer(), default=0)

    webms = relationship('DirtyWEBM', cascade='delete')

    # TODO: Define to_dictionary for JSON serialization
    def to_dict(self):
        return {'id': self.id, 'time_created': self.time_created.isoformat(),
                'screamer_chance': self.screamer_chance, 'views': self.views, 'likes': self.likes,
                'dislikes': self.dislikes}

    def __init__(self, id_, screamer_chance=None):
        self.id = id_
        self.screamer_chance = screamer_chance

    def __repr__(self):
        return "<WEBM(id={}, time_created={}, screamer_chance={}, views={}, likes={}, dislikes={})>".format(self.id,
                                                                                                            self.time_created,
                                                                                                            self.screamer_chance,
                                                                                                            self.views,
                                                                                                            self.likes,
                                                                                                            self.dislikes)


class DirtyWEBM(Base):
    __tablename__ = 'DirtyWEBM'
    md5 = Column(String(32), primary_key=True)
    webm_id = Column(String(32), ForeignKey('WEBM.id', ), nullable=False)
    webm = relationship(WEBM)
    ForeignKeyConstraint(['webm_id'], ['WEBM.id'])
