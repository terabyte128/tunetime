from fastapi import APIRouter

from tunetime.oauth import SessionDependency

from ..gchat import send_chat_message

router = APIRouter()


@router.post("/")
def send_message(session: SessionDependency):
    latest_track = session.latest_track()
    profile = session.get_profile()

    message = f"{profile.display_name} most recently listened to {latest_track.name} from the album {latest_track.album.name}: {latest_track.external_urls.spotify}"

    send_chat_message(message)
