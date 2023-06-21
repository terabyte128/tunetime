from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.engine import create

from tunetime.db import make_session
from tunetime.gchat import send_chat_message
from tunetime.models import Tune, User
from tunetime.oauth import SessionDependency
from tunetime.spotify.types import PrivateUserObject, TrackObject

from . import oauth

app = FastAPI()

app.include_router(oauth.router, prefix="/oauth2")


@app.get("/")
def root():
    return "root"


@app.get("/api/profile", response_model=PrivateUserObject)
def get_user(session: SessionDependency):
    return session["spotify_client"].get_profile()


@app.get("/api/profile/recent", response_model=TrackObject)
def get_recent(session: SessionDependency):
    return session["spotify_client"].latest_track()


class PushRegistration(BaseModel):
    endpoint: str
    keys: dict


@app.post("/api/profile/register-push")
def register_push(
    session: SessionDependency, push_registration: PushRegistration
):
    with make_session() as db_session:
        login_session = session["login_session"]
        login_session.push_registration = push_registration.dict()

        db_session.add(login_session)
        db_session.commit()


@app.delete("/api/profile/register-push")
def delete_push(session: SessionDependency):
    with make_session() as db_session:
        login_session = session["login_session"]
        login_session.push_registration = None

        db_session.add(login_session)
        db_session.commit()


@app.post("/api/profile/share-tune")
def share(session: SessionDependency):
    spotify = session["spotify_client"]
    login_session = session["login_session"]
    user = login_session.user

    latest_track = spotify.latest_track()
    profile = spotify.get_profile()

    with make_session() as db_session:
        db_session.add(user)

        user.tunes.append(
            Tune(
                spotify_id=latest_track.id,
                name=latest_track.name,
                album=latest_track.album.name,
                primary_artist=latest_track.artists[0].name,
            )
        )

        db_session.commit()

    message = f"{profile.display_name} most recently listened to {latest_track.name} by {', '.join([i.name for i in latest_track.artists])} from the album {latest_track.album.name}: {latest_track.external_urls.spotify}"

    send_chat_message(message)


class TuneResponse(BaseModel):
    name: str
    album: str
    primary_artist: str
    user: str
    created_at: int


@app.get("/api/tunes", response_model=list[TuneResponse])
def tunes():
    with make_session() as db_session:
        stmt = select(Tune).join(User).order_by(Tune.created_at.desc())
        data = db_session.scalars(stmt).all()

        return [
            TuneResponse(
                name=i.name,
                album=i.album,
                primary_artist=i.primary_artist,
                user=i.user.spotify_id,
                created_at=i.created_at,
            )
            for i in data
        ]
