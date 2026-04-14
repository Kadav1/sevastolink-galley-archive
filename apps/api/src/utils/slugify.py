"""Slug generation from recipe titles."""

import re
from sqlalchemy.orm import Session


def slugify(title: str) -> str:
    """Convert a title to a URL slug: lowercase, hyphens, no special chars."""
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s)
    return s.strip("-") or "recipe"


_MAX_SLUG_ATTEMPTS = 100


def unique_slug(db: Session, title: str) -> str:
    """Generate a slug and append a numeric suffix if there is a collision.

    NOTE: This issues one query per collision attempt. It is designed for
    interactive single-recipe creation and is not suitable for bulk imports.
    For bulk intake, pre-generate slugs from the full title list and deduplicate
    in-process before calling the DB.
    """
    from src.models.recipe import Recipe  # local import to avoid circular

    base = slugify(title)
    slug = base
    counter = 2
    while db.query(Recipe).filter(Recipe.slug == slug).first() is not None:
        if counter > _MAX_SLUG_ATTEMPTS:
            raise RuntimeError(
                f"Could not generate a unique slug for title {title!r} after "
                f"{_MAX_SLUG_ATTEMPTS} attempts."
            )
        slug = f"{base}-{counter}"
        counter += 1
    return slug
