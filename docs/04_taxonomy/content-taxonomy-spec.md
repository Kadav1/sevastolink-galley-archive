# Sevastolink Galley Archive

## Content & Taxonomy Spec v2.0

---

## 1. Taxonomy Philosophy

### 1.1 The problem with cookbook taxonomy

A simple "starter / main / dessert" model fails as soon as it meets the real world. It cannot represent:

* a Korean banchan that serves as both a side and a condiment
* a Turkish meze that is a starter, a shared plate, and a snack depending on context
* a French bouillon that is a stock, a broth, a poaching liquid, and a soup base
* a Mexican mole that took three days to build but serves as a sauce
* a Japanese onigiri that is a snack, a lunchbox item, and a staple food simultaneously
* a fermented hot sauce that belongs in provisions, condiments, and preservation

A single-shelf taxonomy cannot hold these. It collapses nuance into inaccurate categories, makes retrieval unreliable, and forces every cuisine into a Western European meal structure.

### 1.2 The multi-layer approach

Every recipe in Sevastolink Galley Archive is classified through **eleven independent layers**. Each layer answers a different question about the dish. No single layer dominates.

| Layer | Question answered |
|---|---|
| Dish Role | What function does this play in a meal? |
| Primary Cuisine | What culinary tradition does this come from? |
| Secondary Cuisines | What other traditions influence this dish? |
| Technique Family | What is the dominant cooking method? |
| Ingredient Families | What are the primary ingredient groups? |
| Complexity | How demanding is this to execute? |
| Time Class | How long does this take from start to finish? |
| Service Format | How is this served and used? |
| Season / Mood | When does this belong, and what does it feel like? |
| Storage Profile | How does this behave after cooking? |
| Dietary / Practical Filters | What practical constraints does this satisfy? |

Plus a Sevastolink overlay layer that adds operational identity without replacing culinary clarity.

### 1.3 Design principles

**Broad enough for any cuisine.** The taxonomy must not impose European meal structure on non-European dishes. Classification should work equally well for Ethiopian injera, Japanese dashi, Peruvian ceviche, and Welsh rarebit.

**Retrieval-first.** Every field must justify itself by improving search, filtering, or browsing. Decorative taxonomy is excluded.

**Structured where consistency matters.** Fields used for filtering are controlled vocabularies. Fields where judgment matters are free text.

**Tolerant of partial classification.** A recipe may enter the archive with minimal taxonomy and be enriched later. The system must not require a complete classification at intake.

**AI-friendly.** The field structure and vocabulary must be learnable by a local language model for normalization suggestions. Vague or overlapping terms are avoided.

**Human-fillable.** The user must be able to classify a recipe without consulting documentation. Field names and options must be self-explanatory.

### 1.4 What taxonomy is not for

* Replacing good recipe writing with metadata
* Creating a culinary ontology for academic purposes
* Generating content or recommendations algorithmically
* Tracking what the user has eaten or plans to eat

---

## 2. Primary Structured Fields

### 2.1 Dish Role

**What it answers:** What functional role does this recipe play in a meal or in the kitchen?

**Type:** Single-select. Required.

**Design note:** This is about role, not position in a Western European meal. A dish can play multiple roles across contexts, but must be assigned one primary role for retrieval purposes. Choose the most common or intended use.

| Value | Description |
|---|---|
| `Breakfast` | Morning meal, eaten before other meals |
| `Brunch` | Late morning, mixed character |
| `Snack` | Small, standalone, eaten between meals |
| `Starter` | Beginning of a structured meal, small portion |
| `Soup` | Primarily liquid, bowl-served |
| `Salad` | Cold or room-temperature assembly, usually vegetable-forward |
| `Side` | Served alongside a main, not standalone |
| `Main` | Primary dish of a meal |
| `Shared Plate` | Designed for communal eating at the table |
| `Dessert` | Sweet, served at the end or as a treat |
| `Bread` | Leavened or flatbread, dough-based |
| `Dough` | Pastry, pasta, or bread base not yet baked or cooked |
| `Sauce` | Liquid or semi-liquid, served over or alongside |
| `Condiment` | Accompaniment applied in small amounts |
| `Drink` | Beverage, hot or cold, alcoholic or not |
| `Preserve` | Long-life product: jam, pickle, ferment, chutney |
| `Pantry Staple` | Stock, broth, spice blend, base ingredient |
| `Component` | A building block used in other recipes |
| `Confectionery` | Candy, sweet, or small sugar-based item |
| `Street Food` | Single-portion, informal, eaten without utensils or table |

---

### 2.2 Primary Cuisine

**What it answers:** What is the primary culinary tradition this recipe belongs to?

**Type:** Single-select. Required.

**Design note:** Assign the tradition the recipe originates from or is most closely identified with. For genuinely invented or merged dishes, use `Fusion` or `Global / Mixed`. Do not use `Global / Mixed` to avoid making a decision.

#### Europe

