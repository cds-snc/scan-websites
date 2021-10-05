import datetime
import uuid

from sqlalchemy import DateTime, Column, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from models import Base


class TemplateScanTrigger(Base):
    __tablename__ = "template_scan_triggers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=False, unique=True)
    callback = Column(JSONB, nullable=False)
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

    template_scans = relationship("TemplateScan")

    @validates("callback")
    def validate_callback(self, _key, value):
        assert value != ""
        return value

    @validates("name")
    def validate_name(self, _key, value):
        assert value != ""
        return value
