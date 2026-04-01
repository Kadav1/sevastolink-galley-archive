"""
Dev seed script — inserts representative fixture recipes for development.

Usage (from apps/api/):
    python ../../scripts/seed/seed_dev.py

Usage (from repo root):
    cd apps/api && python ../../scripts/seed/seed_dev.py

Idempotent: skips recipes whose slug already exists.
"""

import json
import sys
from pathlib import Path

# Ensure apps/api is on the path
API_DIR = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_DIR))

from src.db.database import SessionLocal
from src.db.init_db import init_db
from src.models.recipe import Recipe, RecipeIngredient, RecipeNote, RecipeStep
from src.utils.ids import new_ulid
from sqlalchemy import text


def _sync_fts(db, recipe: Recipe) -> None:
    notes_text = " ".join(n.content for n in recipe.notes) if recipe.notes else ""
    db.execute(text("DELETE FROM recipe_search_fts WHERE recipe_id = :rid"), {"rid": recipe.id})
    db.execute(
        text(
            "INSERT INTO recipe_search_fts "
            "(recipe_id, title, short_description, notes, ingredient_text) "
            "VALUES (:rid, :title, :desc, :notes, :ingr)"
        ),
        {
            "rid": recipe.id,
            "title": recipe.title or "",
            "desc": recipe.short_description or "",
            "notes": notes_text,
            "ingr": recipe.ingredient_text or "",
        },
    )