| Value |
|---|
| `Italian` |
| `French` |
| `Spanish` |
| `Catalan` |
| `Portuguese` |
| `Greek` |
| `Turkish` |
| `British` |
| `Irish` |
| `Scottish` |
| `Nordic` |
| `Swedish` |
| `Norwegian` |
| `Danish` |
| `Finnish` |
| `German` |
| `Austrian` |
| `Swiss` |
| `Dutch` |
| `Belgian` |
| `Eastern European` |
| `Polish` |
| `Hungarian` |
| `Czech` |
| `Romanian` |
| `Russian` |
| `Georgian` |
| `Armenian` |
| `Ukrainian` |

#### Middle East & North Africa

| Value |
|---|
| `Levantine` |
| `Lebanese` |
| `Syrian` |
| `Palestinian` |
| `Israeli` |
| `Egyptian` |
| `Moroccan` |
| `Tunisian` |
| `Algerian` |
| `Libyan` |
| `Persian` |
| `Iraqi` |
| `Yemeni` |

#### Sub-Saharan Africa

| Value |
|---|
| `Ethiopian` |
| `Eritrean` |
| `West African` |
| `Nigerian` |
| `Ghanaian` |
| `Senegalese` |
| `East African` |
| `Kenyan` |
| `South African` |
| `Zimbabwean` |

#### South Asia

| Value |
|---|
| `Indian` |
| `North Indian` |
| `South Indian` |
| `Pakistani` |
| `Bangladeshi` |
| `Sri Lankan` |
| `Nepali` |

#### Southeast Asia

| Value |
|---|
| `Thai` |
| `Vietnamese` |
| `Cambodian` |
| `Laotian` |
| `Filipino` |
| `Indonesian` |
| `Malaysian` |
| `Singaporean` |
| `Burmese` |

#### East Asia

| Value |
|---|
| `Chinese` |
| `Cantonese` |
| `Sichuan` |
| `Shanghainese` |
| `Taiwanese` |
| `Japanese` |
| `Korean` |
| `Mongolian` |

#### Central Asia & Caucasus

| Value |
|---|
| `Uzbek` |
| `Kazakh` |
| `Azerbaijani` |
| `Caucasian` |

#### Americas

| Value |
|---|
| `Mexican` |
| `Tex-Mex` |
| `Oaxacan` |
| `Central American` |
| `Guatemalan` |
| `Peruvian` |
| `Colombian` |
| `Venezuelan` |
| `Brazilian` |
| `Argentinian` |
| `Chilean` |
| `American` |
| `American Southern` |
| `American Midwest` |
| `Cajun / Creole` |
| `Caribbean` |
| `Jamaican` |
| `Cuban` |

#### Cross-cultural

| Value |
|---|
| `Fusion` |
| `Global / Mixed` |

---

### 2.3 Secondary Cuisines

**What it answers:** What other culinary traditions noticeably influence this dish?

**Type:** Multi-select. Optional.

**Values:** Same vocabulary as Primary Cuisine.

**Design note:** Use only when influence is genuine and meaningful to the recipe's character. Do not use to add curiosity tags. A dish that uses cumin is not Indian. A Japanese-Peruvian ceviche (Nikkei cuisine) genuinely warrants both.

---

### 2.4 Technique Family

**What it answers:** What is the dominant cooking technique?

**Type:** Single-select. Required.

**Design note:** Choose the technique that defines the dish's character or requires the most skill or attention. A braise that is finished on the grill is still a braise.

| Value | Description |
|---|---|
| `Raw` | No heat applied. Ceviche, tartare, salads |
| `Assemble` | No or minimal cooking. Components combined |
| `Marinate` | Flavor transformation through soaking, no or minimal heat |
| `Cure` | Preservation through salt, acid, or sugar. No heat |
| `Ferment` | Microbial transformation. Long process |
| `Pickle` | Acid or brine preservation |
| `Smoke` | Low heat, smoke-driven flavor |
| `Confit` | Low heat, submerged in fat |
| `Poach` | Gentle heat, liquid |
| `Steam` | Heat via steam, no direct contact with liquid |
| `Boil` | High-heat liquid cooking |
| `Simmer` | Low-moderate heat, sustained liquid cooking |
| `Braise` | Wet heat, long time, low temperature. Meat or vegetables in liquid |
| `Stew` | Similar to braise but more liquid, shorter or equal time |
| `Slow Cook` | Low heat, very long time |
| `Pressure Cook` | Sealed high-pressure cooking |
| `Sear` | High heat, short time, crust development |
| `Fry` | Pan-frying in moderate oil |
| `Stir-Fry` | High heat, small cuts, fast movement |
| `Deep Fry` | Fully submerged in oil |
| `Roast` | Dry heat, oven or open fire, uncovered |
| `Bake` | Dry heat, oven, usually dough or batter |
| `Grill` | Direct dry heat from below or above |
| `Emulsify` | Fat and liquid combined into stable suspension |
| `Blend` | Mechanical reduction to liquid or paste |
| `Dehydrate` | Moisture removal, low heat or air |
| `Multi-Stage` | Two or more distinct techniques of equal importance |

---

### 2.5 Ingredient Families

**What it answers:** What are the major ingredient groups present in this recipe?

**Type:** Multi-select. Required. Recommended 2–5 values.

