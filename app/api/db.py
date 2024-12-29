import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("NO DATABASE_URL")

# Set up engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# TABLE SCHEMA
class JsonMetadata(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    file_content = Column(String, nullable=False)
    uploaddate = Column(DateTime, nullable=False)

# GET DB SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE TABLE
Base.metadata.create_all(bind=engine)