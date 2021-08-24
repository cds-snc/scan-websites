import datetime
import uuid

from sqlalchemy import DateTime, Column, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.TemplateScan import TemplateScan


class TemplateScanTrigger(Base):
    __tablename__ = "template_scan_triggers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(JSONB, nullable=False)
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
    template_scan_id = Column(
        UUID(as_uuid=True), ForeignKey(TemplateScan.id), index=True, nullable=False
    )
    template_scan = relationship(
        "TemplateScan", back_populates="template_scan_triggers"
    )

    @validates("data")
    def validate_name(self, _key, value):
        assert value != ""
        return value