**Design note:** Tag the ingredients that define the dish, not every ingredient present. A chicken stock with carrots and celery is `Poultry` and `Vegetable`, not `Poultry, Vegetable, Herb-forward, Citrus, Allium`.

#### Proteins

| Value |
|---|
| `Beef` |
| `Pork` |
| `Lamb` |
| `Veal` |
| `Poultry` |
| `Game` |
| `Offal` |
| `Egg` |
| `Seafood` |
| `Shellfish` |
| `Freshwater Fish` |

#### Dairy & Plant Proteins

| Value |
|---|
| `Dairy` |
| `Cheese` |
| `Tofu` |
| `Tempeh` |
| `Legume` |
| `Bean` |
| `Lentil` |
| `Chickpea` |

#### Starches & Grains

| Value |
|---|
| `Rice` |
| `Pasta` |
| `Noodles` |
| `Bread` |
| `Flour / Dough` |
| `Potato` |
| `Grain` |
| `Corn / Maize` |

#### Vegetables & Fungi

| Value |
|---|
| `Vegetable` |
| `Leafy Green` |
| `Allium` |
| `Root Vegetable` |
| `Brassica` |
| `Mushroom` |
| `Tomato` |
| `Chili` |
| `Aubergine / Eggplant` |
| `Squash` |

#### Fruit, Nuts & Flavourings

| Value |
|---|
| `Fruit` |
| `Citrus` |
| `Stone Fruit` |
| `Tropical Fruit` |
| `Dried Fruit` |
| `Nut / Seed` |
| `Chocolate` |
| `Coconut` |
| `Herb-forward` |
| `Spice-forward` |
| `Fermented / Preserved` |

---

## 3. Operational Metadata Fields

### 3.1 Complexity

**What it answers:** How demanding is this to execute for a competent home cook?

**Type:** Single-select. Required.

| Value | Description |
|---|---|
| `Basic` | Minimal technique required. Beginner-friendly |
| `Intermediate` | Some technique, timing, or multi-step process required |
| `Advanced` | Significant technique, judgment, or skill required |
| `Project` | Multi-day, multi-stage, or highly demanding work |

**Design note:** Rate by effort and technique requirement, not ingredient count. A 30-ingredient salad may be Basic. A three-step beurre blanc is Intermediate to Advanced.

---

### 3.2 Time Class

**What it answers:** How long does this take from start to plate, including inactive time?

**Type:** Single-select. Required.

| Value | Approximate total time |
|---|---|
| `Under 15 min` | 0–15 minutes |
| `15–30 min` | 15–30 minutes |
| `30–60 min` | 30–60 minutes |
| `1–2 hr` | 1 to 2 hours |
| `2–4 hr` | 2 to 4 hours |
| `Half Day+` | 4 to 8 hours |
| `Multi-Day` | Overnight, 24+ hours, or multi-stage over days |

**Design note:** Time Class captures total elapsed time, including resting, marinating, rising, chilling, or soaking. Prep time and cook time exist as separate numeric fields. Time Class is for filtering and browsing.

---

### 3.3 Service Format

**What it answers:** How is this served and in what social context?

**Type:** Single-select. Required.

| Value | Description |
|---|---|
| `Single Plate` | Plated individually, served directly |
| `Family Style` | Served at the table for sharing |
| `Buffet / Shared` | Available for guests to help themselves |
| `Meal Prep` | Made ahead in bulk, portioned later |
| `Party Food` | Designed for groups, small bites or finger food |
| `Lunchbox` | Packable, room-temperature-stable |
| `Sauce / Add-On` | Applied to or served alongside another dish |
| `Side Component` | Served as part of a larger plate assembly |
| `Base Recipe` | Made to be used in other recipes |
| `Kitchen Use` | Not served as a dish — pantry ingredient, stock, brine |

---

### 3.4 Season

**What it answers:** When does this dish naturally belong?

**Type:** Single-select. Optional.

| Value |
|---|
| `Spring` |
| `Summer` |
| `Autumn` |
| `Winter` |
| `All Year` |

---

### 3.5 Mood Tags

**What it answers:** What does this dish feel like? What occasion or state does it suit?

**Type:** Multi-select. Optional.

| Value |
|---|
| `Light` |
| `Fresh` |
| `Comfort` |
| `Rich` |
| `Smoky` |
| `Spicy` |
| `Sharp / Acidic` |
| `Umami-forward` |
| `Bitter` |
| `Sweet` |
| `Festive` |
| `Rustic` |
| `Elegant` |
| `Everyday` |
| `Restorative` |
| `Indulgent` |
| `Cold Weather` |
| `Hot Weather` |

---

### 3.6 Storage Profile

**What it answers:** How does this recipe behave once cooked?

**Type:** Multi-select. Optional.

| Value |
|---|
| `Best Fresh` |
| `Keeps 2–3 Days` |
| `Keeps Up to a Week` |
| `Freezer Friendly` |
| `Reheats Well` |
| `Improves Over Time` |
| `Batch Cook Friendly` |
| `Picnic / Transport Friendly` |
| `Long Shelf Life` |

---

## 4. Multi-Select Facets

### 4.1 Dietary & Practical Filters

