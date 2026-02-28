from app import db
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime, timezone

class UserHealthLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    log_date: so.Mapped[datetime] = so.mapped_column(sa.DATE, nullable=False, default=lambda: datetime.now(timezone.utc))
    steps: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    sleep: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    blood: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    heart: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    user_comment: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)

    user = db.relationship("User", back_populates="health_logs")

    __table_args__ = (
        db.UniqueConstraint("user_id", "log_date"),
    )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    health_logs = db.relationship(
        "UserHealthLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )