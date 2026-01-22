from sqlalchemy import Column, String, Text

from app.models.base import Base, TimestampMixin, generate_uuid


class AuditLog(Base, TimestampMixin):
    """Audit log for tracking important events."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    # Actor
    user_id = Column(String(36), nullable=True)  # nullable for system events

    # Event info
    action = Column(String(100), nullable=False)  # e.g., "job.created", "profile.created"
    resource_type = Column(String(100), nullable=False)  # e.g., "job", "brand_profile"
    resource_id = Column(String(36), nullable=True)

    # Context
    brand_id = Column(String(36), nullable=True)
    details_json = Column(Text, nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type}>"
