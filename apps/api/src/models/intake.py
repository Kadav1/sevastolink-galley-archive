from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class IntakeJob(Base):
    __tablename__ = "intake_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    intake_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="captured")
    parse_status: Mapped[str] = mapped_column(String, default="not_started")
    ai_status: Mapped[str] = mapped_column(String, default="not_requested")
    review_status: Mapped[str] = mapped_column(String, default="not_started")
    raw_source_text: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String)
    source_media_asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("media_assets.id", ondelete="SET NULL")
    )
    source_snapshot_path: Mapped[str | None] = mapped_column(String)
    error_code: Mapped[str | None] = mapped_column(String)
    error_message: Mapped[str | None] = mapped_column(Text)
    resulting_recipe_id: Mapped[str | None] = mapped_column(
        ForeignKey("recipes.id", ondelete="SET NULL")
    )
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())
    completed_at: Mapped[str | None] = mapped_column(String)

    candidate: Mapped["StructuredCandidate | None"] = relationship(
        back_populates="intake_job", cascade="all, delete-orphan"
    )


class StructuredCandidate(Base):
    __tablename__ = "structured_candidates"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    intake_job_id: Mapped[str] = mapped_column(
        ForeignKey("intake_jobs.id", ondelete="CASCADE"), unique=True
    )
    candidate_status: Mapped[str] = mapped_column(String, default="pending")

    # Taxonomy (mirrors recipes, all nullable)
    title: Mapped[str | None] = mapped_column(String)
    short_description: Mapped[str | None] = mapped_column(Text)
    dish_role: Mapped[str | None] = mapped_column(String)
    primary_cuisine: Mapped[str | None] = mapped_column(String)
    secondary_cuisines: Mapped[str] = mapped_column(Text, default="[]")
    technique_family: Mapped[str | None] = mapped_column(String)
    complexity: Mapped[str | None] = mapped_column(String)
    time_class: Mapped[str | None] = mapped_column(String)
    service_format: Mapped[str | None] = mapped_column(String)
    season: Mapped[str | None] = mapped_column(String)
    ingredient_families: Mapped[str] = mapped_column(Text, default="[]")
    mood_tags: Mapped[str] = mapped_column(Text, default="[]")
    storage_profile: Mapped[str] = mapped_column(Text, default="[]")
    dietary_flags: Mapped[str] = mapped_column(Text, default="[]")
    provision_tags: Mapped[str] = mapped_column(Text, default="[]")
    sector: Mapped[str | None] = mapped_column(String)
    operational_class: Mapped[str | None] = mapped_column(String)
    heat_window: Mapped[str | None] = mapped_column(String)

    servings: Mapped[str | None] = mapped_column(String)
    prep_time_minutes: Mapped[int | None] = mapped_column(Integer)
    cook_time_minutes: Mapped[int | None] = mapped_column(Integer)
    total_time_minutes: Mapped[int | None] = mapped_column(Integer)
    rest_time_minutes: Mapped[int | None] = mapped_column(Integer)

    notes: Mapped[str | None] = mapped_column(Text)
    service_notes: Mapped[str | None] = mapped_column(Text)
    source_credit: Mapped[str | None] = mapped_column(String)

    ai_payload_json: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())

    intake_job: Mapped[IntakeJob] = relationship(back_populates="candidate")
    ingredients: Mapped[list["CandidateIngredient"]] = relationship(
        back_populates="candidate",
        order_by="CandidateIngredient.position",
        cascade="all, delete-orphan",
    )
    steps: Mapped[list["CandidateStep"]] = relationship(
        back_populates="candidate",
        order_by="CandidateStep.position",
        cascade="all, delete-orphan",
    )


class CandidateIngredient(Base):
    __tablename__ = "candidate_ingredients"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("structured_candidates.id", ondelete="CASCADE")
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    group_heading: Mapped[str | None] = mapped_column(String)
    quantity: Mapped[str | None] = mapped_column(String)
    unit: Mapped[str | None] = mapped_column(String)
    item: Mapped[str | None] = mapped_column(String)
    preparation: Mapped[str | None] = mapped_column(String)
    optional: Mapped[int] = mapped_column(Integer, default=0)
    display_text: Mapped[str | None] = mapped_column(Text)

    candidate: Mapped[StructuredCandidate] = relationship(back_populates="ingredients")


class CandidateStep(Base):
    __tablename__ = "candidate_steps"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("structured_candidates.id", ondelete="CASCADE")
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str | None] = mapped_column(Text)
    time_note: Mapped[str | None] = mapped_column(String)
    equipment_note: Mapped[str | None] = mapped_column(String)

    candidate: Mapped[StructuredCandidate] = relationship(back_populates="steps")
