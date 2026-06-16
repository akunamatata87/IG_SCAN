"""Dashboard tab (Tab 1) for InstaAnalytics Pro."""

import streamlit as st
import pandas as pd
import plotly.express as px
from i18n import t


def render_dashboard(comparison: dict):
    """Render the main dashboard with metrics, donut chart, and tips.

    Parameters
    ----------
    comparison : dict
        Keys: f1, f2, ing1, ing2, gained, lost, nfb, fans, friends
        (all are sets).
    """
    # --- Metrics row ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("followers"), len(comparison["f2"]),
              delta=len(comparison["f2"]) - len(comparison["f1"]))
    c2.metric(t("following"), len(comparison["ing2"]),
              delta=len(comparison["ing2"]) - len(comparison["ing1"]))
    c3.metric(t("new"), len(comparison["gained"]))
    c4.metric(t("lost"), len(comparison["lost"]), delta_color="inverse")

    # --- Separator ---
    st.markdown("---")

    # --- Donut chart + tip ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        labels = [t("friends"), t("fans"), t("not_following_back")]
        values = [
            len(comparison["friends"]),
            len(comparison["fans"]),
            len(comparison["nfb"]),
        ]
        df_pie = pd.DataFrame({"label": labels, "value": values})
        fig = px.pie(
            df_pie,
            names="label",
            values="value",
            title=t("audience_composition"),
            hole=0.4,
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")

    with col_right:
        st.info(t("theme_tip"))