**What it answers:** What practical dietary constraints or qualities apply?

**Type:** Multi-select. Optional.

**Design note:** These are filters for retrieval, not identity labels. Apply them accurately. A dish that could be made vegan with one swap is not Vegan.

| Value |
|---|
| `Vegetarian` |
| `Vegan` |
| `Pescatarian` |
| `Gluten-Free` |
| `Dairy-Free` |
| `Egg-Free` |
| `Nut-Free` |
| `Soy-Free` |
| `Low-Carb` |
| `High-Protein` |
| `Alcohol-Free` |
| `Halal-Friendly` |
| `Kosher-Style` |
| `Low-Sodium` |
| `No Added Sugar` |

---

### 4.2 Provision Tags

**What it answers:** What practical operational qualities does this recipe have?

**Type:** Multi-select. Optional.

**Design note:** This is a flexible operational facet. It bridges dietary filters and mood tags by addressing real kitchen planning considerations.

| Value |
|---|
| `Weeknight` |
| `Weekend` |
| `Pantry-Heavy` |
| `Freezer-Build` |
| `Dinner Party` |
| `Leftover-Friendly` |
| `One-Pot` |
| `One-Pan` |
| `No Oven` |
| `No Stovetop` |
| `Kitchen-Equipment-Intensive` |
| `Minimal Equipment` |
| `Budget-Friendly` |
| `Crowd-Scaled` |
| `Kid-Friendly` |
| `Pantry Clear-Out` |

---

## 5. Sevastolink Overlay Fields

These fields impose operational identity on the archive without replacing culinary classification. They are secondary to the core taxonomy and should feel structural rather than decorative.

### 5.1 Sector

**What it answers:** What station or operational area of a working kitchen does this recipe primarily belong to?

**Type:** Single-select. Optional.

**Design note:** Borrowed loosely from professional kitchen structure, adapted for a home archive. This field creates a spatial metaphor that groups recipes by their kitchen home. It also provides a fast filter for the user's own mental model of their kitchen workflow.

| Value | Represents |
|---|---|
| `Fire Line` | Stovetop and oven cooking. Sears, braises, stews, roasts |
| `Cold Line` | Raw, chilled, assembled. Salads, dressings, cold sauces, crudités |
| `Bakehouse` | Baking, bread, pastry, dough-based work |
| `Provisions` | Pantry-making. Stocks, preserves, ferments, dried goods |
| `House Stock` | Recipes that maintain the household kitchen: broths, bases, spice blends |
| `Service` | Plated or presented dishes for serving at the table |
| `Galley` | General working recipes with no specific station identity |

---

### 5.2 Class

**What it answers:** What is the operational character of this recipe? What kind of effort or occasion does it represent?

**Type:** Single-select. Optional.

| Value | Character |
|---|---|
| `House Standard` | A reliable recipe cooked regularly |
| `Field Meal` | Fast, practical, no ceremony required |
| `Long Simmer` | Low-effort but time-intensive. Set and leave |
| `Quick Assembly` | Fast execution, minimal technique |
| `Weekend Project` | Demanding, extended, intentional |
| `Base Component` | Made to be used in other recipes |
| `Service Sauce` | A sauce, condiment, or dressing for serving |
| `Preservation Run` | A batch for the pantry or freezer |
| `Festive Operation` | Reserved for special occasions |
| `Experimental` | Being tested. Not yet a House Standard |

---

### 5.3 Heat Window

**What it answers:** What is the dominant heat environment this recipe requires?

**Type:** Single-select. Optional.

**Design note:** A practical field for kitchen planning. Knowing that five recipes in a week all require the oven lets the user batch them efficiently.

| Value |
|---|
| `No Heat` |
| `Cold Prep` |
| `Low Heat` |
| `Medium Heat` |
| `High Heat` |
| `Oven` |
| `Grill / Open Fire` |
| `Multi-Stage` |

---

### 5.4 Service Notes

**What it answers:** What does the cook need to know about serving, pairing, or presenting this dish?

**Type:** Free text. Optional.

Examples:
* `Best with a full-bodied red — Syrah or Rioja`
* `Better on day two. Make ahead.`
* `Serve immediately. Does not hold well.`
* `Reduce salt by half if using commercial stock`
* `Pairs well with the yogurt flatbread from this archive`

---

## 6. Field Type Reference

