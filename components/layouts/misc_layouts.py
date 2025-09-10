import dash_mantine_components as dmc
from dash import html


def logo_and_title_layout(size):
    """
    size (str): Either "small" or "large"
    """
    if size == "large":
        svg_source = "/assets/app_logo_big.svg"
        style = {"width": "65px", "height": "65px"}
        order = 2
    elif size == "small":
        svg_source = "/assets/app_logo_small.svg"
        style = {"width": "35px", "height": "35px"}
        order = 4
    else:
        raise ValueError("size must be either 'small' or 'large'")

    logo_and_title_layout = dmc.Group(
        align="center",
        gap="xs",
        children=[
            html.Img(src=svg_source, style=style),
            dmc.Title(
                "The Investment Board",
                order=order,
                className="title-font",
            ),
        ],
    )
    return logo_and_title_layout
