"""
Canonical taxonomy vocabulary constants — Python mirror of @galley/shared-taxonomy.

Source of truth: docs/04_taxonomy/content-taxonomy-spec.md
TypeScript source: packages/shared-taxonomy/src/index.ts

When adding new values, update both files together.
"""

DISH_ROLES: frozenset[str] = frozenset({
    "Breakfast", "Brunch", "Snack", "Starter", "Soup", "Salad", "Side", "Main",
    "Shared Plate", "Dessert", "Bread", "Dough", "Sauce", "Condiment", "Drink",
    "Preserve", "Pantry Staple", "Component", "Confectionery", "Street Food",
})

PRIMARY_CUISINES: frozenset[str] = frozenset({
    # Europe
    "Italian", "French", "Spanish", "Catalan", "Portuguese", "Greek", "Turkish",
    "British", "Irish", "Scottish", "Nordic", "Swedish", "Norwegian", "Danish",
    "Finnish", "German", "Austrian", "Swiss", "Dutch", "Belgian",
    "Eastern European", "Polish", "Hungarian", "Czech", "Romanian", "Russian",
    "Georgian", "Armenian", "Ukrainian",
    # Middle East & North Africa
    "Levantine", "Lebanese", "Syrian", "Palestinian", "Israeli", "Egyptian",
    "Moroccan", "Tunisian", "Algerian", "Libyan", "Persian", "Iraqi", "Yemeni",
    # Sub-Saharan Africa
    "Ethiopian", "Eritrean", "West African", "Nigerian", "Ghanaian",
    "Senegalese", "East African", "Kenyan", "South African", "Zimbabwean",
    # South Asia
    "Indian", "North Indian", "South Indian", "Pakistani", "Bangladeshi",
    "Sri Lankan", "Nepali",
    # Southeast Asia
    "Thai", "Vietnamese", "Cambodian", "Laotian", "Filipino", "Indonesian",
    "Malaysian", "Singaporean", "Burmese",
    # East Asia
    "Chinese", "Cantonese", "Sichuan", "Shanghainese", "Taiwanese",
    "Japanese", "Korean", "Mongolian",
    # Central Asia & Caucasus
    "Uzbek", "Kazakh", "Azerbaijani", "Caucasian",
    # Americas
    "Mexican", "Tex-Mex", "Oaxacan", "Central American", "Guatemalan",
    "Peruvian", "Colombian", "Venezuelan", "Brazilian", "Argentinian",
    "Chilean", "American", "American Southern", "American Midwest",
    "Cajun / Creole", "Caribbean", "Jamaican", "Cuban",
    # Cross-cultural
    "Fusion", "Global / Mixed",
})

TECHNIQUE_FAMILIES: frozenset[str] = frozenset({
    "Raw", "Assemble", "Marinate", "Cure", "Ferment", "Pickle", "Smoke",
    "Confit", "Poach", "Steam", "Boil", "Simmer", "Braise", "Stew",
    "Slow Cook", "Pressure Cook", "Sear", "Fry", "Stir-Fry", "Deep Fry",
    "Roast", "Bake", "Grill", "Emulsify", "Blend", "Dehydrate", "Multi-Stage",
})

INGREDIENT_FAMILIES: frozenset[str] = frozenset({
    # Proteins
    "Beef", "Pork", "Lamb", "Veal", "Poultry", "Game", "Offal", "Egg",
    "Seafood", "Shellfish", "Freshwater Fish",
    # Dairy & Plant Proteins
    "Dairy", "Cheese", "Tofu", "Tempeh", "Legume", "Bean", "Lentil", "Chickpea",
    # Starches & Grains
    "Rice", "Pasta", "Noodles", "Bread", "Flour / Dough", "Potato", "Grain",
    "Corn / Maize",
    # Vegetables & Fungi
    "Vegetable", "Leafy Green", "Allium", "Root Vegetable", "Brassica",
    "Mushroom", "Tomato", "Chili", "Aubergine / Eggplant", "Squash",
    # Fruit, Nuts & Flavourings
    "Fruit", "Citrus", "Stone Fruit", "Tropical Fruit", "Dried Fruit",
    "Nut / Seed", "Chocolate", "Coconut", "Herb-forward", "Spice-forward",
    "Fermented / Preserved",
})

COMPLEXITY_OPTIONS: frozenset[str] = frozenset({
    "Basic", "Intermediate", "Advanced", "Project",
})

TIME_CLASS_OPTIONS: frozenset[str] = frozenset({
    "Under 15 min", "15–30 min", "30–60 min",
    "1–2 hr", "2–4 hr", "Half Day+", "Multi-Day",
})

SERVICE_FORMATS: frozenset[str] = frozenset({
    "Single Plate", "Family Style", "Buffet / Shared", "Meal Prep",
    "Party Food", "Lunchbox", "Sauce / Add-On", "Side Component",
    "Base Recipe", "Kitchen Use",
})

SEASONS: frozenset[str] = frozenset({
    "Spring", "Summer", "Autumn", "Winter", "All Year",
})

MOOD_TAGS: frozenset[str] = frozenset({
    "Light", "Fresh", "Comfort", "Rich", "Smoky", "Spicy", "Sharp / Acidic",
    "Umami-forward", "Bitter", "Sweet", "Festive", "Rustic", "Elegant",
    "Everyday", "Restorative", "Indulgent", "Cold Weather", "Hot Weather",
})

STORAGE_PROFILES: frozenset[str] = frozenset({
    "Best Fresh", "Keeps 2–3 Days", "Keeps Up to a Week", "Freezer Friendly",
    "Reheats Well", "Improves Over Time", "Batch Cook Friendly",
    "Picnic / Transport Friendly", "Long Shelf Life",
})

DIETARY_FLAGS: frozenset[str] = frozenset({
    "Vegetarian", "Vegan", "Pescatarian", "Gluten-Free", "Dairy-Free",
    "Egg-Free", "Nut-Free", "Soy-Free", "Low-Carb", "High-Protein",
    "Alcohol-Free", "Halal-Friendly", "Kosher-Style", "Low-Sodium",
    "No Added Sugar",
})

PROVISION_TAGS: frozenset[str] = frozenset({
    "Weeknight", "Weekend", "Pantry-Heavy", "Freezer-Build", "Dinner Party",
    "Leftover-Friendly", "One-Pot", "One-Pan", "No Oven", "No Stovetop",
    "Kitchen-Equipment-Intensive", "Minimal Equipment", "Budget-Friendly",
    "Crowd-Scaled", "Kid-Friendly", "Pantry Clear-Out",
})

SECTORS: frozenset[str] = frozenset({
    "Fire Line", "Cold Line", "Bakehouse", "Provisions", "House Stock",
    "Service", "Galley",
})

OPERATIONAL_CLASSES: frozenset[str] = frozenset({
    "House Standard", "Field Meal", "Long Simmer", "Quick Assembly",
    "Weekend Project", "Base Component", "Service Sauce", "Preservation Run",
    "Festive Operation", "Experimental",
})

HEAT_WINDOWS: frozenset[str] = frozenset({
    "No Heat", "Cold Prep", "Low Heat", "Medium Heat", "High Heat",
    "Oven", "Grill / Open Fire", "Multi-Stage",
})
