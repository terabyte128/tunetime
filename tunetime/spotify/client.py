from typing import Type, TypeVar, cast
from pydantic.main import BaseModel
import requests
import time
from requests.exceptions import JSONDecodeError

from requests.models import HTTPBasicAuth
from tinydb.table import Document
from tunetime.db import SessionTable

from tunetime.settings import SETTINGS
from .types import (
    CursorPagingPlayHistoryObject,
    CurrentlyPlayingObject,
    PrivateUserObject,
    TrackObject,
)

BASE_URL = "https://api.spotify.com/v1"


class PushRegistration(BaseModel):
    endpoint: str
    keys: dict


class SpotifySession(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int
    push_registration: PushRegistration | None


def requires_auth(inner):
    def check_and_refresh(self: "SpotifyClient", **args):
        if self.access_token is None or self.expires_at < int(time.time()):
            auth_rsp = requests.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
                auth=HTTPBasicAuth(SETTINGS.client_id, SETTINGS.client_secret),
            )
            auth_rsp.raise_for_status()
            auth_data = auth_rsp.json()

            self.access_token = auth_data["access_token"]
            self.refresh_token = auth_data.get(
                "refresh_token", self.refresh_token
            )
            self.expires_at = int(time.time()) + int(auth_data["expires_in"])

            self.upsert()

        return inner(self, **args)

    return check_and_refresh


T = TypeVar("T", bound=BaseModel)


class SpotifyClient:
    def __init__(
        self,
        session_id: int,
        access_token: str,
        refresh_token: str,
        expires_at: int,
        push_registration: PushRegistration | None = None,
        **_,  # fuckit ignore everything else
    ) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.session_id = session_id
        self.push_registration = push_registration

        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"

    def _request(self, method: str, path: str, deserialize_to: Type[T]) -> T:
        rsp = self.session.request(method, f"{BASE_URL}/{path}")
        rsp.raise_for_status()

        data = rsp.json()
        return deserialize_to.parse_obj(data)

    @requires_auth
    def recently_played(self) -> CursorPagingPlayHistoryObject:
        return self._request(
            "GET", "me/player/recently-played", CursorPagingPlayHistoryObject
        )

    @requires_auth
    def currently_playing(self) -> CurrentlyPlayingObject | None:
        try:
            return self._request(
                "GET", "me/player/currently-playing", CurrentlyPlayingObject
            )
        except JSONDecodeError:
            return None

    def latest_track(self) -> TrackObject:
        current = self.currently_playing()

        if current:
            return current.item

        else:
            last = self.recently_played()
            return last.items[0].track

    @requires_auth
    def get_profile(self) -> PrivateUserObject:
        return self._request("GET", "me", PrivateUserObject)

    def upsert(self):
        SessionTable.upsert(
            Document(
                SpotifySession(
                    access_token=self.access_token,
                    refresh_token=self.refresh_token,
                    expires_at=self.expires_at,
                    push_registration=self.push_registration,
                ).dict(),
                doc_id=self.session_id,
            )
        )

    @classmethod
    def from_id(cls, session_id: int):
        doc = SessionTable.get(doc_id=session_id)

        if doc is None:
            raise ValueError("unknown session id")

        return cls(session_id=session_id, **cast(Document, doc))

    @classmethod
    def from_tokens(
        cls,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        push_registration: PushRegistration | None = None,
    ):
        session = SpotifySession(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=int(time.time()) + expires_in,
            push_registration=push_registration,
        )

        session_id = SessionTable.insert(session.dict())
        return cls(session_id=session_id, **session.dict())
