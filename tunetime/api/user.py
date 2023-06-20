from fastapi.routing import APIRouter

from tunetime.oauth import SessionDependency
from tunetime.spotify.client import PushRegistration
from tunetime.spotify.types import PrivateUserObject, TrackObject


router = APIRouter()


@router.get("/", response_model=PrivateUserObject)
def get_user(session: SessionDependency):
    return session.get_profile()


@router.get("/recent", response_model=TrackObject)
def get_recent(session: SessionDependency):
    return session.latest_track()


@router.post("/register-push")
def register_push(
    session: SessionDependency, push_registration: PushRegistration
):
    session.push_registration = push_registration
    session.upsert()
