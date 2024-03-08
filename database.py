from sqlalchemy import create_engine, Column, Integer, String, Date, Time, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

path = os.path.abspath('database/clubManagement.db')
engine = create_engine(f'sqlite:///{path}', echo=True)

# Step 2: Define a base class using Declarative system
Base = declarative_base()


# Step 3: Define your data model as a class
class ScheduleEvent(Base):
    __tablename__ = 'Schedule_Event'

    id = Column(Integer, primary_key=True)
    eventName = Column(String)
    venueName = Column(String)
    eventLatitude = Column(String)
    eventLongitude = Column(String)
    eventTime = Column(String)
    eventDate = Column(Date)
    eventDescription = Column(String)
    eventImage = Column(String)


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    fullNames = Column(String)
    email = Column(String)
    phoneNumber = Column(Integer)
    password = Column(String)


class Profile(Base):
    __tablename__ = 'Profile'
    id = Column(Integer, primary_key=True)
    subscribed = Column(Boolean)
    profileImage = Column(String)


# Step 4: Create the database schema
Base.metadata.create_all(engine)

# Step 5: Create a session
Session = sessionmaker(bind=engine)
session = Session()
