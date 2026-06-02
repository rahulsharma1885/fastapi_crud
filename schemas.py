from pydantic import BaseModel, Field


# Schemas for user registration and login
class UserCreate(BaseModel):
    username: str
    password: str = Field(max_length=72)


class UserLogin(BaseModel):
    username: str
    password: str = Field(max_length=72)

# Schemas for employee management
class EmployeeCreate(BaseModel):
    name: str
    age: int
    salary: float


class EmployeeResponse(EmployeeCreate):
    id: int

    class Config:
        from_attributes = True