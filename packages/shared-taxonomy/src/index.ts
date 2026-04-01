/**
 * @galley/shared-taxonomy
 *
 * Canonical taxonomy vocabulary for the Sevastolink Galley Archive.
 * All values derive from docs/04_taxonomy/content-taxonomy-spec.md.
 *
 * Two tiers of export:
 *   Complete arrays  — every valid value for a field (use for validation)
 *   Filter arrays    — curated subset suitable for UI filter panels and forms
 */

// ── §2.1 Dish Role ─────────────────────────────────────────────────────────────

export const DISH_ROLES = [
  "Breakfast", "Brunch", "Snack", "Starter", "Soup", "Salad", "Side", "Main",
  "Shared Plate", "Dessert", "Bread", "Dough", "Sauce", "Condiment", "Drink",
  "Preserve", "Pantry Staple", "Component", "Confectionery", "Street Food",
] as const;

export type DishRole = typeof DISH_ROLES[number];

/** Common dish roles for filter panels and intake forms. */
export const DISH_ROLE_FILTER_OPTIONS: DishRole[] = [
  "Breakfast", "Brunch", "Snack", "Starter", "Soup", "Salad",
  "Side", "Main", "Shared Plate", "Dessert", "Bread",
  "Sauce", "Condiment", "Pantry Staple", "Drink",
];

// ── §2.2 Primary Cuisine ───────────────────────────────────────────────────────

export const PRIMARY_CUISINES = [
  // Europe
  "Italian", "French", "Spanish", "Catalan", "Portuguese", "Greek", "Turkish",
  "British", "Irish", "Scottish", "Nordic", "Swedish", "Norwegian", "Danish",
  "Finnish", "German", "Austrian", "Swiss", "Dutch", "Belgian",
  "Eastern European", "Polish", "Hungarian", "Czech", "Romanian", "Russian",
  "Georgian", "Armenian", "Ukrainian",
  // Middle East & North Africa
  "Levantine", "Lebanese", "Syrian", "Palestinian", "Israeli", "Egyptian",
  "Moroccan", "Tunisian", "Algerian", "Libyan", "Persian", "Iraqi", "Yemeni",
  // Sub-Saharan Africa
  "Ethiopian", "Eritrean", "West African", "Nigerian", "Ghanaian",
  "Senegalese", "East African", "Kenyan", "South African", "Zimbabwean",
  // South Asia
  "Indian", "North Indian", "South Indian", "Pakistani", "Bangladeshi",
  "Sri Lankan", "Nepali",
  // Southeast Asia
  "Thai", "Vietnamese", "Cambodian", "Laotian", "Filipino", "Indonesian",
  "Malaysian", "Singaporean", "Burmese",
  // East Asia
  "Chinese", "Cantonese", "Sichuan", "Shanghainese", "Taiwanese",
  "Japanese", "Korean", "Mongolian",
  // Central Asia & Caucasus
  "Uzbek", "Kazakh", "Azerbaijani", "Caucasian",
  // Americas
  "Mexican", "Tex-Mex", "Oaxacan", "Central American", "Guatemalan",
  "Peruvian", "Colombian", "Venezuelan", "Brazilian", "Argentinian",
  "Chilean", "American", "American Southern", "American Midwest",
  "Cajun / Creole", "Caribbean", "Jamaican", "Cuban",
  // Cross-cultural
  "Fusion", "Global / Mixed",
] as const;

export type PrimaryCuisine = typeof PRIMARY_CUISINES[number];

/** Common cuisines for filter panels and intake forms. */
export const CUISINE_FILTER_OPTIONS: PrimaryCuisine[] = [
  "British", "French", "Italian", "Spanish", "Portuguese", "Greek", "Turkish",
  "German", "Russian", "Eastern European",
  "Levantine", "Moroccan", "Egyptian", "Persian",
  "Ethiopian", "West African",
  "Indian", "Pakistani", "Sri Lankan",
  "Thai", "Vietnamese", "Indonesian", "Filipino",
  "Chinese", "Japanese", "Korean",
  "Mexican", "Peruvian", "Brazilian", "American", "Cajun / Creole", "Caribbean",
  "Fusion", "Global / Mixed",
];

// ── §2.4 Technique Family ──────────────────────────────────────────────────────

export const TECHNIQUE_FAMILIES = [
  "Raw", "Assemble", "Marinate", "Cure", "Ferment", "Pickle", "Smoke",
  "Confit", "Poach", "Steam", "Boil", "Simmer", "Braise", "Stew",
  "Slow Cook", "Pressure Cook", "Sear", "Fry", "Stir-Fry", "Deep Fry",
  "Roast", "Bake", "Grill", "Emulsify", "Blend", "Dehydrate", "Multi-Stage",
] as const;

export type TechniqueFamily = typeof TECHNIQUE_FAMILIES[number];

/** Common techniques for filter panels and intake forms. */
export const TECHNIQUE_FILTER_OPTIONS: TechniqueFamily[] = [
  "Raw", "Assemble", "Roast", "Braise", "Stew", "Simmer", "Fry", "Stir-Fry",
  "Deep Fry", "Grill", "Bake", "Steam", "Ferment", "Cure", "Pickle", "Smoke",
];

// ── §2.5 Ingredient Families ───────────────────────────────────────────────────

