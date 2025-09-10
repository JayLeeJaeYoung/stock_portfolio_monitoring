# UI configurations and themes

mantine_theme = {
    "primaryColor": "custom-blue",
    "primaryShade": {"light": 6, "dark": 8},  # light: #2c40dc, dark: #1f32c4
    "colors": {
        "custom-blue": [
            "#ecefff",  # lightest
            "#d5dafb",
            "#a9b1f1",
            "#7a87e9",
            "#5362e1",
            "#3a4bdd",
            "#2c40dc",
            "#1f32c4",
            "#182cb0",
            "#0a259c",  # darkest
        ],
        # Neutral grays for backgrounds, text, and cards
        "gray": [
            "#f8f9fa",
            "#e9ecef",
            "#dee2e6",
            "#ced4da",
            "#adb5bd",
            "#868e96",
            "#6c757d",
            "#495057",
            "#343a40",
            "#212529",
        ],
    },
    "fontFamily": "'Roboto Flex', sans-serif",
    "defaultColorScheme": "auto",  # Supports light/dark mode toggling
    "components": {
        "Button": {
            "defaultProps": {"color": "custom-blue"},
        },
        "Card": {"styles": {"root": {"backgroundColor": "gray.0", "borderRadius": 8}}},
    },
}
