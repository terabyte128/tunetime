from pywebpush import WebPushException, webpush
from tunetime.models import LoginSession
from tunetime.settings import SETTINGS


def send_push(session: LoginSession, message: str, db_session):
    if not session.push_registration:
        raise ValueError("session has no push registration")

    try:
        print("pushing", session.user.spotify_id)
        webpush(
            session.push_registration,
            message,
            SETTINGS.webpush_private_key,
            vapid_claims={"sub": "mailto:terabyte128@gmail.com"},
        )
    except WebPushException as e:
        # TODO be better about failures
        session.push_registration = None
        db_session.add(session)
        db_session.commit()

