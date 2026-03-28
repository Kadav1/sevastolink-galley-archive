from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, CheckConstraint, ForeignKey, Integer, String, Text,
    Computed,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class RecipeSource(Base):
    __tablename__ = "recipe_sources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    source_title: Mapped[str | None] = mapped_column(String)
    source_author: Mapped[str | None] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String)
    source_notes: Mapped[str | None] = mapped_column(Text)
    raw_source_text: Mapped[str | None] = mapped_column(Text)
    source_media_asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("media_assets.id", ondelete="SET NULL")
    )
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())

    recipe: Mapped["Recipe | None"] = relationship(back_populates="source")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    short_description: Mapped[str | None] = mapped_column(Text)

    # Primary taxonomy
    dish_role: Mapped[str | None] = mapped_column(String)
    primary_cuisine: Mapped[str | None] = mapped_column(String)
    technique_family: Mapped[str | None] = mapped_column(String)
    complexity: Mapped[str | None] = mapped_column(String)
    time_class: Mapped[str | None] = mapped_column(String)
    service_format: Mapped[str | None] = mapped_column(String)
    season: Mapped[str | None] = mapped_column(String)

    # Multi-select taxonomy (JSON arrays)
    secondary_cuisines: Mapped[str] = mapped_column(Text, default="[]")
    ingredient_families: Mapped[str] = mapped_column(Text, default="[]")
    mood_tags: Mapped[str] = mapped_column(Text, default="[]")
    storage_profile: Mapped[str] = mapped_column(Text, default="[]")
    dietary_flags: Mapped[str] = mapped_column(Text, default="[]")
    provision_tags: Mapped[str] = mapped_column(Text, default="[]")

    # Sevastolink overlay
    sector: Mapped[str | None] = mapped_column(String)
    operational_class: Mapped[str | None] = mapped_column(String)
    heat_window: Mapped[str | None] = mapped_column(String)

    # Timing
    servings: Mapped[str | None] = mapped_column(String)
    prep_time_minutes: Mapped[int | None] = mapped_column(Integer)
    cook_time_minutes: Mapped[int | None] = mapped_column(Integer)
    # total_time_minutes is a virtual generated column in the DB; read-only here
    rest_time_minutes: Mapped[int | None] = mapped_column(Integer)

    # Trust and state
    verification_state: Mapped[str] = mapped_column(String, default="Draft")
    favorite: Mapped[int] = mapped_column(Integer, default=0)
    archived: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[int | None] = mapped_column(Integer)

    # Search support
    ingredient_text: Mapped[str | None] = mapped_column(Text)

    # Cover image
    cover_media_asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("media_assets.id", ondelete="SET NULL")
    )

    # Linkage
    source_id: Mapped[str | None] = mapped_column(
        ForeignKey("recipe_sources.id", ondelete="SET NULL")
    )
    intake_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("intake_jobs.id", ondelete="SET NULL")
    )

    # Timestamps
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    last_viewed_at: Mapped[str | None] = mapped_column(String)
    last_cooked_at: Mapped[str | None] = mapped_column(String)

    # Relationships
    source: Mapped[RecipeSource | None] = relationship(
        "RecipeSource", back_populates="recipe", foreign_keys=[source_id]
    )
    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        order_by="RecipeIngredient.position",
        cascade="all, delete-orphan",
    )
    steps: Mapped[list["RecipeStep"]] = relationship(
        back_populates="recipe",
        order_by="RecipeStep.position",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["RecipeNote"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    recipe_id: Mapped[str] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    group_heading: Mapped[str | None] = mapped_column(String)
    quantity: Mapped[str | None] = mapped_column(String)
    unit: Mapped[str | None] = mapped_column(String)
    item: Mapped[str] = mapped_column(String, nullable=False)
    preparation: Mapped[str | None] = mapped_column(String)
    optional: Mapped[int] = mapped_column(Integer, default=0)
    display_text: Mapped[str | None] = mapped_column(Text)

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    recipe_id: Mapped[str] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    time_note: Mapped[str | None] = mapped_column(String)
    equipment_note: Mapped[str | None] = mapped_column(String)

    recipe: Mapped[Recipe] = relationship(back_populates="steps")


class RecipeNote(Base):
    __tablename__ = "recipe_notes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    recipe_id: Mapped[str] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    note_type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat())

    recipe: Mapped[Recipe] = relationship(back_populates="notes")