| Field | Type | Required |
|---|---|---|
| `title` | Free text | Yes |
| `slug` | Derived / auto-generated | Yes |
| `short_description` | Free text | Optional |
| `dish_role` | Single-select | Yes |
| `primary_cuisine` | Single-select | Yes |
| `secondary_cuisines` | Multi-select | Optional |
| `technique_family` | Single-select | Yes |
| `ingredient_families` | Multi-select | Yes |
| `complexity` | Single-select | Yes |
| `time_class` | Single-select | Yes |
| `service_format` | Single-select | Yes |
| `season` | Single-select | Optional |
| `mood_tags` | Multi-select | Optional |
| `storage_profile` | Multi-select | Optional |
| `dietary_flags` | Multi-select | Optional |
| `provision_tags` | Multi-select | Optional |
| `servings` | Integer or text | Optional |
| `prep_time_minutes` | Integer | Optional |
| `cook_time_minutes` | Integer | Optional |
| `total_time_minutes` | Derived (prep + cook) | Derived |
| `rest_time_minutes` | Integer | Optional |
| `ingredients` | Structured array | Yes |
| `steps` | Structured array | Yes |
| `recipe_notes` | Free text | Optional |
| `service_notes` | Free text | Optional |
| `storage_notes` | Free text | Optional |
| `substitution_notes` | Free text | Optional |
| `source_type` | Single-select | Yes |
| `source_title` | Free text | Optional |
| `source_author` | Free text | Optional |
| `source_url` | URL string | Optional |
| `source_notes` | Free text | Optional |
| `raw_source_text` | Free text (long) | Optional |
| `verification_state` | Single-select | Yes |
| `favorite` | Boolean | Yes (default false) |
| `rating` | Integer 1–5 | Optional |
| `last_cooked_at` | Date | Optional |
| `last_viewed_at` | Date | Derived |
| `sector` | Single-select | Optional |
| `class` | Single-select | Optional |
| `heat_window` | Single-select | Optional |

---

## 7. Example Classifications

### Example 1 — Ragù alla Bolognese

A slow meat sauce from Bologna, central Italy.

| Field | Value |
|---|---|
| Dish Role | `Main` |
| Primary Cuisine | `Italian` |
| Technique Family | `Braise` |
| Ingredient Families | `Beef`, `Pork`, `Tomato`, `Dairy` |
| Complexity | `Intermediate` |
| Time Class | `2–4 hr` |
| Service Format | `Family Style` |
| Season | `Autumn` |
| Mood Tags | `Comfort`, `Rich`, `Rustic` |
| Storage Profile | `Reheats Well`, `Freezer Friendly`, `Improves Over Time` |
| Sector | `Fire Line` |
| Class | `Long Simmer` |
| Heat Window | `Low Heat` |
| Verification State | `Verified` |
| Service Notes | `Serve with fresh tagliatelle, never spaghetti. Finish with a knob of butter off heat.` |

---

### Example 2 — Som Tam (Green Papaya Salad)

A sharp, spicy salad from Northeast Thailand (Isaan) and Laos.

| Field | Value |
|---|---|
| Dish Role | `Salad` |
| Primary Cuisine | `Thai` |
| Secondary Cuisines | `Laotian` |
| Technique Family | `Raw` |
| Ingredient Families | `Vegetable`, `Chili`, `Citrus`, `Nut / Seed` |
| Complexity | `Basic` |
| Time Class | `Under 15 min` |
| Service Format | `Shared Plate` |
| Season | `Summer` |
| Mood Tags | `Fresh`, `Spicy`, `Sharp / Acidic` |
| Storage Profile | `Best Fresh` |
| Dietary Flags | `Gluten-Free` |
| Sector | `Cold Line` |
| Class | `Quick Assembly` |
| Heat Window | `No Heat` |
| Verification State | `Verified` |
| Service Notes | `Pound in a mortar. Adjust fish sauce, lime, and sugar to balance. Serve immediately.` |

---

### Example 3 — Mole Negro

A complex, dark sauce from Oaxaca, Mexico. Multiple chillies, chocolate, dried fruit, spices.

| Field | Value |
|---|---|
| Dish Role | `Sauce` |
| Primary Cuisine | `Oaxacan` |
| Secondary Cuisines | `Mexican` |
| Technique Family | `Multi-Stage` |
| Ingredient Families | `Chili`, `Chocolate`, `Spice-forward`, `Dried Fruit`, `Nut / Seed`, `Poultry` |
| Complexity | `Project` |
| Time Class | `Half Day+` |
| Service Format | `Sauce / Add-On` |
| Season | `Autumn` |
| Mood Tags | `Rich`, `Smoky`, `Rustic`, `Festive` |
| Storage Profile | `Improves Over Time`, `Freezer Friendly`, `Batch Cook Friendly` |
| Sector | `Fire Line` |
| Class | `Weekend Project` |
| Heat Window | `Multi-Stage` |
| Verification State | `Unverified` |
| Service Notes | `Build over two days for best flavor. Freezes in portions. Traditionally served with turkey.` |

---

### Example 4 — Miso Soup with Tofu and Wakame

A daily Japanese soup, made from dashi, miso paste, tofu, and seaweed.

| Field | Value |
|---|---|
| Dish Role | `Soup` |
| Primary Cuisine | `Japanese` |
| Technique Family | `Simmer` |
| Ingredient Families | `Tofu`, `Fermented / Preserved`, `Mushroom` |
| Complexity | `Basic` |
| Time Class | `Under 15 min` |
| Service Format | `Single Plate` |
| Season | `All Year` |
| Mood Tags | `Restorative`, `Umami-forward`, `Light` |
| Storage Profile | `Best Fresh` |
| Dietary Flags | `Vegan`, `Gluten-Free` |
| Sector | `Fire Line` |
| Class | `Field Meal` |
| Heat Window | `Low Heat` |
| Verification State | `Verified` |
| Service Notes | `Do not boil after adding miso. Add tofu last.` |

