from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#stating the connection to my database 
DATABASE_URL = "sqlite:////home/sofia/timetable-maker/technical-solution/backend/timetable.db"  

engine = create_engine(DATABASE_URL, echo=False) #establishing SQLAlchemy 
SessionLocal = sessionmaker(bind=engine)
#this combines a metadata container and a maper that maps our class 
#to my database table 
Base = declarative_base() 