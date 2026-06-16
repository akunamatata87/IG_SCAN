"""
CSS theming module for InstaAnalytics Pro.

Provides functions to build and inject a dynamic CSS theme into the
Streamlit application.  All colour parameters are validated against the
``#RRGGBB`` hex format; invalid values are silently replaced with safe
defaults.
"""

import re

import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

_DEFAULTS = {
    "primary_col": "#6C63FF",
    "bg_color": "#FFFFFF",
    "text_color": "#333333",
    "card_bg": "#F8F8F8",
    "btn_bg": "#6C63FF",
    "btn_txt": "#FFFFFF",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validated(value: str, fallback: str) -> str:
    """Return *value* if it is a valid ``#RRGGBB`` hex colour, otherwise
    return *fallback*.

    Parameters
    ----------
    value : str
        The colour string to validate.
    fallback : str
        A known-good ``#RRGGBB`` colour returned when *value* is invalid.

    Returns
    -------
    str
        A valid hex colour string.
    """
    if isinstance(value, str) and _HEX_COLOR_RE.match(value):
        return value
    return fallback


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_css(
    primary_col: str,
    bg_color: str,
    text_color: str,
    card_bg: str,
    btn_bg: str,
    btn_txt: str,
) -> str:
    """Build a complete ``<style>`` block for the InstaAnalytics Pro theme.

    Each colour parameter is validated against the ``#RRGGBB`` hex format.
    Invalid values are replaced with safe defaults so the UI never breaks.

    Parameters
    ----------
    primary_col : str
        Accent colour used for headings, links, and active-tab indicators.
    bg_color : str
        Main application background colour.
    text_color : str
        Default text colour.
    card_bg : str
        Background colour for metric and data-frame cards.
    btn_bg : str
        Button background colour.
    btn_txt : str
        Button text colour.

    Returns
    -------
    str
        An HTML ``<style>…</style>`` string ready to be injected via
        ``st.markdown(…, unsafe_allow_html=True)``.
    """
    primary_col = _validated(primary_col, _DEFAULTS["primary_col"])
    bg_color = _validated(bg_color, _DEFAULTS["bg_color"])
    text_color = _validated(text_color, _DEFAULTS["text_color"])
    card_bg = _validated(card_bg, _DEFAULTS["card_bg"])
    btn_bg = _validated(btn_bg, _DEFAULTS["btn_bg"])
    btn_txt = _validated(btn_txt, _DEFAULTS["btn_txt"])

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    /* ---- Fade-in animation for the main content area ---- */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0);   }}
    }}

    html, body, [class*="css"] {{
        font-family: 'Roboto', sans-serif;
        color: {text_color};
    }}

    .stApp {{
        background-color: {bg_color};
    }}

    /* Apply subtle fade-in to main content */
    section[data-testid="stMain"] > div {{
        animation: fadeIn 0.4s ease-out;
    }}

    h1, h2, h3, h4 {{
        color: {primary_col} !important;
        font-weight: 700;
    }}

    div[data-testid="stMetric"] {{
        background-color: {card_bg};
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        border-left: 5px solid {primary_col};
        color: {text_color};
    }}

    div[data-testid="stMetricLabel"] p {{
        color: {text_color} !important;
        opacity: 0.8;
    }}

    div[data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}

    div[data-testid="stDataFrame"] {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }}

    .stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_txt} !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }}

    .stButton > button:hover {{
        opacity: 0.9;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }}

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: {card_bg} !important;
        border-bottom: 2px solid {primary_col} !important;
        color: {primary_col} !important;
    }}

    a {{
        color: {primary_col} !important;
        text-decoration: none;
    }}
    </style>
    """


def inject_css(
    primary_col: str,
    bg_color: str,
    text_color: str,
    card_bg: str,
    btn_bg: str,
    btn_txt: str,
) -> None:
    """Build the theme CSS and inject it into the running Streamlit app.

    This is a convenience wrapper around :func:`build_css` that calls
    ``st.markdown`` with ``unsafe_allow_html=True``.

    Parameters
    ----------
    primary_col : str
        Accent colour used for headings, links, and active-tab indicators.
    bg_color : str
        Main application background colour.
    text_color : str
        Default text colour.
    card_bg : str
        Background colour for metric and data-frame cards.
    btn_bg : str
        Button background colour.
    btn_txt : str
        Button text colour.
    """
    css = build_css(primary_col, bg_color, text_color, card_bg, btn_bg, btn_txt)
    st.markdown(css, unsafe_allow_html=True)
