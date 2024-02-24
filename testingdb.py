from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///C:\\Users\\HP\\OneDrive\\Desktop\\cubManangegmentBackend\\TEST.db',
                       echo=True)  # 'echo=True' prints SQL queries

# Step 2: Define a base class using Declarative system
Base = declarative_base()


# Step 3: Define your data model as a class
class User(Base):
    __tablename__ = 'Schedule_Event'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


# Step 4: Create the database schema
Base.metadata.create_all(engine)

# Step 5: Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Step 6: Insert data into the tables
user1 = User(name='Alice', age=30)
user2 = User(name='Bob', age=25)
session.add_all([user1, user2])
session.commit()

# Step 7: Close the session
session.close()
