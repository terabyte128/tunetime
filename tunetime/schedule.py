from os import environ
import time
import random
from sqlalchemy import select

from tunetime.db import make_session
from tunetime.gchat import send_chat_message
from tunetime.models import LoginSession, TuneTime
from tunetime.subscription import send_push


def its_tunetime():
    with make_session() as db_session:
        new_tunetime = TuneTime()
        db_session.add(new_tunetime)
        db_session.commit()

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


def write_to_docker_log(text: str, prefix: str = "SCHEDULER: "):
    try:
        # attempt to write to fd for the initial docker process
        with open("/proc/1/fd/1", "a") as f:
            f.write(prefix + text + "\n")
            f.flush()
    except:
        pass

    print(prefix + text)


def wait_until_tunetime():
    hour = int(environ.get("HOUR", random.randint(0, 5)))
    minute = int(environ.get("MINUTE", random.randint(0, 59)))

    write_to_docker_log(f"tunetime is {hour}h {minute}m from now")

    for _ in range(hour):
        write_to_docker_log("sleeping for an hour...")
        time.sleep(60 * 60)

    write_to_docker_log(f"sleeping for {minute} minutes...")
    time.sleep(minute * 60)


if __name__ == "__main__":
    wait_until_tunetime()
    its_tunetime()
