from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from django_project import settings

# Load database URL from .env
import os

DATABASE_URL = settings.django_project

# Connect to the database
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)  # Auto-detects all tables

# Get table references
ParishKnowledge = Table("parish_knowledge", metadata, autoload_with=engine)
ChatQuery = Table("chat_query", metadata, autoload_with=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
