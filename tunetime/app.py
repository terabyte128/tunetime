from fastapi import FastAPI

from . import oauth
from .api import user

app = FastAPI()

app.include_router(oauth.router, prefix="/oauth2")
app.include_router(user.router, prefix="/api/profile")


@app.get("/")
def root():
    return "root"
