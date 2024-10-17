from sqlalchemy import create_engine, Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base

# Create the base class
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

# Define the Punishments model
class Punishments(Base):
    __tablename__ = 'punishments'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer)
    user_id = Column(Integer)
    punishment_type = Column(String)
    punishment_time = Column(TIMESTAMP)
    punisher_id = Column(Integer)
    reason = Column(String)

# Define the CC model
class CC(Base):
    __tablename__ = 'cc'

    name = Column(String, primary_key=True)
    owner_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    text = Column(String, nullable=False)
    image = Column(String)
    nsfw = Column(Boolean, nullable=False)

# Function to create the database
def create_database():
    engine = create_engine("sqlite:///database.db")
    Base.metadata.create_all(engine)

# Call the function to create the database and tables
if __name__ == "__main__":
    create_database()
