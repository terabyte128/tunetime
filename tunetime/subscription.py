from pywebpush import WebPushException, webpush
from tunetime.gchat import send_chat_message
from sqlalchemy import select

from tunetime.db import make_session
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


def its_tunetime():
    with make_session() as db_session:
        stmt = select(LoginSession).where(
            LoginSession.push_registration != None
        )
        results = db_session.execute(stmt).scalars()

        send_chat_message(
            "it's tunetime! open https://tunetime.wolfbyt.es to share your tunes :)"
        )

        for session in results:
            send_push(
                session,
                "it's tunetime! share ur tunes with ur friends.",
                db_session,
            )
