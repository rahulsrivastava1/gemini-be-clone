import os
import time

import redis
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Redis setup
r = redis.Redis(host="localhost", port=6379, db=0)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def call_gemini_api(text):
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY,
    }
    data = {"contents": [{"parts": [{"text": text}]}]}
    response = requests.post(GEMINI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "[Gemini API: Unexpected response format]"
    else:
        return f"[Gemini API Error: {response.status_code}]"


def process_queue():
    while True:
        message_id = r.rpop("gemini_message_queue")
        if message_id is None:
            time.sleep(2)
            continue
        try:
            message_id = int(message_id.decode()) if isinstance(message_id, bytes) else int(message_id)
        except Exception:
            continue
        db = SessionLocal()
        try:
            msg = db.query(Message).filter(Message.id == message_id).first()
            if not msg:
                continue
            msg.status = "processing"
            db.commit()
            db.refresh(msg)
            gemini_response = call_gemini_api(msg.content)
            msg.response = gemini_response
            msg.status = "completed"
            db.commit()
        except Exception as e:
            if "msg" in locals() and msg:
                msg.status = "failed"
                db.commit()
        finally:
            db.close()
        time.sleep(1)


if __name__ == "__main__":
    process_queue()
