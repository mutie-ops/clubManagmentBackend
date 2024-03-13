from sqlalchemy import create_engine, Column, Integer, String, Date, Time, func, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

path = os.path.abspath('database/clubManagement.db')
engine = create_engine(f'sqlite:///{path}', echo=True)

# Step 2: Define a base class using Declarative system
Base = declarative_base()


# Step 3: Define your data model as a class

class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    fullNames = Column(String)
    email = Column(String, unique=True)
    phoneNumber = Column(String, unique=True)
    password = Column(String)

    profile = relationship('Profile', back_populates='user')

    events = relationship('ScheduleEvent', back_populates='user')

    event_status = relationship('EventStatus', back_populates='user')


class Profile(Base):
    __tablename__ = 'Profile'
    id = Column(Integer, primary_key=True)
    subscribed = Column(Boolean)
    profileImage = Column(String)
    user_id = Column(Integer, ForeignKey('Users.id'))
    user = relationship('Users', back_populates='profile')


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
    user_id = Column(Integer, ForeignKey('Users.id'))
    user = relationship('Users', back_populates='events')
    event_statuses = relationship("EventStatus", back_populates="event")


class EventStatus(Base):
    __tablename__ = 'Events'
    id = Column(Integer, primary_key=True)
    booked = Column(Boolean)
    checkedIn = Column(Boolean)
    user_id = Column(Integer, ForeignKey('Users.id'))
    event_id = Column(Integer, ForeignKey('Schedule_Event.id'))

    user = relationship('Users', back_populates='event_status')
    event = relationship("ScheduleEvent", back_populates="event_statuses")


# Step 4: Create the database schema
Base.metadata.create_all(engine)

# Step 5: Create a session
Session = sessionmaker(bind=engine)
session = Session()