FIXTURES = [
    {
        "slug": "shakshuka",
        "title": "Shakshuka",
        "short_description": "Eggs poached in a spiced tomato and pepper sauce. Quick weeknight staple.",
        "dish_role": "Breakfast",
        "primary_cuisine": "Levantine",
        "complexity": "Basic",
        "time_class": "15–30 min",
        "servings": "2",
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "verification_state": "Verified",
        "ingredient_families": json.dumps(["Eggs & Dairy", "Vegetables"]),
        "ingredient_text": "olive oil onion red bell pepper garlic tomatoes eggs cumin paprika chili flakes flat-leaf parsley",
        "ingredients": [
            {"position": 1, "quantity": "2 tbsp", "item": "olive oil"},
            {"position": 2, "quantity": "1", "item": "onion", "preparation": "finely diced"},
            {"position": 3, "quantity": "1", "item": "red bell pepper", "preparation": "diced"},
            {"position": 4, "quantity": "3 cloves", "item": "garlic", "preparation": "minced"},
            {"position": 5, "quantity": "400 g", "item": "canned whole tomatoes"},
            {"position": 6, "quantity": "1 tsp", "item": "ground cumin"},
            {"position": 7, "quantity": "1 tsp", "item": "sweet paprika"},
            {"position": 8, "quantity": "¼ tsp", "item": "chili flakes", "optional": 1},
            {"position": 9, "quantity": "4", "item": "eggs"},
            {"position": 10, "item": "flat-leaf parsley", "preparation": "roughly chopped", "optional": 1},
        ],
        "steps": [
            {"position": 1, "instruction": "Heat olive oil in a wide skillet over medium heat. Add onion and bell pepper and cook until softened, about 8 minutes."},
            {"position": 2, "instruction": "Add garlic, cumin, paprika, and chili flakes. Stir for 1 minute until fragrant."},
            {"position": 3, "instruction": "Add canned tomatoes, crushing them with a spoon. Simmer 10 minutes until sauce thickens. Season with salt."},
            {"position": 4, "instruction": "Make 4 wells in the sauce. Crack an egg into each well. Cover and cook until whites are just set, 4–6 minutes."},
            {"position": 5, "instruction": "Scatter parsley over the top and serve directly from the pan with crusty bread."},
        ],
        "notes": [
            {"note_type": "recipe", "content": "Keep the yolks runny — pull the pan off heat while they still wobble."},
        ],
    },
    {
        "slug": "braised-short-ribs",
        "title": "Braised Short Ribs",
        "short_description": "Bone-in beef short ribs slow-braised in red wine and aromatics until fork-tender.",
        "dish_role": "Main",
        "primary_cuisine": "European",
        "technique_family": "Braise",
        "complexity": "Advanced",
        "time_class": "3+ hours",
        "servings": "4",
        "prep_time_minutes": 30,
        "cook_time_minutes": 210,
        "verification_state": "Verified",
        "ingredient_families": json.dumps(["Beef & Veal", "Alliums", "Root Vegetables"]),
        "ingredient_text": "beef short ribs flour olive oil onion carrot celery garlic tomato paste red wine beef stock thyme bay leaves",
        "ingredients": [
            {"position": 1, "quantity": "1.5 kg", "item": "bone-in beef short ribs"},
            {"position": 2, "quantity": "2 tbsp", "item": "plain flour"},
            {"position": 3, "quantity": "2 tbsp", "item": "olive oil"},
            {"position": 4, "quantity": "1", "item": "large onion", "preparation": "diced"},
            {"position": 5, "quantity": "2", "item": "carrots", "preparation": "diced"},
            {"position": 6, "quantity": "2 stalks", "item": "celery", "preparation": "diced"},
            {"position": 7, "quantity": "4 cloves", "item": "garlic", "preparation": "smashed"},
            {"position": 8, "quantity": "2 tbsp", "item": "tomato paste"},
            {"position": 9, "quantity": "375 ml", "item": "dry red wine"},
            {"position": 10, "quantity": "500 ml", "item": "beef stock"},
            {"position": 11, "quantity": "4 sprigs", "item": "fresh thyme"},
            {"position": 12, "quantity": "2", "item": "bay leaves"},
        ],
        "steps": [
            {"position": 1, "instruction": "Preheat oven to 160 °C / 325 °F. Season ribs generously with salt and pepper, then dust lightly with flour."},
            {"position": 2, "instruction": "Heat oil in a large Dutch oven over high heat. Sear ribs in batches until deeply browned on all sides, 3–4 minutes per side. Remove and set aside.", "time_note": "12–15 min"},
            {"position": 3, "instruction": "Reduce heat to medium. Add onion, carrot, and celery to the pot. Cook until softened and beginning to colour, about 8 minutes."},
            {"position": 4, "instruction": "Add garlic and tomato paste. Stir for 2 minutes. Pour in wine and scrape up all the browned bits from the bottom."},
            {"position": 5, "instruction": "Add stock, thyme, and bay leaves. Return ribs to the pot — liquid should come halfway up the meat. Bring to a simmer."},
            {"position": 6, "instruction": "Cover tightly and braise in the oven until the meat is completely tender and falling off the bone, 3–3½ hours.", "time_note": "3–3.5 hours"},
            {"position": 7, "instruction": "Skim fat from the braising liquid. If desired, simmer the strained liquid over high heat to reduce into a glossy sauce."},
        ],
        "notes": [
            {"note_type": "storage", "content": "Even better the next day — refrigerate overnight and lift off solidified fat before reheating."},
            {"note_type": "service", "content": "Serve over polenta, mashed potato, or wide egg noodles."},
        ],
    },
    {
        "slug": "roast-chicken",
        "title": "Roast Chicken",
        "short_description": "A reliable whole roast chicken with crisp skin and juicy meat. Sunday standard.",
        "dish_role": "Main",
        "primary_cuisine": "European",
        "technique_family": "Roast",
        "complexity": "Everyday",
        "time_class": "1–2 hours",
        "servings": "4",
        "prep_time_minutes": 15,
        "cook_time_minutes": 80,
        "verification_state": "Verified",
        "ingredient_families": json.dumps(["Poultry", "Alliums", "Aromatics"]),
        "ingredient_text": "whole chicken butter lemon thyme garlic olive oil",
        "ingredients": [
            {"position": 1, "quantity": "1.6 kg", "item": "whole chicken", "preparation": "at room temperature"},
            {"position": 2, "quantity": "40 g", "item": "unsalted butter", "preparation": "softened"},
            {"position": 3, "quantity": "1", "item": "lemon", "preparation": "halved"},
            {"position": 4, "quantity": "6 sprigs", "item": "fresh thyme"},
            {"position": 5, "quantity": "1 head", "item": "garlic", "preparation": "halved crosswise"},
            {"position": 6, "quantity": "1 tbsp", "item": "olive oil"},
        ],
        "steps": [
            {"position": 1, "instruction": "Preheat oven to 220 °C / 430 °F. Pat the chicken dry inside and out with paper towels."},
            {"position": 2, "instruction": "Rub butter all over the outside skin. Season generously with salt and pepper, including inside the cavity."},
            {"position": 3, "instruction": "Stuff the cavity with the lemon halves, thyme, and garlic. Truss the legs loosely with kitchen twine."},
            {"position": 4, "instruction": "Place breast-side up in a roasting tray. Drizzle with olive oil. Roast at 220 °C for 15 minutes to crisp the skin.", "time_note": "15 min"},
            {"position": 5, "instruction": "Reduce oven to 180 °C / 350 °F and continue roasting until juices run clear when thigh is pierced, about 60–65 more minutes.", "time_note": "60–65 min"},
            {"position": 6, "instruction": "Rest the chicken uncovered for 10 minutes before carving. The internal temperature should read 74 °C / 165 °F at the thigh.", "time_note": "10 min rest"},
        ],
        "notes": [
            {"note_type": "recipe", "content": "Drying the skin thoroughly is the single most important step for crispness."},
        ],
    },
    {
        "slug": "green-salad-vinaigrette",
        "title": "Green Salad with Vinaigrette",
        "short_description": "A simple dressed green salad. Foundational technique for daily use.",
        "dish_role": "Side",
        "primary_cuisine": "French",
        "complexity": "Basic",
        "time_class": "Under 15 min",
        "servings": "2",
        "prep_time_minutes": 10,
        "cook_time_minutes": 0,
        "verification_state": "Draft",
        "dietary_flags": json.dumps(["Vegetarian", "Vegan", "Gluten-Free"]),
        "ingredient_families": json.dumps(["Leafy Greens"]),
        "ingredient_text": "mixed salad leaves shallot dijon mustard white wine vinegar olive oil",
        "ingredients": [
            {"position": 1, "quantity": "100 g", "item": "mixed salad leaves"},
            {"position": 2, "quantity": "1 small", "item": "shallot", "preparation": "very finely minced"},
            {"position": 3, "quantity": "1 tsp", "item": "Dijon mustard"},
            {"position": 4, "quantity": "1 tbsp", "item": "white wine vinegar"},
            {"position": 5, "quantity": "3 tbsp", "item": "extra virgin olive oil"},
        ],
        "steps": [
            {"position": 1, "instruction": "Whisk together shallot, mustard, and vinegar with a pinch of salt. Slowly drizzle in olive oil while whisking to emulsify."},
            {"position": 2, "instruction": "Taste and adjust seasoning. The dressing should be balanced — not too sharp, not flat."},
            {"position": 3, "instruction": "Dress the salad leaves just before serving. Toss gently to coat without bruising."},
        ],
        "notes": [],
    },
]


