import datetime
import uuid

from sqlalchemy import DateTime, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.Organisation import Organisation


class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(UUID(as_uuid=True), default=uuid.uuid4)
    name = Column(String, nullable=False)
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
    organisation = relationship("Organisation", back_populates="templates")

    @validates("name")
    def validate_name(self, _key, value):
        assert value != ""
        return value
