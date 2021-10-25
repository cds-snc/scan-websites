import datetime
import uuid

from sqlalchemy import DateTime, Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models import Base
from models.Scan import Scan


class ScanIgnore(Base):
    __tablename__ = "scan_ignores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation = Column(String, nullable=False)
    location = Column(String, nullable=False)
    condition = Column(String, nullable=False)
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
    scan_id = Column(
        UUID(as_uuid=True), ForeignKey(Scan.id), index=True, nullable=False
    )
    scan = relationship("Scan", back_populates="scan_ignores")