def seed(db) -> None:
    created = 0
    skipped = 0
    for fixture in FIXTURES:
        existing = db.query(Recipe).filter_by(slug=fixture["slug"]).first()
        if existing:
            print(f"  skip  {fixture['slug']} (already exists)")
            skipped += 1
            continue

        recipe_id = new_ulid()
        recipe = Recipe(
            id=recipe_id,
            slug=fixture["slug"],
            title=fixture["title"],
            short_description=fixture.get("short_description"),
            dish_role=fixture.get("dish_role"),
            primary_cuisine=fixture.get("primary_cuisine"),
            technique_family=fixture.get("technique_family"),
            complexity=fixture.get("complexity"),
            time_class=fixture.get("time_class"),
            service_format=fixture.get("service_format"),
            servings=fixture.get("servings"),
            prep_time_minutes=fixture.get("prep_time_minutes"),
            cook_time_minutes=fixture.get("cook_time_minutes"),
            verification_state=fixture.get("verification_state", "Draft"),
            ingredient_families=fixture.get("ingredient_families", "[]"),
            dietary_flags=fixture.get("dietary_flags", "[]"),
            mood_tags=fixture.get("mood_tags", "[]"),
            ingredient_text=fixture.get("ingredient_text"),
        )
        db.add(recipe)

        for ing in fixture.get("ingredients", []):
            db.add(RecipeIngredient(
                id=new_ulid(),
                recipe_id=recipe_id,
                position=ing["position"],
                item=ing["item"],
                quantity=ing.get("quantity"),
                unit=ing.get("unit"),
                preparation=ing.get("preparation"),
                optional=ing.get("optional", 0),
            ))

        for step in fixture.get("steps", []):
            db.add(RecipeStep(
                id=new_ulid(),
                recipe_id=recipe_id,
                position=step["position"],
                instruction=step["instruction"],
                time_note=step.get("time_note"),
                equipment_note=step.get("equipment_note"),
            ))

        for note in fixture.get("notes", []):
            db.add(RecipeNote(
                id=new_ulid(),
                recipe_id=recipe_id,
                note_type=note["note_type"],
                content=note["content"],
            ))

        db.flush()

        # Reload with relationships for FTS sync
        db.refresh(recipe)
        _sync_fts(db, recipe)

        print(f"  added {fixture['slug']}")
        created += 1

    db.commit()
    print(f"\nSeed complete: {created} added, {skipped} skipped.")


if __name__ == "__main__":
    print("Initialising database...")
    init_db()
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
