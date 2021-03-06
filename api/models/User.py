import bcrypt
import datetime
import os
import uuid

from sqlalchemy import DateTime, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as VALIDATOR_UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.Organisation import Organisation

from pydantic import BaseModel, validator
from starlette.authentication import BaseUser

from typing import Optional

BCRYPT_WORK_FACTOR = 14 if os.environ.get("CI", False) is False else 4


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email_address = Column(String, nullable=False, index=False, unique=True)
    password_hash = Column(String, nullable=True)
    access_token = Column(UUID(as_uuid=True), default=uuid.uuid4)
    created_at = Column(
        DateTime,
        index=False,
        unique=False,
        nullable=False,
        default=datetime.datetime.utcnow,
    )
    updated_at = Column(
        DateTime,
        index=False,
        unique=False,
        nullable=True,
        onupdate=datetime.datetime.utcnow,
    )
    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey(Organisation.id), index=True, nullable=False
    )
    organisation = relationship("Organisation", back_populates="users")

    @property
    def password(self):
        raise AttributeError("Password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(
            str.encode(password), bcrypt.gensalt(BCRYPT_WORK_FACTOR)
        )

    @validates("name")
    def validate_name(self, _key, value):
        assert value != ""
        return value

    @validates("email_address")
    def validate_email_address(self, _key, value):
        assert value != ""
        return value

    @validates("password_hash")
    def validate_password_hash(self, _key, value):
        assert value != ""
        return value


class AuthenticatedUser(BaseModel, BaseUser):
    email_address: Optional[str]
    name: Optional[str]
    organisation_id: Optional[VALIDATOR_UUID]

    # UUID is not JSON serializable so we validate and then cast to str
    @validator("organisation_id")
    def must_be_uuid_return_str(cls, v):
        assert type(v) is VALIDATOR_UUID, "must UUID"
        return str(v)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.name

    @property
    def identity(self) -> str:
        raise NotImplementedError()  # pragma: no cover
