import asyncio
import os
import threading
from datetime import datetime
from typing import List

import aiohttp
from sqlalchemy.orm import Session

from database.cache import CacheService, get_cache_key_user_chatrooms
from database.db_connection import SessionLocal

from .models import Chatroom, Message

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


async def call_gemini_api_async(text: str) -> str:
    """
    Call Gemini API asynchronously
    """
    if not GEMINI_API_KEY:
        return "[Gemini API Error: API key not configured. Please set GEMINI_API_KEY environment variable]"

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY,
    }
    data = {"contents": [{"parts": [{"text": text}]}]}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GEMINI_API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    return f"[Gemini API Error: {response.status}]"
    except Exception as e:
        return f"[Gemini API Error: {str(e)}]"


async def process_message_async(message_id: int):
    """
    Process a message asynchronously by calling Gemini API and updating the database
    """
    db = SessionLocal()
    try:
        # Get the message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return

        # Update status to processing
        message.status = "processing"
        db.commit()
        db.refresh(message)

        # Call Gemini API with the message content
        message_content = str(message.content)
        gemini_response = await call_gemini_api_async(message_content)

        # Update message with response
        message.response = gemini_response
        message.status = "completed"
        db.commit()

    except Exception as e:
        # Update status to failed if there's an error
        if "message" in locals() and message:
            message.status = "failed"
            db.commit()
        print(f"Error processing message {message_id}: {e}")
    finally:
        db.close()


def run_async_in_thread(message_id: int):
    """
    Run the async function in a separate thread with its own event loop
    """

    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(process_message_async(message_id))
        finally:
            loop.close()

    thread = threading.Thread(target=run_async)
    thread.daemon = True
    thread.start()


def create_chatroom(db: Session, user_id: int) -> Chatroom:
    chatroom = Chatroom(user_id=user_id)
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)

    # Invalidate cache for this user's chatrooms
    cache_key = get_cache_key_user_chatrooms(user_id)
    CacheService.delete(cache_key)

    return chatroom


def get_user_chatrooms(db: Session, user_id: int) -> List[Chatroom]:
    """Get all chatrooms for a user with caching"""
    # Try to get from cache first
    cache_key = get_cache_key_user_chatrooms(user_id)
    cached_data = CacheService.get(cache_key)

    if cached_data:
        # Convert cached data back to Chatroom objects
        chatrooms = []
        for chatroom_data in cached_data:
            created_at = None
            if chatroom_data["created_at"] is not None:
                created_at = datetime.fromisoformat(chatroom_data["created_at"])

            chatroom = Chatroom(id=chatroom_data["id"], user_id=chatroom_data["user_id"], created_at=created_at)
            chatrooms.append(chatroom)
        return chatrooms

    # If not in cache, get from database
    chatrooms = db.query(Chatroom).filter(Chatroom.user_id == user_id).all()

    # Try to cache the results for 5 minutes (but don't fail if Redis is unavailable)
    try:
        cache_data = []
        for chatroom in chatrooms:
            created_at_str = None
            if chatroom.created_at is not None:
                created_at_str = chatroom.created_at.isoformat()

            cache_data.append(
                {
                    "id": chatroom.id,
                    "user_id": chatroom.user_id,
                    "created_at": created_at_str,
                }
            )
        CacheService.set(cache_key, cache_data, expire=300)
    except Exception as e:
        print(f"Warning: Failed to cache chatrooms for user {user_id}: {e}")
        # Continue without caching - this is not a critical failure

    return chatrooms


def get_chatroom_by_id(db: Session, chatroom_id: int, user_id: int) -> Chatroom:
    """Get a specific chatroom by ID, ensuring the user has access to it"""
    chatroom = db.query(Chatroom).filter(Chatroom.id == chatroom_id, Chatroom.user_id == user_id).first()

    if not chatroom:
        raise ValueError("Chatroom not found or access denied")

    return chatroom


def save_message_and_process_async(db: Session, user_id: int, chatroom_id: int, content: str) -> Message:
    """
    Save a message to the database and start async processing in a background thread
    """
    # Create message with pending status
    db_message = Message(user_id=user_id, chatroom_id=chatroom_id, content=content, status="pending")
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Start async processing in a background thread
    message_id = int(db_message.id)
    run_async_in_thread(message_id)

    return db_message
