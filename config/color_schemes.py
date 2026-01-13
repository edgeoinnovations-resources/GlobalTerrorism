"""Consistent color schemes for all GTD visualizations."""

ATTACK_TYPE_COLORS = {
    'Bombing/Explosion': '#e41a1c',
    'Armed Assault': '#377eb8',
    'Assassination': '#4daf4a',
    'Hostage Taking (Kidnapping)': '#984ea3',
    'Hostage Taking (Barricade Incident)': '#ff7f00',
    'Facility/Infrastructure Attack': '#ffff33',
    'Unarmed Assault': '#a65628',
    'Hijacking': '#f781bf',
    'Unknown': '#999999'
}

ATTACK_TYPE_COLORS_RGB = {
    'Bombing/Explosion': [228, 26, 28],
    'Armed Assault': [55, 126, 184],
    'Assassination': [77, 175, 74],
    'Hostage Taking (Kidnapping)': [152, 78, 163],
    'Hostage Taking (Barricade Incident)': [255, 127, 0],
    'Facility/Infrastructure Attack': [255, 255, 51],
    'Unarmed Assault': [166, 86, 40],
    'Hijacking': [247, 129, 191],
    'Unknown': [153, 153, 153]
}

REGION_COLORS = {
    'Middle East & North Africa': '#e41a1c',
    'South Asia': '#377eb8',
    'Sub-Saharan Africa': '#4daf4a',
    'South America': '#984ea3',
    'Western Europe': '#ff7f00',
    'Southeast Asia': '#ffff33',
    'Eastern Europe': '#a65628',
    'North America': '#f781bf',
    'Central America & Caribbean': '#999999',
    'East Asia': '#66c2a5',
    'Central Asia': '#fc8d62',
    'Australasia & Oceania': '#8da0cb'
}

REGION_COLORS_RGB = {
    'Middle East & North Africa': [228, 26, 28],
    'South Asia': [55, 126, 184],
    'Sub-Saharan Africa': [77, 175, 74],
    'South America': [152, 78, 163],
    'Western Europe': [255, 127, 0],
    'Southeast Asia': [255, 255, 51],
    'Eastern Europe': [166, 86, 40],
    'North America': [247, 129, 191],
    'Central America & Caribbean': [153, 153, 153],
    'East Asia': [102, 194, 165],
    'Central Asia': [252, 141, 98],
    'Australasia & Oceania': [141, 160, 203]
}

# Sequential color scale for heatmaps/density
DENSITY_COLORS = [
    '#ffffb2', '#fed976', '#feb24c',
    '#fd8d3c', '#fc4e2a', '#e31a1c', '#b10026'
]


def get_attack_color_rgb(attack_type: str) -> list:
    """Get RGB color for attack type, with fallback."""
    return ATTACK_TYPE_COLORS_RGB.get(attack_type, [153, 153, 153])


def get_region_color_rgb(region: str) -> list:
    """Get RGB color for region, with fallback."""
    return REGION_COLORS_RGB.get(region, [153, 153, 153])
