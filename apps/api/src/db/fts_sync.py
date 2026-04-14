"""Shared FTS5 synchronisation helper for the recipe_search_fts virtual table."""

from sqlalchemy import text
from sqlalchemy.orm import Session


def sync_fts(db: Session, recipe: object) -> None:
    """Upsert recipe into the standalone FTS5 table."""
    notes_text = " ".join(n.content for n in recipe.notes) if recipe.notes else ""  # type: ignore[attr-defined]
    db.execute(
        text("DELETE FROM recipe_search_fts WHERE recipe_id = :rid"),
        {"rid": recipe.id},  # type: ignore[attr-defined]
    )
    db.execute(
        text(
            "INSERT INTO recipe_search_fts "
            "(recipe_id, title, short_description, notes, ingredient_text) "
            "VALUES (:rid, :title, :desc, :notes, :ingr)"
        ),
        {
            "rid": recipe.id,  # type: ignore[attr-defined]
            "title": recipe.title or "",  # type: ignore[attr-defined]
            "desc": recipe.short_description or "",  # type: ignore[attr-defined]
            "notes": notes_text,
            "ingr": recipe.ingredient_text or "",  # type: ignore[attr-defined]
        },
    )