---

### Example 5 — Injera

An Ethiopian/Eritrean sourdough flatbread made from teff flour. Also functions as plate and utensil.

| Field | Value |
|---|---|
| Dish Role | `Bread` |
| Primary Cuisine | `Ethiopian` |
| Secondary Cuisines | `Eritrean` |
| Technique Family | `Ferment` |
| Ingredient Families | `Grain`, `Fermented / Preserved` |
| Complexity | `Advanced` |
| Time Class | `Multi-Day` |
| Service Format | `Base Recipe` |
| Season | `All Year` |
| Mood Tags | `Rustic`, `Sharp / Acidic` |
| Storage Profile | `Keeps 2–3 Days` |
| Dietary Flags | `Gluten-Free`, `Vegan`, `Egg-Free`, `Dairy-Free` |
| Sector | `Bakehouse` |
| Class | `Weekend Project` |
| Heat Window | `Medium Heat` |
| Verification State | `Unverified` |
| Service Notes | `Ferment 2–3 days for sourness. Cook on a flat non-stick pan. Rest covered.` |

---

### Example 6 — Chicken Stock

A base stock made from chicken bones, aromatics, and water.

| Field | Value |
|---|---|
| Dish Role | `Pantry Staple` |
| Primary Cuisine | `Global / Mixed` |
| Technique Family | `Simmer` |
| Ingredient Families | `Poultry`, `Vegetable`, `Herb-forward`, `Allium` |
| Complexity | `Basic` |
| Time Class | `2–4 hr` |
| Service Format | `Kitchen Use` |
| Season | `All Year` |
| Mood Tags | `Restorative` |
| Storage Profile | `Freezer Friendly`, `Batch Cook Friendly` |
| Dietary Flags | `Gluten-Free`, `Dairy-Free` |
| Provision Tags | `Freezer-Build`, `Pantry-Heavy` |
| Sector | `House Stock` |
| Class | `Base Component` |
| Heat Window | `Low Heat` |
| Verification State | `Verified` |
| Service Notes | `Skim fat before portioning. Freeze in 500ml blocks.` |

---

### Example 7 — Khachapuri (Georgian Cheese Bread)

An open-faced bread boat filled with cheese, butter, and egg from Georgia.

| Field | Value |
|---|---|
| Dish Role | `Bread` |
| Primary Cuisine | `Georgian` |
| Technique Family | `Bake` |
| Ingredient Families | `Flour / Dough`, `Cheese`, `Egg`, `Dairy` |
| Complexity | `Intermediate` |
| Time Class | `1–2 hr` |
| Service Format | `Shared Plate` |
| Season | `Winter` |
| Mood Tags | `Comfort`, `Rich`, `Indulgent` |
| Storage Profile | `Best Fresh` |
| Sector | `Bakehouse` |
| Class | `Weekend Project` |
| Heat Window | `Oven` |
| Verification State | `Unverified` |
| Service Notes | `Serve immediately from oven. Mix egg and butter into filling at the table.` |

---

### Example 8 — Beet-Cured Salmon (Gravlax)

A Scandinavian-style cured salmon with beet, dill, and salt. No heat applied.

| Field | Value |
|---|---|
| Dish Role | `Starter` |
| Primary Cuisine | `Nordic` |
| Secondary Cuisines | `Swedish` |
| Technique Family | `Cure` |
| Ingredient Families | `Seafood`, `Herb-forward`, `Citrus` |
| Complexity | `Intermediate` |
| Time Class | `Multi-Day` |
| Service Format | `Single Plate` |
| Season | `Winter` |
| Mood Tags | `Elegant`, `Fresh`, `Festive` |
| Storage Profile | `Keeps Up to a Week`, `Improves Over Time` |
| Dietary Flags | `Gluten-Free`, `Dairy-Free` |
| Sector | `Cold Line` |
| Class | `Preservation Run` |
| Heat Window | `No Heat` |
| Verification State | `Verified` |
| Service Notes | `Cure 48–72 hours under weight. Slice thin against grain. Serve with crème fraîche and rye.` |

---

### Example 9 — Shakshuka

Eggs poached in a spiced tomato and pepper sauce. Levantine / North African origin.

| Field | Value |
|---|---|
| Dish Role | `Breakfast` |
| Primary Cuisine | `Levantine` |
| Secondary Cuisines | `North African`, `Israeli` |
| Technique Family | `Simmer` |
| Ingredient Families | `Egg`, `Tomato`, `Chili`, `Spice-forward` |
| Complexity | `Basic` |
| Time Class | `15–30 min` |
| Service Format | `Single Plate` |
| Season | `All Year` |
| Mood Tags | `Comfort`, `Spicy`, `Rustic`, `Everyday` |
| Storage Profile | `Best Fresh` |
| Dietary Flags | `Vegetarian`, `Gluten-Free`, `Dairy-Free` |
| Provision Tags | `One-Pan`, `Weeknight`, `Pantry-Heavy` |
| Sector | `Fire Line` |
| Class | `Field Meal` |
| Heat Window | `Medium Heat` |
| Verification State | `Verified` |
| Service Notes | `Do not overcook eggs. Serve in the pan with bread for scooping.` |

