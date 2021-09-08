import bcrypt
import datetime
import os
import uuid

from sqlalchemy import DateTime, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.Organisation import Organisation

BCRYPT_WORK_FACTOR = int(os.environ.get("BCRYPT_WORK_FACTOR", "14"))


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email_address = Column(String, nullable=False, index=False, unique=True)
    password_hash = Column(String, nullable=False)
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
        self.password_hash = bcrypt.hashpw(str.encode(password), bcrypt.gensalt(BCRYPT_WORK_FACTOR))

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
