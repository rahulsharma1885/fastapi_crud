from fastapi import FastAPI, Header, HTTPException,Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

from database import SessionLocal, engine
from models import Base, Employee, User
from schemas import EmployeeCreate, UserCreate, UserLogin

app = FastAPI()

Base.metadata.create_all(bind=engine)


#---------------- HOME ---------------- #
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )



# ------------------Password Hashing ------------------ #
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# --------------------JWT Config------------------------#
SECRET_KEY = "rahul_secret_key"
ALGORITHM = "HS256"


# ---------------- JWT FUNCTIONS ---------------- #

from datetime import datetime, timedelta

def create_token(username):

    expire = datetime.utcnow() + timedelta(minutes=5)

    token = jwt.encode(
        {
            "username": username,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def verify_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired (5 min over)")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

# ---------------- REGISTER ---------------- #

@app.post("/register")
def register(user: UserCreate):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        db.close()
        return {"message": "Username already exists"}

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        username=user.username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()

    db.close()

    return {"message": "User Registered Successfully"}


# ---------------- LOGIN ---------------- #

@app.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    db_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if not db_user:
        db.close()
        return {"message": "User Not Found"}

    if not pwd_context.verify(
        user.password,
        db_user.password
    ):
        db.close()
        return {"message": "Invalid Password"}

    token = create_token(user.username)

    db.close()

    return {
        "message": "Login Successful",
        "token": token
    }


# ---------------- CREATE ---------------- #

@app.post("/employees")
def create_employee(
    emp: EmployeeCreate,
    token: str = Header(...)
):

    verify_token(token)

    db: Session = SessionLocal()

    employee = Employee(
        name=emp.name,
        age=emp.age,
        salary=emp.salary
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    db.close()

    return employee


# ---------------- READ ALL ---------------- #

@app.get("/employees")
def get_employees(
    token: str = Header(...)
):

    verify_token(token)

    db: Session = SessionLocal()

    employees = db.query(Employee).all()

    db.close()

    return employees


# ---------------- READ ONE ---------------- #

@app.get("/employees/{emp_id}")
def get_employee(
    emp_id: int,
    token: str = Header(...)
):

    verify_token(token)

    db: Session = SessionLocal()

    employee = db.query(Employee).filter(
        Employee.id == emp_id
    ).first()

    db.close()

    return employee


# ---------------- UPDATE ---------------- #

@app.put("/employees/{emp_id}")
def update_employee(
    emp_id: int,
    emp: EmployeeCreate,
    token: str = Header(...)
):

    verify_token(token)

    db: Session = SessionLocal()

    employee = db.query(Employee).filter(
        Employee.id == emp_id
    ).first()

    if employee:

        employee.name = emp.name
        employee.age = emp.age
        employee.salary = emp.salary

        db.commit()

    db.close()

    return {"message": "Updated"}


# ---------------- DELETE ---------------- #

@app.delete("/employees/{emp_id}")
def delete_employee(
    emp_id: int,
    token: str = Header(...)
):

    verify_token(token)

    db: Session = SessionLocal()

    employee = db.query(Employee).filter(
        Employee.id == emp_id
    ).first()

    if employee:

        db.delete(employee)
        db.commit()

    db.close()

    return {"message": "Deleted"}