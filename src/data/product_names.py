"""Illustrative product name mapping for M5 SKU codes.

M5 dataset item IDs are anonymised - no real names exist. This module maps
SKU codes to plausible retail product names for demo purposes.
Specific high-frequency SKUs are mapped explicitly; all others fall back to a
deterministic category-level lookup seeded by the item number.
"""

_SPECIFIC: dict[str, str] = {
    # FOODS_3
    "FOODS_3_785": "Salsa Verde 16oz",
    "FOODS_3_324": "BBQ Sauce 18oz",
    "FOODS_3_385": "Hot Sauce 12oz",
    "FOODS_3_438": "Ranch Dressing 16oz",
    "FOODS_3_555": "Soy Sauce 10oz",
    "FOODS_3_090": "Ketchup 32oz",
    "FOODS_3_200": "Mustard 12oz",
    "FOODS_3_120": "Mayonnaise 30oz",
    # FOODS_2
    "FOODS_2_185": "Whole Milk 1gal",
    "FOODS_2_347": "Cheddar Cheese 8oz",
    "FOODS_2_031": "Greek Yogurt 32oz",
    "FOODS_2_098": "Orange Juice 64oz",
    # FOODS_1
    "FOODS_1_001": "Canned Tomatoes 28oz",
    "FOODS_1_025": "Black Beans 15oz",
    "FOODS_1_090": "Chicken Broth 32oz",
    # HOUSEHOLD_1
    "HOUSEHOLD_1_294": "Dish Soap 32oz",
    "HOUSEHOLD_1_232": "Laundry Detergent 50oz",
    "HOUSEHOLD_1_496": "Multi-Surface Cleaner 32oz",
    "HOUSEHOLD_1_477": "Paper Towels 6pk",
    "HOUSEHOLD_1_017": "Fabric Softener 64oz",
    "HOUSEHOLD_1_119": "Toilet Paper 12rl",
    "HOUSEHOLD_1_380": "Sponges 6pk",
    # HOUSEHOLD_2
    "HOUSEHOLD_2_315": "Kitchen Trash Bags 13gal 80ct",
    "HOUSEHOLD_2_296": "Aluminum Foil 200sqft",
    "HOUSEHOLD_2_336": "Plastic Wrap 200sqft",
    "HOUSEHOLD_2_473": "Sandwich Bags 150ct",
    "HOUSEHOLD_2_040": "Dishwasher Pods 72ct",
    "HOUSEHOLD_2_311": "Freezer Bags 30ct",
    # HOBBIES_1
    "HOBBIES_1_002": "Colored Pencils 24pk",
    "HOBBIES_1_138": "Watercolor Set 18pc",
    "HOBBIES_1_175": "Sketch Pad A4 50sh",
    "HOBBIES_1_216": "Glitter Glue 6pk",
    "HOBBIES_1_275": "Acrylic Paint Set 12pc",
    # HOBBIES_2
    "HOBBIES_2_116": "Jigsaw Puzzle 500pc",
    "HOBBIES_2_122": "Card Game Family Ed.",
    "HOBBIES_2_126": "Strategy Board Game",
}

_FALLBACK: dict[str, list[str]] = {
    "FOODS_1": [
        "Canned Tomatoes 28oz", "Black Beans 15oz", "Chicken Broth 32oz",
        "Peanut Butter 16oz", "Pasta Sauce 24oz", "Canned Corn 15oz",
        "Tuna 5oz", "Olive Oil 17oz", "Apple Cider Vinegar 32oz",
        "Maple Syrup 12oz",
    ],
    "FOODS_2": [
        "Whole Milk 1gal", "Cheddar Cheese 8oz", "White Bread Loaf",
        "Greek Yogurt 32oz", "Butter 1lb", "Orange Juice 64oz",
        "Sliced Turkey 9oz", "Cream Cheese 8oz", "Sour Cream 16oz",
        "Shredded Mozzarella 8oz",
    ],
    "FOODS_3": [
        "Potato Chips 8oz", "Sparkling Water 12pk", "Granola Bar 6ct",
        "Cookies 13oz", "Pretzels 16oz", "Mixed Nuts 10oz",
        "Energy Drink 4pk", "Salsa 16oz", "Tortilla Chips 12oz",
        "Trail Mix 9oz",
    ],
    "HOBBIES_1": [
        "Markers 10pk", "Construction Paper 50sh", "Craft Scissors",
        "Foam Stickers Set", "Paint Brush Set 7pc", "Modeling Clay 8pk",
        "Glue Sticks 6pk", "Scrapbook Kit", "Stencil Set 12pc",
        "Washi Tape 6rl",
    ],
    "HOBBIES_2": [
        "Puzzle 300pc", "Playing Cards", "Dice Set 6pc",
        "Trivia Game", "Coloring Book Adult", "Mini Travel Game",
        "Dominos Set", "Chess Set", "Sudoku Book", "Word Search 300pg",
    ],
    "HOUSEHOLD_1": [
        "All-Purpose Cleaner 32oz", "Sponges 6pk", "Paper Towels 8pk",
        "Toilet Paper 12rl", "Laundry Pods 32ct", "Dryer Sheets 120ct",
        "Dish Soap 16oz", "Scrub Brush", "Glass Cleaner 23oz",
        "Mop Refill Pads 2pk",
    ],
    "HOUSEHOLD_2": [
        "Trash Bags 30ct", "Storage Containers 3pk", "Kitchen Towels 4pk",
        "Foil Pans 3pk", "Plastic Cups 50ct", "Napkins 250ct",
        "Parchment Paper 45sqft", "Plastic Wrap 100sqft",
        "Rubber Gloves M", "Lint Roller 60sh",
    ],
}


def get_product_name(sku: str) -> str:
    """Return a plausible product name for a M5 SKU code.

    Strips the store suffix first (e.g. FOODS_3_785_CA_1_evaluation -> FOODS_3_785).
    """
    # Strip store/evaluation suffix - keep only CATEGORY_DEPT_ITEM
    parts = sku.split("_")
    if len(parts) >= 3:
        base = f"{parts[0]}_{parts[1]}_{parts[2]}"
    else:
        base = sku

    if base in _SPECIFIC:
        return _SPECIFIC[base]

    # Category+dept fallback with deterministic index
    if len(parts) >= 3:
        cat_dept = f"{parts[0]}_{parts[1]}"
        pool = _FALLBACK.get(cat_dept)
        if pool:
            try:
                idx = int(parts[2]) % len(pool)
            except ValueError:
                idx = 0
            return pool[idx]

    return base
