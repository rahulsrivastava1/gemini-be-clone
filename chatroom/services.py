from typing import List

from sqlalchemy.orm import Session

from database.cache import CacheService, get_cache_key_user_chatrooms

from .models import Chatroom


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
        from datetime import datetime

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
