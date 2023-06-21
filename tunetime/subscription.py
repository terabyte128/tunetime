from pywebpush import WebPushException, webpush
from requests.models import Response
from sqlalchemy import select, null

from tunetime.db import make_session
from tunetime.models import LoginSession
from tunetime.settings import SETTINGS


def send_push(session: LoginSession, message: str):
    if not session.push_registration:
        raise ValueError("session has no push registration")

    try:
        webpush(
            session.push_registration,
            message,
            SETTINGS.webpush_private_key,
            vapid_claims={"sub": "mailto:terabyte128@gmail.com"},
        )
    except WebPushException as e:
        if not e.response:
            raise

        rsp: Response = e.response

        # remove the registration, no longer valid
        if rsp.status_code in [404, 410]:
            with make_session() as db_session:
                session.push_registration = null()  # type: ignore
                db_session.add(session)
                db_session.commit()


def its_tunetime():
    with make_session() as db_session:
        stmt = select(LoginSession).where(
            LoginSession.push_registration != None
        )
        results = db_session.execute(stmt).scalars()

        for session in results:
            send_push(session, "it's tunetime! share ur tunes with ur friends.")
