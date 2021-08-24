import datetime
import uuid

from sqlalchemy import DateTime, Column, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.ScanType import ScanType
from models.Template import Template


class TemplateScan(Base):
    __tablename__ = "template_scans"

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
    template_id = Column(
        UUID(as_uuid=True), ForeignKey(Template.id), index=True, nullable=False
    )
    template = relationship("Template", back_populates="template_scans")
    scan_type_id = Column(
        UUID(as_uuid=True), ForeignKey(ScanType.id), index=True, nullable=False
    )
    scan_type = relationship("ScanType", back_populates="template_scans")

    template_scan_triggers = relationship("TemplateScanTrigger")

    @validates("data")
    def validate_data(self, _key, value):
        assert value is not None
        return value
