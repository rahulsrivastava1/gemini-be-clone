from fastapi import FastAPI

from auth.router import router, user_router
from chatroom.router import router as chatroom_router

app = FastAPI()

app.include_router(router)
app.include_router(user_router)
app.include_router(chatroom_router)
