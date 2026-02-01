from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

import mysql.connector
class basedata(BaseModel):
    name:str
    age: int
    gender:str
    joindate:str
    city: str
    contact: int
    duration: str
    train: str
    payment: str
    expiredate:str

app= FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def dbconn():
    return mysql.connector.connect(
        host="srv1834.hstgr.io",
        user="u651328475_batch_11",
        password="Batch_11",
        database="u651328475_batch_11"
    )
@app.post("/registerform")
def add(data:basedata):
        conn=dbconn()
        cursor=conn.cursor()
        sql="INSERT INTO gl_memberlist (name,age,gender,joindate,city,contact,duration,train,payment,expiredate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        values= (data.name,data.age,data.gender,data.joindate,data.city,data.contact,data.duration,data.train,data.payment,data.expiredate)
        cursor.execute(sql,values)
        conn.commit()
        cursor.close()
        conn.close()
        return f"data inserted {data.name,data.age,data.gender,data.joindate,data.city,data.contact,data.duration,data.train,data.payment,data.expiredate}"

@app.get("/dashboard")
def get():
    conn=dbconn()
    cursor=conn.cursor(dictionary=True)
    sql="select * from gl_memberlist"
    cursor.execute(sql)
    res=cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.delete("/del/{id}")
def delete_data(id: int):
    conn = dbconn()
    cursor = conn.cursor()
    sql = "DELETE FROM gl_memberlist WHERE id = %s"
    cursor.execute(sql, (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Data deleted successfully for id {id}"}

class UserUpdate(BaseModel):
    expiredate: str

@app.put("/update/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    conn =dbconn()
    cursor = conn.cursor()
    sql = "UPDATE gl_memberlist SET expiredate = %s WHERE id = %s"
    values = (user.expiredate, user_id)
    cursor.execute(sql, values)
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    cursor.close()
    conn.close()
    return {"message": "User updated successfully"}

class Userpayment(BaseModel):
    name:str
    joindate:str
    fees: str

@app.post("/payment")
def add(data:Userpayment):
        conn=dbconn()
        cursor=conn.cursor()
        sql="INSERT INTO gl_payment (name,joindate,fees) VALUES (%s,%s,%s)"
        values= (data.name,data.joindate,data.fees)
        cursor.execute(sql,values)
        conn.commit()
        cursor.close()
        conn.close()
        return f"data inserted successfully"

@app.get("/history")
def get():
    conn=dbconn()
    cursor=conn.cursor(dictionary=True)
    sql="select * from gl_payment"
    cursor.execute(sql)
    res=cursor.fetchall()
    cursor.close()
    conn.close()
    return res

SECRET_KEY = "vebboxx"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
security = HTTPBearer()
@app.post("/login")
async def login(username: str, password: str):
    if username != "admin" or password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "role": "admin",
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer"
    }
def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


