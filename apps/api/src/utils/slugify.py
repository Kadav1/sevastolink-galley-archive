"""Slug generation from recipe titles."""

import re
from sqlalchemy.orm import Session


def slugify(title: str) -> str:
    """Convert a title to a URL slug: lowercase, hyphens, no special chars."""
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s)
    return s.strip("-") or "recipe"


def unique_slug(db: Session, title: str) -> str:
    """Generate a slug and append a numeric suffix if there is a collision."""
    from src.models.recipe import Recipe  # local import to avoid circular

    base = slugify(title)
    slug = base
    counter = 2
    while db.query(Recipe).filter(Recipe.slug == slug).first() is not None:
        slug = f"{base}-{counter}"
        counter += 1
    return slug
