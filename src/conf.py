"""Sphinx configuration for michaelwisely.github.io."""

project = "Michael Wisely"
author = "Michael Wisely"
copyright = "2026, Michael Wisely"

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinxext.opengraph",
    "sphinx.ext.githubpages",  # writes .nojekyll so GitHub Pages serves _static/
]

exclude_patterns = ["_build"]

# Markdown (MyST) settings. colon_fence enables ::: blocks for dropdowns and callouts.
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

html_theme = "furo"
html_title = "Michael Wisely"
html_baseurl = "https://michaelwisely.github.io/"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = False
html_copy_source = False
html_theme_options = {
    # Pumpkin orange links and accents.
    "light_css_variables": {
        "color-brand-primary": "#c2410c",
        "color-brand-content": "#c2410c",
    },
    "dark_css_variables": {
        "color-brand-primary": "#fb923c",
        "color-brand-content": "#fb923c",
    },
}

ogp_site_url = html_baseurl
ogp_site_name = "Michael Wisely"
ogp_social_cards = {"enable": False}  # needs matplotlib; plain previews are fine

linkcheck_anchors = False
