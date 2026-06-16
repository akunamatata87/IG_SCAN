"""
InstaAnalytics Pro — Main Application Entry Point

A Streamlit app for analyzing Instagram follower/following data over time.
Supports local folder browsing (PC) and ZIP upload (Cloud/Android).
Persists all data in a single world_state.json file.
"""

import streamlit as st
import os
import sys

# Ensure the script directory is on the Python path so local imports work
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from i18n import t, render_language_toggle
from state_manager import (
    load_state, save_state, get_snapshot_labels, get_comparison_data,
    get_trend_data, get_all_events, migrate_from_folders, DEFAULT_STATE_PATH
)
from ui.css import inject_css
from ui.sidebar import (
    render_data_source, render_import_section, render_theme_settings,
    render_comparison_selectors, render_status, render_state_management
)
from ui.dashboard import render_dashboard
from ui.lost_tab import render_lost_tab
from ui.relations_tab import render_relations_tab
from ui.trend_tab import render_trend_tab
from ui.timeline_tab import render_timeline_tab

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="InstaAnalytics Pro",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR: SETTINGS TITLE + LANGUAGE TOGGLE ---
st.sidebar.title(f"⚙️ {t('settings')}")

# --- SIDEBAR: DATA SOURCE ---
st.sidebar.subheader(f"📂 {t('data')}")
data_path = render_data_source()

# --- SIDEBAR: THEME ---
st.sidebar.markdown("---")
theme = render_theme_settings()

# --- INJECT CUSTOM CSS ---
inject_css(
    primary_col=theme['primary_col'],
    bg_color=theme['bg_color'],
    text_color=theme['text_color'],
    card_bg=theme['card_bg'],
    btn_bg=theme['btn_bg'],
    btn_txt=theme['btn_txt']
)

# --- TITLE + LANGUAGE TOGGLE ---
title_col, lang_col = st.columns([6, 1])
with title_col:
    st.title(t('title'))
with lang_col:
    st.write("")  # Spacing
    render_language_toggle()

# --- LOAD OR MIGRATE STATE ---
state = load_state()

# Auto-migration: if no state file exists but legacy folders do
if state is None:
    legacy_path = os.path.join(_script_dir, "instagram_data")
    if os.path.isdir(legacy_path):
        subfolders = [d for d in os.listdir(legacy_path)
                      if os.path.isdir(os.path.join(legacy_path, d))
                      and not d.startswith('.')]
        if subfolders:
            with st.spinner(t('migration_detected', count=len(subfolders))):
                state, count = migrate_from_folders(legacy_path)
            if state and count > 0:
                st.success(t('migration_complete', count=count))
            else:
                st.error(t('migration_error'))
                st.stop()

# If still no state (no legacy data either), show import prompt
if state is None:
    if data_path:
        # User has selected a data source but no state yet — offer import
        st.info(t('no_state_file'))
        render_import_section(state, data_path)
    else:
        st.info(f"☁️ {t('upload_zip_prompt')}")
        st.markdown(f"""
        ### 📦 {t('zip_instructions_title')}
        1. {t('zip_step_1')}
        2. {t('zip_step_2')}
        3. {t('zip_step_3')}
        """)
    st.stop()

# --- SIDEBAR: IMPORT NEW DATA ---
if data_path:
    st.sidebar.markdown("---")
    render_import_section(state, data_path)

# --- SIDEBAR: STATE MANAGEMENT ---
if state is not None:
    st.sidebar.markdown("---")
    render_state_management(state)

# --- SIDEBAR: DATE COMPARISON ---
snapshot_labels = get_snapshot_labels(state)

if len(snapshot_labels) < 1:
    st.warning(t('no_state_file'))
    st.stop()

st.sidebar.markdown("---")
t0_label, t1_label = render_comparison_selectors(snapshot_labels)

# Validate date order
if t0_label >= t1_label:
    st.error(t('date_validation_error'))
    st.stop()

# --- COMPUTE DATA ---
comparison = get_comparison_data(state, t0_label, t1_label)
all_events = get_all_events(state)
trend_data = get_trend_data(state)

# --- SIDEBAR: STATUS ---
st.sidebar.markdown("---")
render_status(state, t1_label, comparison)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    t('tab_dashboard'),
    t('tab_lost'),
    t('tab_relations'),
    t('tab_trend'),
    t('tab_timeline')
])

with tab1:
    render_dashboard(comparison)

with tab2:
    render_lost_tab(comparison, all_events, t0_label, t1_label)

with tab3:
    render_relations_tab(comparison, t1_label)

with tab4:
    render_trend_tab(trend_data, theme)

with tab5:
    render_timeline_tab(all_events)
