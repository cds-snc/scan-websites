import datetime
import uuid

from sqlalchemy import Boolean, DateTime, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.Scan import Scan


class A11yReport(Base):
    __tablename__ = "a11y_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product = Column(String, nullable=False)
    revision = Column(String, nullable=False)
    url = Column(String)
    ci = Column(Boolean, unique=False, default=False)
    summary = Column(JSONB, nullable=False)
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
    scan = relationship("Scan", back_populates="a11y_reports")

    @validates("product")
    def validate_product(self, _key, value):
        assert value != ""
        return value

    @validates("revision")
    def validate_revision(self, _key, value):
        assert value != ""
        return value

    @validates("summary")
    def validate_summary(self, _key, value):
        assert value != ""
        return value
