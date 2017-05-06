from sqlalchemy.orm import sessionmaker, scoped_session

# Database session factory
session_factory = sessionmaker()
Session = scoped_session(session_factory)
