from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class SettingEntry(Base):
    """Key-value row in the settings table."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default="(datetime('now'))",
    )
