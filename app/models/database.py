from sqlalchemy import String, Float, Text, Boolean, DateTime, JSON, Integer, create_engine
from sqlalchemy.orm import declarative_base, mapped_column, sessionmaker
import uuid
from datetime import datetime, timezone
from app.config import settings

Base = declarative_base()

class Meeting(Base):
     __tablename__ = "meetings"

     id = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
     filename = mapped_column(String, nullable=False)
     original_filename = mapped_column(String, nullable=False)
     file_path = mapped_column(String, nullable=False)
     duration = mapped_column(Float)
     transcription_text = mapped_column(Text)
     transcription_confidence = mapped_column(Float)
     processed = mapped_column(Boolean, default=False)
     created_at = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))
     updated_at = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc), onupdate=lambda : datetime.now(timezone.utc))

class Requirement(Base):
     __tablename__ = "requirements"

     id = mapped_column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
     meeting_id = mapped_column(String, nullable=False)
     text = mapped_column(Text, nullable=False)
     summary=mapped_column(String, nullable=False)
     description=mapped_column(Text)
     requirement_type=mapped_column(String, nullable=False)
     priority=mapped_column(String, nullable=True)
     labels=mapped_column(JSON)
     acceptance_criteria=mapped_column(JSON)
     confidence=mapped_column(Float)
     timestamp=mapped_column(String)
     jira_ticket_key=mapped_column(String)
     created_at=mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))

class JiraTicket(Base):
     __tablename__="jira_tickets"

     id=mapped_column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
     requirement_id=mapped_column(String, nullable=False)
     ticket_key=mapped_column(String, nullable=False)
     url=mapped_column(String, nullable=False)
     summary=mapped_column(String, nullable=False)
     status=mapped_column(String, nullable=False)
     created_at=mapped_column(String, default=lambda : datetime.now(timezone.utc))

class ProcessingJob(Base):
     __tablename__="processing_jobs"

     id=mapped_column(String, primary_key=True, default=lambda : str(uuid.uuid4()))
     meeting_id=mapped_column(String, nullable=False)
     status=mapped_column(String, nullable=False)
     progress=mapped_column(Integer, default=0)
     message=mapped_column(String)
     result=mapped_column(JSON)
     created_at=mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))
     updated_at=mapped_column(DateTime, default=lambda : datetime.now(timezone.utc), onupdate=lambda : datetime.now(timezone.utc))

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
     db = SessionLocal()
     try:
          yield db
     finally:
          db.close()