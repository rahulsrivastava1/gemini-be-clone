import os

from fastapi import FastAPI

from auth.router import router, user_router
from chatroom.router import router as chatroom_router

app = FastAPI()

app.include_router(router)
app.include_router(user_router)
app.include_router(chatroom_router)

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 4000))
    uvicorn.run(app, host="0.0.0.0", port=port)
