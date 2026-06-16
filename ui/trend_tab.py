"""Tab 4 – Trend over time for InstaAnalytics Pro."""

import streamlit as st
import pandas as pd
import plotly.express as px
from i18n import t


def render_trend_tab(trend_data: list[dict], theme: dict):
    """Render the trend-analysis tab.

    Parameters
    ----------
    trend_data : list[dict]
        Each dict must contain the keys *label*, *follower_count*,
        *following_count*, and *ratio*.
    theme : dict
        Visual theme with keys *card_bg*, *text_color*.
    """

    # --- Section 1: Followers / Following line chart -----------------------
    st.subheader(t('trend_over_time'))

    df = pd.DataFrame(trend_data)

    fig = px.line(
        df,
        x='label',
        y=['follower_count', 'following_count'],
        markers=True,
    )

    # Translate legend labels
    fig.for_each_trace(
        lambda tr: tr.update(
            name=t('followers') if 'follower' in tr.name else t('following'),
        )
    )

    fig.update_layout(
        plot_bgcolor=theme['card_bg'],
        paper_bgcolor=theme['card_bg'],
        font_color=theme['text_color'],
    )
    fig.update_xaxes(title_text=t('date'))
    fig.update_yaxes(title_text='')

    st.plotly_chart(fig, width="stretch")

    # --- Divider -----------------------------------------------------------
    st.markdown('---')

    # --- Section 2: Ratio area chart ---------------------------------------
    st.subheader(t('ratio'))

    fig_ratio = px.area(
        df,
        x='label',
        y='ratio',
        markers=True,
    )

    fig_ratio.update_layout(
        plot_bgcolor=theme['card_bg'],
        paper_bgcolor=theme['card_bg'],
        font_color=theme['text_color'],
    )

    st.plotly_chart(fig_ratio, width="stretch")
