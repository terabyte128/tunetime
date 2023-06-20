import time
from typing import Annotated
from uuid import uuid4

import requests
from fastapi import APIRouter, Cookie, Depends, HTTPException
from requests.models import HTTPBasicAuth
from starlette.responses import RedirectResponse
from tinydb import Query

from tunetime.spotify.client import SpotifyClient

from .settings import SETTINGS

router = APIRouter()
q = Query()


def get_url(state: str):
    url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={SETTINGS.client_id}&scope=user-read-recently-played user-read-currently-playing&redirect_uri={SETTINGS.redirect_uri}&state={state}"
    return url


state_cache = []


async def _require_session(session_id: Annotated[int | None, Cookie()] = None):
    if not session_id:
        raise HTTPException(401, "no session")

    return SpotifyClient.from_id(session_id)


SessionDependency = Annotated[SpotifyClient, Depends(_require_session)]


@router.get("/login")
def login(session_id: Annotated[int | None, Cookie()] = None):
    if session_id:
        return RedirectResponse("/")

    state = uuid4().hex
    state_cache.append(state)
    return RedirectResponse(get_url(state))


@router.get("/callback")
def callback(code: str, state: str):
    if state not in state_cache:
        raise HTTPException(401, detail="unknown state")

    state_cache.remove(state)

    auth_rsp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SETTINGS.redirect_uri,
        },
        auth=HTTPBasicAuth(SETTINGS.client_id, SETTINGS.client_secret),
    )

    auth_rsp.raise_for_status()
    auth_data = auth_rsp.json()

    client = SpotifyClient.from_tokens(
        auth_data["access_token"],
        auth_data["refresh_token"],
        auth_data["expires_in"],
    )

    rsp = RedirectResponse("/")
    rsp.set_cookie("session_id", str(client.session_id), httponly=True)

    return rsp