---

### Example 10 — Bacalhau à Brás

A Portuguese salt cod dish with potatoes, onions, and egg.

| Field | Value |
|---|---|
| Dish Role | `Main` |
| Primary Cuisine | `Portuguese` |
| Technique Family | `Fry` |
| Ingredient Families | `Seafood`, `Egg`, `Potato`, `Allium` |
| Complexity | `Intermediate` |
| Time Class | `1–2 hr` |
| Service Format | `Family Style` |
| Season | `All Year` |
| Mood Tags | `Comfort`, `Rich`, `Rustic`, `Everyday` |
| Storage Profile | `Best Fresh` |
| Provision Tags | `Weeknight`, `One-Pan` |
| Sector | `Fire Line` |
| Class | `House Standard` |
| Heat Window | `Medium Heat` |
| Verification State | `Verified` |
| Service Notes | `Salt cod must soak 24–48 hours. Change water 3–4 times. Add egg off heat.` |

---

## 8. Recommended Final Taxonomy Model

### 8.1 Required fields (must be set before Verified state)

| Field | Type |
|---|---|
| `title` | Free text |
| `dish_role` | Single-select |
| `primary_cuisine` | Single-select |
| `technique_family` | Single-select |
| `ingredient_families` | Multi-select |
| `complexity` | Single-select |
| `time_class` | Single-select |
| `service_format` | Single-select |
| `ingredients` | Structured array |
| `steps` | Structured array |
| `source_type` | Single-select |
| `verification_state` | Single-select |

### 8.2 Optional but highly recommended

| Field | Type |
|---|---|
| `short_description` | Free text |
| `season` | Single-select |
| `mood_tags` | Multi-select |
| `storage_profile` | Multi-select |
| `provision_tags` | Multi-select |
| `service_notes` | Free text |
| `sector` | Single-select |
| `class` | Single-select |
| `heat_window` | Single-select |
| `servings` | Integer or text |
| `prep_time_minutes` | Integer |
| `cook_time_minutes` | Integer |

### 8.3 Optional, lower priority

| Field | Type |
|---|---|
| `secondary_cuisines` | Multi-select |
| `dietary_flags` | Multi-select |
| `rating` | Integer 1–5 |
| `rest_time_minutes` | Integer |
| `last_cooked_at` | Date |
| `recipe_notes` | Free text |
| `substitution_notes` | Free text |
| `storage_notes` | Free text |
| `source_title` | Free text |
| `source_author` | Free text |
| `source_url` | URL |
| `source_notes` | Free text |

### 8.4 For AI-enriched records only

| Field | Type |
|---|---|
| `ai_summary` | Free text |
| `ai_suggested_tags` | JSON |
| `ai_normalized_json` | JSON |
| `ai_embedding` | Vector (v2) |
| `ai_last_processed_at` | Datetime |
| `ai_model_used` | String |

---

## 9. Notes for Database Implementation

### 9.1 Single-select fields

Store as `TEXT` with a constraint or enum check. Do not use foreign key lookups for taxonomy values in v1 — it adds join complexity without benefit at this scale.

```sql
dish_role TEXT NOT NULL CHECK (dish_role IN ('Breakfast','Brunch','Snack','Starter',...))
```

If the vocabulary needs to be editable at runtime, store the vocabulary in a separate `taxonomy_values` table keyed by field name. This allows expanding the cuisine list without a schema migration.

Recommended approach for v1: stored vocabulary in a constants file, with the database accepting any text value but the application enforcing selection from the list.

---

### 9.2 Multi-select fields

Store as either:

**Option A — JSON array in a single column**
```sql
ingredient_families TEXT  -- stored as JSON array: '["Beef","Tomato","Pasta"]'
mood_tags TEXT            -- stored as JSON array: '["Comfort","Rich"]'
```

This is the simplest approach for SQLite in v1. Retrieval by value requires a `LIKE` or `json_each` query but works reliably.

**Option B — Junction table**
```sql
recipe_ingredient_families (recipe_id, ingredient_family)
recipe_mood_tags (recipe_id, mood_tag)
```

This enables clean indexed queries but adds table count and join complexity. Recommended only if multi-select filtering is known to be a performance concern.

**Recommendation for v1:** JSON arrays in the recipe row. Migrate to junction tables in v2 if search performance requires it.

---

### 9.3 Structured rows (ingredients and steps)

In the canonical v1 schema, ingredients and steps are stored in dedicated tables, not JSON blobs on the recipe row.

**Recipe ingredients**

Store in `recipe_ingredients` with one row per ingredient line.

Recommended fields:
* `recipe_id`
* `position`
* `group_heading`
* `quantity`
* `unit`
* `item`
* `preparation`
* `optional`
* `display_text`

**Recipe steps**

Store in `recipe_steps` with one row per step.

Recommended fields:
* `recipe_id`
* `position`
* `instruction`
* `time_note`
* `equipment_note`

For full-text search across ingredients, maintain a flattened `ingredient_text` column on the recipe row, computed by the application from the related ingredient records at save time.

---

### 9.4 Free text fields

