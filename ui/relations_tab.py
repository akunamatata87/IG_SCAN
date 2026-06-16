"""Tab 3 – Relations: Not Following Back & Fans."""

import streamlit as st
import pandas as pd
from i18n import t


def render_relations_tab(comparison: dict, t1_label: str) -> None:
    """Render the *Relations* tab.

    Parameters
    ----------
    comparison : dict
        Must contain:
        - ``'nfb'``: set of usernames who do not follow back.
        - ``'fans'``: set of usernames who follow but are not followed.
    t1_label : str
        Human-readable date label for the end snapshot (T1).
    """
    nfb: set = comparison["nfb"]
    fans: set = comparison["fans"]

    # ------------------------------------------------------------------
    # Summary metrics row
    # ------------------------------------------------------------------
    col_m1, col_m2 = st.columns(2)
    col_m1.metric(t("not_following_back"), len(nfb))
    col_m2.metric(t("fans"), len(fans))

    st.markdown("---")

    # ------------------------------------------------------------------
    # Detail tables – two columns
    # ------------------------------------------------------------------
    col_left, col_right = st.columns(2)

    # --- Left column: Not Following Back ---
    with col_left:
        st.subheader(t("not_following_back_title"))

        if nfb:
            df_nfb = pd.DataFrame({
                "Username": sorted(nfb),
            })
            df_nfb[t("detection_date")] = t1_label
            df_nfb["Link"] = "https://instagram.com/" + df_nfb["Username"]

            search_nfb: str = st.text_input(
                t("search_user"),
                key="nfb_search",
            )

            if search_nfb:
                df_nfb = df_nfb[
                    df_nfb["Username"].str.contains(
                        search_nfb, case=False, na=False
                    )
                ]

            st.dataframe(
                df_nfb,
                column_config={"Link": st.column_config.LinkColumn()},
                hide_index=True,
                width="stretch",
            )

            csv_nfb: str = df_nfb.to_csv(index=False)
            st.download_button(
                t("download_csv"),
                csv_nfb,
                "not_following_back.csv",
                "text/csv",
                key="download_nfb",
            )
        else:
            st.info(t("no_users_in_category"))

    # --- Right column: Fans ---
    with col_right:
        st.subheader(t("fans_title"))

        if fans:
            df_fans = pd.DataFrame({
                "Username": sorted(fans),
            })
            df_fans[t("detection_date")] = t1_label
            df_fans["Link"] = "https://instagram.com/" + df_fans["Username"]

            search_fans: str = st.text_input(
                t("search_user"),
                key="fans_search",
            )

            if search_fans:
                df_fans = df_fans[
                    df_fans["Username"].str.contains(
                        search_fans, case=False, na=False
                    )
                ]

            st.dataframe(
                df_fans,
                column_config={"Link": st.column_config.LinkColumn()},
                hide_index=True,
                width="stretch",
            )

            csv_fans: str = df_fans.to_csv(index=False)
            st.download_button(
                t("download_csv"),
                csv_fans,
                "fans.csv",
                "text/csv",
                key="download_fans",
            )
        else:
            st.info(t("no_users_in_category"))
