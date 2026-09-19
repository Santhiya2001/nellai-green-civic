"""Canonical natural-language description of every complaint category, used
as the zero-shot reference text the classifier embeds and compares the
citizen's description against. Keeping this in one place means a new module
just adds its categories here -- no retraining required."""

CATEGORY_PROMPTS: dict[str, str] = {
    "DRAIN_BLOCKAGE": "a blocked or clogged street drain overflowing with dirty water",
    "WATER_STAGNATION": "stagnant standing water pooling on a road or open ground",
    "GARBAGE_DUMPING": "a pile of household garbage dumped on the street or open plot",
    "ILLEGAL_DUMPING": "illegal dumping of waste or debris in an unauthorized public place",
    "PLASTIC_WASTE": "scattered plastic waste and plastic bags littering an area",
    "ROAD_DAMAGE": "a damaged road surface with potholes or broken pavement",
    "STREETLIGHT_PROBLEM": "a broken or non-functioning street light at night",
    "PUBLIC_TOILET_ISSUE": "a dirty or broken public toilet facility",
    "FALLEN_TREE": "a fallen tree blocking a road or damaging property",
    "LAKE_POLLUTION": "a polluted lake with visible contamination or algae",
    "RIVER_POLLUTION": "river water polluted with sewage or industrial waste",
    "CANAL_BLOCKAGE": "an irrigation or storm water canal blocked by debris",
    "WATER_BODY_ENCROACHMENT": "illegal encroachment or construction on a water body",
    "REDUCED_WATER_LEVEL": "a lake, pond or well with unusually low water level",
    "CROP_DISEASE": "crop leaves showing signs of plant disease or fungal infection",
    "CROP_PEST": "crop plants damaged by insect or pest infestation",
    "WILDLIFE_SIGHTING": "a sighting of a wild animal, bird or insect species",
    "HABITAT_DAMAGE": "damage to a natural habitat such as clearing or burning vegetation",
    "FLOOD_REPORT": "a flooded street or area with rising water after heavy rain",
    "DISASTER_DAMAGE": "storm, cyclone or disaster damage to property or infrastructure",
    "OTHER": "a general civic or environmental issue not covered by other categories",
}

SEVERITY_KEYWORDS: dict[str, list[str]] = {
    "CRITICAL": ["rescue", "casualty", "casualties", "collapse", "collapsed", "flood", "flooding", "fire", "drowning", "life threatening", "electrocution"],
    "HIGH": ["overflow", "overflowing", "sewage", "contaminat", "days", "weeks", "children", "school", "hospital", "accident"],
    "MEDIUM": ["blocked", "broken", "damaged", "leak"],
    "LOW": ["minor", "small", "slight"],
}