export const INGREDIENT_FAMILIES = [
  // Proteins
  "Beef", "Pork", "Lamb", "Veal", "Poultry", "Game", "Offal", "Egg",
  "Seafood", "Shellfish", "Freshwater Fish",
  // Dairy & Plant Proteins
  "Dairy", "Cheese", "Tofu", "Tempeh", "Legume", "Bean", "Lentil", "Chickpea",
  // Starches & Grains
  "Rice", "Pasta", "Noodles", "Bread", "Flour / Dough", "Potato", "Grain",
  "Corn / Maize",
  // Vegetables & Fungi
  "Vegetable", "Leafy Green", "Allium", "Root Vegetable", "Brassica",
  "Mushroom", "Tomato", "Chili", "Aubergine / Eggplant", "Squash",
  // Fruit, Nuts & Flavourings
  "Fruit", "Citrus", "Stone Fruit", "Tropical Fruit", "Dried Fruit",
  "Nut / Seed", "Chocolate", "Coconut", "Herb-forward", "Spice-forward",
  "Fermented / Preserved",
] as const;

export type IngredientFamily = typeof INGREDIENT_FAMILIES[number];

/** Top-level ingredient families for filter panels — covers the most common browsing dimensions. */
export const INGREDIENT_FAMILY_FILTER_OPTIONS: IngredientFamily[] = [
  // Proteins
  "Beef", "Pork", "Lamb", "Poultry", "Seafood", "Shellfish", "Egg",
  // Dairy & Plant Proteins
  "Dairy", "Cheese", "Legume",
  // Starches & Grains
  "Rice", "Pasta", "Noodles", "Bread", "Potato", "Grain",
  // Vegetables & Fungi
  "Vegetable", "Leafy Green", "Mushroom", "Tomato", "Chili",
  // Fruit & Flavourings
  "Fruit", "Citrus", "Chocolate", "Herb-forward", "Spice-forward",
];

// ── §3.1 Complexity ────────────────────────────────────────────────────────────

export const COMPLEXITY_OPTIONS = [
  "Basic", "Intermediate", "Advanced", "Project",
] as const;

export type Complexity = typeof COMPLEXITY_OPTIONS[number];

// ── §3.2 Time Class ────────────────────────────────────────────────────────────

export const TIME_CLASS_OPTIONS = [
  "Under 15 min", "15–30 min", "30–60 min",
  "1–2 hr", "2–4 hr", "Half Day+", "Multi-Day",
] as const;

export type TimeClass = typeof TIME_CLASS_OPTIONS[number];

// ── §3.3 Service Format ────────────────────────────────────────────────────────

export const SERVICE_FORMATS = [
  "Single Plate", "Family Style", "Buffet / Shared", "Meal Prep",
  "Party Food", "Lunchbox", "Sauce / Add-On", "Side Component",
  "Base Recipe", "Kitchen Use",
] as const;

export type ServiceFormat = typeof SERVICE_FORMATS[number];

// ── §3.4 Season ────────────────────────────────────────────────────────────────

export const SEASONS = [
  "Spring", "Summer", "Autumn", "Winter", "All Year",
] as const;

export type Season = typeof SEASONS[number];

// ── §3.5 Mood Tags ─────────────────────────────────────────────────────────────

export const MOOD_TAGS = [
  "Light", "Fresh", "Comfort", "Rich", "Smoky", "Spicy", "Sharp / Acidic",
  "Umami-forward", "Bitter", "Sweet", "Festive", "Rustic", "Elegant",
  "Everyday", "Restorative", "Indulgent", "Cold Weather", "Hot Weather",
] as const;

export type MoodTag = typeof MOOD_TAGS[number];

// ── §3.6 Storage Profile ───────────────────────────────────────────────────────

export const STORAGE_PROFILES = [
  "Best Fresh", "Keeps 2–3 Days", "Keeps Up to a Week", "Freezer Friendly",
  "Reheats Well", "Improves Over Time", "Batch Cook Friendly",
  "Picnic / Transport Friendly", "Long Shelf Life",
] as const;

export type StorageProfile = typeof STORAGE_PROFILES[number];

// ── §4.1 Dietary Flags ─────────────────────────────────────────────────────────

export const DIETARY_FLAGS = [
  "Vegetarian", "Vegan", "Pescatarian", "Gluten-Free", "Dairy-Free",
  "Egg-Free", "Nut-Free", "Soy-Free", "Low-Carb", "High-Protein",
  "Alcohol-Free", "Halal-Friendly", "Kosher-Style", "Low-Sodium",
  "No Added Sugar",
] as const;

export type DietaryFlag = typeof DIETARY_FLAGS[number];

// ── §4.2 Provision Tags ────────────────────────────────────────────────────────

export const PROVISION_TAGS = [
  "Weeknight", "Weekend", "Pantry-Heavy", "Freezer-Build", "Dinner Party",
  "Leftover-Friendly", "One-Pot", "One-Pan", "No Oven", "No Stovetop",
  "Kitchen-Equipment-Intensive", "Minimal Equipment", "Budget-Friendly",
  "Crowd-Scaled", "Kid-Friendly", "Pantry Clear-Out",
] as const;

export type ProvisionTag = typeof PROVISION_TAGS[number];

// ── §5.1 Sector ────────────────────────────────────────────────────────────────

export const SECTORS = [
  "Fire Line", "Cold Line", "Bakehouse", "Provisions", "House Stock",
  "Service", "Galley",
] as const;

export type Sector = typeof SECTORS[number];

// ── §5.2 Operational Class ─────────────────────────────────────────────────────

export const OPERATIONAL_CLASSES = [
  "House Standard", "Field Meal", "Long Simmer", "Quick Assembly",
  "Weekend Project", "Base Component", "Service Sauce", "Preservation Run",
  "Festive Operation", "Experimental",
] as const;

export type OperationalClass = typeof OPERATIONAL_CLASSES[number];

// ── §5.3 Heat Window ───────────────────────────────────────────────────────────

export const HEAT_WINDOWS = [
  "No Heat", "Cold Prep", "Low Heat", "Medium Heat", "High Heat",
  "Oven", "Grill / Open Fire", "Multi-Stage",
] as const;

export type HeatWindow = typeof HEAT_WINDOWS[number];
