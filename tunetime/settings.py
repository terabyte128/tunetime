from pydantic import BaseSettings


class _Settings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str
    chat_url: str
    webpush_private_key: str
    db_connection: str = (
        "postgresql://tunetime:tunetime@localhost:5543/tunetime"
    )


SETTINGS = _Settings()  # pyright: ignore
