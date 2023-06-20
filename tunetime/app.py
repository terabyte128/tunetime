from fastapi import FastAPI

from . import oauth
from .api import user, message

app = FastAPI()

app.include_router(oauth.router, prefix="/oauth")
app.include_router(user.router, prefix="/api/profile")
app.include_router(message.router, prefix="/api/message")


@app.get("/")
def root():
    return "root"
