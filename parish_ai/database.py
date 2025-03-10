from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from django.conf import settings
import os
import django
import environ
env = environ.Env()
environ.Env.read_env()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")  # Adjust if needed
django.setup()


# Initialize env variablesparent

DATABASE_URL = DATABASE_URL = f"mysql+pymysql://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}"

# Connect to the database
engine = create_engine(DATABASE_URL, echo = True)
metadata = MetaData()
metadata.reflect(bind=engine)  # Auto-detects all tables

# Get table references
ParishKnowledge = Table("parish_knowledge", metadata, autoload_with=engine)
ChatQuery = Table("pages_chatquery", metadata, autoload_with=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

