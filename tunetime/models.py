import secrets
import time
from typing import Any

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import ForeignKey


def make_secure_token() -> str:
    return secrets.token_urlsafe(64)


DictStrAny = dict[str, Any]


class Base(DeclarativeBase):
    type_annotation_map = {DictStrAny: JSON}


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    spotify_id: Mapped[str] = mapped_column(unique=True)
    refresh_token: Mapped[str | None] = mapped_column()
    sessions: Mapped[list["LoginSession"]] = relationship(back_populates="user")
    tunes: Mapped[list["Tune"]] = relationship(back_populates="user")


class LoginSession(Base):
    __tablename__ = "login_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    cookie_id: Mapped[str] = mapped_column(default=make_secure_token)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="sessions")
    push_registration: Mapped[DictStrAny | None] = mapped_column(JSON(none_as_null=True))


class Tune(Base):
    __tablename__ = "tunes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="tunes")
    spotify_id: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    album: Mapped[str] = mapped_column()
    primary_artist: Mapped[str] = mapped_column()
    created_at: Mapped[int] = mapped_column(default=lambda: int(time.time()))
