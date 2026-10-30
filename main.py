import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

class UserAuth(BaseModel):
    id: str
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    photo_url: str = ""
    referred_by: str = None

class AdWatch(BaseModel):
    user_id: str
    ad_value: float = 0.5

class Withdrawal(BaseModel):
    user_id: str
    user_name: str
    amount: float
    method: str
    account: str

@app.get("/")
def home():
    return {"status": "Looby API is running smoothly!"}

@app.post("/api/user/auth")
def auth_user(data: UserAuth):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (data.id,))
    user = cur.fetchone()
    
    if not user:
        cur.execute(
            """
            INSERT INTO users (id, first_name, last_name, username, photo_url, referred_by)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
            """,
            (data.id, data.first_name, data.last_name, data.username, data.photo_url, data.referred_by)
        )
        user = cur.fetchone()
        conn.commit()
    
    cur.close()
    conn.close()
    return user

@app.post("/api/user/watch-ad")
def watch_ad(data: AdWatch):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE users 
        SET balance = balance + %s,
            total_earned = total_earned + %s,
            lifetime_ad_count = lifetime_ad_count + 1,
            daily_ad_count = daily_ad_count + 1
        WHERE id = %s RETURNING balance, daily_ad_count, total_earned
        """,
        (data.ad_value, data.ad_value, data.user_id)
    )
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@app.post("/api/withdraw")
def request_withdraw(data: Withdrawal):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE id = %s", (data.id if hasattr(data, 'id') else data.user_id,))
    user = cur.fetchone()
    if not user or user["balance"] < data.amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (data.amount, data.user_id))
    cur.execute(
        """
        INSERT INTO withdrawals (user_id, user_name, amount, method, account)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        """,
        (data.user_id, data.user_name, data.amount, data.method, data.account)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "message": "Withdrawal submitted"}
