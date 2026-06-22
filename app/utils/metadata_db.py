from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

Base = declarative_base()

class DataMetadata(Base):
    __tablename__ = 'data_metadata'
    id = Column(Integer, primary_key=True)
    source = Column(String)
    indicator = Column(String)
    url = Column(String)
    file_path = Column(String)
    file_hash = Column(String)
    row_count = Column(Integer)
    fetch_time = Column(DateTime, default=datetime.datetime.utcnow)
    duration_ms = Column(Float)

def init_db(db_url="sqlite:///./metadata.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
