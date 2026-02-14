import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Grab the Database URL from the environment (Cloud) or use a local file
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./renzo.db")

# 2. Fix for Render Postgres URL format (if you use their Postgres DB later)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Create the database engine
# Note: connect_args is needed only for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Define your database tables
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, index=True)
    prompt = Column(String)
    audio_url = Column(String)

# 5. Create the tables if they don't exist
Base.metadata.create_all(bind=engine)

# 6. Helper function to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()