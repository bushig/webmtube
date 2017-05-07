from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from webmtube.config import DB_ENGINE

# default
engine = create_engine(DB_ENGINE)
# Database session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)