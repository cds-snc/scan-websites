import datetime
import uuid

from sqlalchemy import DateTime, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.SecurityReport import SecurityReport


class SecurityViolation(Base):
    __tablename__ = "security_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation = Column(String, nullable=False)
    risk = Column(String, nullable=False)
    confidence = Column(String, nullable=False)
    solution = Column(Text)
    reference = Column(Text)
    target = Column(Text)
    data = Column(JSONB, nullable=False)
    tags = Column(JSONB, nullable=False)
    message = Column(Text)
    url = Column(String)
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
    security_report_id = Column(
        UUID(as_uuid=True), ForeignKey(SecurityReport.id), index=True, nullable=False
    )
    security_report = relationship(
        "SecurityReport", back_populates="security_violations"
    )

    @validates("violation")
    def validate_violation(self, _key, value):
        assert value != ""
        return value

    @validates("impact")
    def validate_impact(self, _key, value):
        assert value != ""
        return value

    @validates("data")
    def validate_data(self, _key, value):
        assert value != ""
        return value

    @validates("tags")
    def validate_tags(self, _key, value):
        assert value != ""
        return value
