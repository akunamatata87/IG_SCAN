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
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(t('ratio'))
    with col2:
        st.write("") # small vertical spacing
        use_log = st.toggle(t('log_scale'), value=False)

    fig_ratio = px.area(
        df,
        x='label',
        y='ratio',
        markers=True,
    )

    if use_log:
        fig_ratio.update_yaxes(type='log')

    fig_ratio.update_layout(
        plot_bgcolor=theme['card_bg'],
        paper_bgcolor=theme['card_bg'],
        font_color=theme['text_color'],
    )

    st.plotly_chart(fig_ratio, width="stretch")
