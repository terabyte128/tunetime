import secrets
from typing import Annotated, TypedDict

import requests
from fastapi import APIRouter, Cookie, Depends, HTTPException
from requests.models import HTTPBasicAuth
from sqlalchemy import select
from starlette.responses import RedirectResponse
from tinydb import Query

from tunetime.spotify.client import SpotifyClient

from .db import make_session
from .models import LoginSession, User
from .settings import SETTINGS

router = APIRouter()
q = Query()


def get_url(state: str):
    url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={SETTINGS.client_id}&scope=user-read-recently-played user-read-currently-playing&redirect_uri={SETTINGS.redirect_uri}&state={state}"
    return url


state_cache = []


class SessionData(TypedDict):
    spotify_client: SpotifyClient
    login_session: LoginSession


async def _require_session(
    session_id: Annotated[str | None, Cookie()] = None
) -> SessionData:
    if not session_id:
        raise HTTPException(401, "no session")

    with make_session() as session:
        stmt = select(LoginSession).where(LoginSession.cookie_id == session_id)
        login_session = session.execute(stmt).scalar()

        if login_session is None:
            raise HTTPException(401, "invalid session")

        user = login_session.user

    return {
        "spotify_client": SpotifyClient(user.refresh_token),
        "login_session": login_session,
    }


SessionDependency = Annotated[SessionData, Depends(_require_session)]


@router.get("/login")
def login(session_id: Annotated[str | None, Cookie()] = None):
    if session_id is not None:
        with make_session() as session:
            stmt = select(LoginSession).where(
                LoginSession.cookie_id == session_id
            )
            login_session = session.execute(stmt).scalar()

            if login_session is not None:
                return RedirectResponse("/")

    state = secrets.token_urlsafe()
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

    user_rsp = requests.get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {auth_data['access_token']}"},
    )
    user_rsp.raise_for_status()
    user_data = user_rsp.json()

    with make_session() as session:
        stmt = select(User).where(User.spotify_id == user_data["id"])
        user = session.execute(stmt).scalar()

        if user is None:
            user = User(spotify_id=user_data["id"])

        user.refresh_token = auth_data["refresh_token"]

        if user.override_display_name is None:
            user.override_display_name = user_data.get("display_name")

        login_session = LoginSession()

        user.sessions.append(login_session)

        session.add(user)
        session.commit()

        rsp = RedirectResponse("/")
        rsp.set_cookie(
            "session_id",
            str(login_session.cookie_id),
            httponly=True,
            secure=True,
        )

        return rsp
