"""Tab 5 – Full Timeline view for InstaAnalytics Pro."""

import streamlit as st
import pandas as pd
from i18n import t


def render_timeline_tab(all_events: list[dict]):
    """Render an interactive, filterable timeline of all tracked events.

    Parameters
    ----------
    all_events : list[dict]
        Each dict must contain the keys **date**, **username**, **type**,
        and **link**.  The *type* value must be one of
        ``'new_follower'``, ``'unfollower'``, ``'new_following'``,
        or ``'unfollowed'``.
    """

    st.subheader(t('full_timeline'))

    if all_events:
        # -- build display-name mapping (evaluated at render time so the
        #    current language is picked up) --------------------------------
        event_display = {
            'new_follower':  t('event_new_follower'),
            'unfollower':    t('event_unfollower'),
            'new_following': t('event_new_following'),
            'unfollowed':    t('event_unfollowed'),
        }

        df = pd.DataFrame(all_events)

        # Map raw type codes to translated display names
        df['type'] = df['type'].map(event_display)

        # Rename columns to translated headers
        df = df.rename(columns={
            'date':     t('date'),
            'username': t('username'),
            'type':     t('event'),
            'link':     t('link'),
        })

        # -- filters -------------------------------------------------------
        unique_event_types = df[t('event')].unique().tolist()

        col_left, col_right = st.columns(2)

        with col_left:
            search_user = st.text_input(
                t('search_user'),
                placeholder=t('search_placeholder'),
            )

        with col_right:
            selected_events = st.multiselect(
                t('filter_event'),
                unique_event_types,
                default=unique_event_types,
            )

        # Apply event-type filter
        df = df[df[t('event')].isin(selected_events)]

        # Apply username search (case-insensitive, partial match)
        if search_user:
            df = df[
                df[t('username')]
                .str.contains(search_user, case=False, na=False)
            ]

        # Sort by date descending
        df = df.sort_values(by=t('date'), ascending=False)

        # -- display -------------------------------------------------------
        st.dataframe(
            df,
            column_config={
                t('link'): st.column_config.LinkColumn(),
            },
            hide_index=True,
            width="stretch",
        )
    else:
        st.info(t('need_two_dates'))
