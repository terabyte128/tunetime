from typing import Type, TypeVar
from pydantic.main import BaseModel
import requests
from requests.exceptions import JSONDecodeError

from requests.models import HTTPBasicAuth

from tunetime.settings import SETTINGS
from .types import (
    CursorPagingPlayHistoryObject,
    CurrentlyPlayingObject,
    PrivateUserObject,
    TrackObject,
)

BASE_URL = "https://api.spotify.com/v1"


T = TypeVar("T", bound=BaseModel)

_token_cache = {}


class SpotifyClient:
    def __init__(
        self,
        refresh_token: str,
    ) -> None:
        self.refresh_token = refresh_token

        self.session = requests.Session()

    def access_token(self):
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

        return auth_data["access_token"]

    def _request(self, method: str, path: str, deserialize_to: Type[T]) -> T:
        self.session.headers["Authorization"] = f"Bearer {self.access_token()}"
        rsp = self.session.request(method, f"{BASE_URL}/{path}")
        rsp.raise_for_status()

        data = rsp.json()
        return deserialize_to.parse_obj(data)

    def recently_played(self) -> CursorPagingPlayHistoryObject:
        return self._request(
            "GET", "me/player/recently-played", CursorPagingPlayHistoryObject
        )

    def currently_playing(self) -> CurrentlyPlayingObject | None:
        try:
            return self._request(
                "GET", "me/player/currently-playing", CurrentlyPlayingObject
            )
        except JSONDecodeError:
            return None

    def latest_track(self) -> TrackObject:
        last = self.recently_played()
        return last.items[0].track

    def get_profile(self) -> PrivateUserObject:
        return self._request("GET", "me", PrivateUserObject)
