import datetime
import uuid

from sqlalchemy import DateTime, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from models import Base
from models.A11yReport import A11yReport


class A11yViolation(Base):
    __tablename__ = "a11y_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation = Column(String, nullable=False)
    impact = Column(String, nullable=False)
    target = Column(Text)
    html = Column(Text)
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
    a11y_report_id = Column(
        UUID(as_uuid=True), ForeignKey(A11yReport.id), index=True, nullable=False
    )
    a11y_report = relationship("A11yReport", back_populates="a11y_violations")

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
