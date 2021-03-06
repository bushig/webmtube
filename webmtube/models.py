from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, ForeignKeyConstraint, \
    CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()


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

    CheckConstraint('views >= 0', name='views_positive')
    CheckConstraint('likes >= 0', name='likes_positive')
    CheckConstraint('dislikes >= 0', name='dislikes_positive')
    # TODO: Define to_dictionary for JSON serialization
    def to_dict(self):
        return {'id': self.id, 'time_created': str(self.time_created),
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
