from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

# Create a base class for your models
Base = declarative_base()

# Define the Logs model
class Logs(Base):
    __tablename__ = 'logs'

    guild_id = Column(Integer, primary_key=True)
    message_logs = Column(Integer)
    member_logs = Column(Integer)
    voice_logs = Column(Integer)
    mod_logs = Column(Integer)
    muterole = Column(Integer)
    muterole_channel = Column(Integer)

# Create the engine and session
DATABASE_FILE = "database.db"
engine = create_engine(f"sqlite:///{DATABASE_FILE}")
Session = sessionmaker(bind=engine)