Store as `TEXT`, nullable.

`raw_source_text` may be very long. In the canonical v1 schema it lives in the dedicated `recipe_sources` table, not directly on the `recipes` row.

---

### 9.5 Slug

Derived from title at creation time. Stored and indexed as `TEXT UNIQUE`. Must not change after initial creation unless explicitly regenerated by the user. Slugs are used for stable references and URL generation.

---

### 9.6 Timestamps

| Field | Type | Notes |
|---|---|---|
| `created_at` | `DATETIME` | Set on insert, never modified |
| `updated_at` | `DATETIME` | Updated on any record change |
| `last_cooked_at` | `DATETIME` | User-set, nullable |
| `last_viewed_at` | `DATETIME` | Updated on recipe view, nullable |
| `ai_last_processed_at` | `DATETIME` | Nullable, AI-only |

---

### 9.7 Search index recommendations

For SQLite in v1, create FTS5 virtual table indexes on:
* `title`
* `short_description`
* `ingredient_text` (flattened ingredient item names)
* `recipe_notes`

Standard `WHERE` column filtering (no full-text) is acceptable for:
* `dish_role`
* `primary_cuisine`
* `technique_family`
* `complexity`
* `time_class`
* `verification_state`
* `favorite`
* `sector`

Multi-select fields stored as JSON require `json_each()` or `LIKE '%value%'` queries in SQLite v1. This is acceptable for a single-user personal archive.

---

### 9.8 Vocabulary management

The taxonomy enums in this document are the authoritative vocabulary. They should be:

1. Stored in a constants file in the application layer (e.g., `taxonomy.ts` or `taxonomy.py`)
2. Used for validation at both API and UI layers
3. Used to populate dropdowns and multi-select controls
4. Not hardcoded in SQL constraints — this avoids migration pain when the vocabulary is extended

The vocabulary may be extended by adding values to the constants file. Values should never be removed if they are referenced by existing records — deprecation is the correct approach.

---

### 9.9 AI embedding field

Defer to v2. Not required for v1 functionality. When implemented, use a dedicated column or a separate `recipe_embeddings` table. SQLite does not natively support vector operations; a vector extension (sqlite-vec) or external store (ChromaDB, FAISS) will be needed.

---

## Decisions Made

1. Taxonomy uses eleven independent classification layers plus the Sevastolink overlay.
2. Dish Role vocabulary is expanded to 20 values including `Street Food`, `Component`, `Confectionery`.
3. Primary Cuisine vocabulary is expanded to 80+ values with regional granularity (e.g., `Cantonese`, `Sichuan`, `Oaxacan`, `South Indian`).
4. Technique Family is expanded to 27 values including `Dehydrate` and refined `Multi-Stage`.
5. Ingredient Families is reorganized into five groups: Proteins, Dairy & Plant Proteins, Starches & Grains, Vegetables & Fungi, Fruit / Nuts / Flavourings.
6. Mood Tags expanded to 18 values including `Umami-forward`, `Sharp / Acidic`, `Bitter`, `Restorative`.
7. Service Format includes `Kitchen Use` for pantry and base recipes that are never plated.
8. Sevastolink Sector simplified to 7 values. `Archive` removed (verification state already handles this).
9. Sevastolink Class expanded to 10 values including `Experimental`.
10. For v1: multi-select fields stored as JSON arrays in SQLite. Junction tables deferred to v2.
11. Full-text search on title, description, ingredient text, and notes via FTS5.
12. Vocabulary managed in application-layer constants, not SQL constraints, to allow extension without migration.

---

## Open Questions

1. **Cuisine vocabulary expansion** — The current list is extensive but not exhaustive. Is there a curation strategy for adding cuisines over time, or should users be allowed to enter free text for cuisine and the vocabulary be trained from real use?
2. **Ingredient families granularity** — The current list uses broad groups (`Vegetable`, `Seafood`). Should the schema support a secondary ingredient layer for more specific retrieval (e.g., `Courgette`, `Mackerel`), or is this handled by full-text ingredient search?
3. **Sevastolink overlay optionality** — Should `Sector`, `Class`, and `Heat Window` default to a sensible value on creation, or remain null until the user sets them? Null values in required filters create awkward UI states.
4. **Rating implementation** — 1–5 integer vs half-star decimal vs simply Favorite boolean. Deferred but needs a decision before the schema is finalised.
5. **Multi-day recipe time class** — `Multi-Day` covers overnight to five days. Should this be split (e.g., `Overnight`, `Multi-Day`) for more useful filtering?

---

## Deliverables Created

* `docs/04_taxonomy/content-taxonomy-spec.md` v2.0 — this document (supersedes v1.0)

---

## What the Next Document Should Cover

**`docs/08_database/schema-spec.md` — Database Schema Spec v2.0**

This document now exists and is the canonical schema reference aligned with taxonomy v2.0.

The next update pass should keep the AI and architecture documents aligned with:

* v1 multi-select taxonomy fields stored as JSON arrays
* dedicated ingredient, step, note, and source tables
* `operational_class` as the schema-safe name for the Sevastolink class field
* migration-managed SQLite evolution from `schema_migrations`
