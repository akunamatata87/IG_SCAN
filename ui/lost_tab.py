"""Tab 2 – Lost followers (unfollowers) between two snapshots."""

import streamlit as st
import pandas as pd
from i18n import t


def render_lost_tab(
    comparison: dict,
    all_events: list[dict],
    t0_label: str,
    t1_label: str,
) -> None:
    """Render the *Lost Followers* tab.

    Parameters
    ----------
    comparison : dict
        Must contain a ``'lost'`` key whose value is a set of usernames.
    all_events : list[dict]
        Event dicts with keys ``date``, ``username``, ``type``, ``link``.
    t0_label, t1_label : str
        Human-readable date labels for the two comparison snapshots.
    """
    st.subheader(t("lost_between", d1=t0_label, d2=t1_label))

    lost: set = comparison["lost"]

    if lost:
        df = pd.DataFrame({"Username": sorted(lost)})

        # Build a date lookup from unfollower events that fall in (t0, t1].
        date_lookup: dict[str, str] = {}
        for ev in all_events:
            if (
                ev["type"] == "unfollower"
                and ev["date"] > t0_label
                and ev["date"] <= t1_label
            ):
                date_lookup[ev["username"]] = ev["date"]

        df[t("abandon_date")] = df["Username"].map(
            lambda u: date_lookup.get(u, t1_label)
        )
        df["Link"] = "https://instagram.com/" + df["Username"]

        # Search box
        search: str = st.text_input(
            t("search_user"),
            placeholder=t("search_placeholder"),
            key="lost_search",
        )

        if search:
            df = df[
                df["Username"].str.contains(search, case=False, na=False)
            ]

        st.dataframe(
            df,
            column_config={"Link": st.column_config.LinkColumn()},
            hide_index=True,
            width="stretch",
        )

        csv: str = df.to_csv(index=False)
        st.download_button(
            t("download_csv"),
            csv,
            "unfollowers.csv",
            "text/csv",
        )
    else:
        st.success(t("no_lost"))
