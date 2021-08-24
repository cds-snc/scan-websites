import datetime
import uuid

from sqlalchemy import DateTime, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models import Base
from models.Organisation import Organisation
from models.ScanType import ScanType
from models.Template import Template


class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    organisation = relationship("Organisation", back_populates="scans")
    template_id = Column(
        UUID(as_uuid=True), ForeignKey(Template.id), index=True, nullable=False
    )
    template = relationship("Template", back_populates="scans")
    scan_type_id = Column(
        UUID(as_uuid=True), ForeignKey(ScanType.id), index=True, nullable=False
    )
    scan_type = relationship("ScanType", back_populates="scans")
