DOJO_PREREQUISITES = {
    "linux-basic": ["welcome"],
    "pwntools": ["welcome"],
    "pewter": ["linux-basic", "pwntools"],
    "cerulean": ["linux-basic", "pwntools"],
    "vermilion": ["linux-basic", "pwntools"],
    "saffron": ["linux-basic", "pwntools"],
    "celadon": ["pewter", "saffron", "cerulean", "vermilion"],
    "fuchsia": ["pewter", "saffron", "cerulean", "vermilion"],
    "cinnabar": ["pewter", "saffron", "cerulean", "vermilion"],
    "viridian": ["pewter", "saffron", "cerulean", "vermilion"],
    "leagueconference": ["celadon", "fuchsia", "cinnabar", "viridian"],
    "leagueconference": ["viridian"],
}