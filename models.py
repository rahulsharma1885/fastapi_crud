from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()


# Define your models here
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True)
    password = Column(String(255))


# Define the Employee model
class Employee(Base):

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    age = Column(Integer)
    salary = Column(Float)