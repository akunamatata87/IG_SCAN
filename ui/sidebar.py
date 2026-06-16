"""
sidebar.py – Sidebar module for InstaAnalytics Pro.

Renders the entire sidebar: data source selection, import functionality,
theme customization, and date comparison selectors.
"""

import streamlit as st
import os
import platform
import zipfile
import tempfile
import shutil
import io

from i18n import t
from data_loader import load_dataset
from state_manager import (
    load_state,
    save_state,
    import_snapshot,
    migrate_from_folders,
    get_snapshot_labels,
    get_latest_state_path,
)

# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------

def render_state_management(state: dict) -> None:
    """Render the state management expander for backup/restore."""
    with st.sidebar.expander(t("state_management"), expanded=False):
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        current_state_path = get_latest_state_path(directory)
        
        # 1. Download Current State
        if current_state_path and os.path.exists(current_state_path):
            file_name = os.path.basename(current_state_path)
            with open(current_state_path, "r", encoding="utf-8") as f:
                state_json = f.read()
            st.download_button(
                label=t("download_state"),
                data=state_json,
                file_name=file_name,
                mime="application/json",
                width="stretch"
            )
        
        # 2. Upload State (Restore Backup)
        uploaded_state = st.file_uploader(
            t("upload_state"),
            type=["json"],
            help=t("upload_state_help")
        )
        if uploaded_state is not None:
            if st.button("Restore Backup", width="stretch"):
                # Save the uploaded state directly with a new timestamp
                import json
                try:
                    uploaded_json = json.loads(uploaded_state.getvalue().decode("utf-8"))
                    save_state(uploaded_json)
                    st.success(t("state_uploaded"))
                    st.rerun()
                except Exception as e:
                    st.error(f"Invalid state file: {e}")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_ZIP_SIZE = 500 * 1024 * 1024  # 500 MB


# ---------------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------------

def render_data_source() -> str | None:
    """Render data-source options in the sidebar and return the selected path.

    On Windows the user may choose between a local folder browser and a
    ZIP upload.  On all other platforms only the ZIP upload is offered.

    Returns
    -------
    str | None
        Absolute path to the data directory, or ``None`` when no data
        source has been selected yet.
    """
    is_windows = platform.system() == "Windows"

    if is_windows:
        data_mode = st.sidebar.radio(
            t("data_source"),
            [t("local_folder"), t("upload_zip")],
            horizontal=True,
        )
    else:
        data_mode = t("upload_zip")

    # -- LOCAL FOLDER mode -------------------------------------------------
    if data_mode == t("local_folder"):
        return _render_local_folder()

    # -- ZIP UPLOAD mode ---------------------------------------------------
    return _render_zip_upload()


# ---------------------------------------------------------------------------
# Local-folder browsing (Windows only)
# ---------------------------------------------------------------------------

def _render_local_folder() -> str | None:
    """Render the local-folder browser and return the selected path."""
    # Use parent directory since this script is in ui/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = os.path.join(base_dir, "instagram_data")
    
    # Initialise session-state defaults
    if "local_folder" not in st.session_state:
        st.session_state["local_folder"] = default_path
    if "browse_path" not in st.session_state:
        st.session_state["browse_path"] = os.path.dirname(
            st.session_state["local_folder"]
        )

    # Expander with directory browser
    with st.sidebar.expander(t("browse_folder"), expanded=False):
        browse = st.session_state["browse_path"]

        # Current path
        st.caption(f"📍 {browse}")

        # Parent-folder button
        parent = os.path.dirname(browse)
        if parent != browse:
            if st.button(t("parent_folder")):
                st.session_state["browse_path"] = parent
                st.rerun()

        # List subdirectories
        try:
            subdirs = sorted(
                d
                for d in os.listdir(browse)
                if os.path.isdir(os.path.join(browse, d))
                and not d.startswith(".")
            )
        except PermissionError:
            subdirs = []
            st.warning(t("folder_access_denied"))

        if subdirs:
            selected = st.selectbox(
                t("subfolders"), subdirs, key="browse_select"
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(t("open")):
                    st.session_state["browse_path"] = os.path.join(
                        browse, selected
                    )
                    st.rerun()
            with col_b:
                if st.button(t("select")):
                    new_path = os.path.join(browse, selected)
                    st.session_state["local_folder"] = new_path
                    st.session_state["browse_path"] = new_path
                    st.rerun()
        else:
            st.info(t("no_subfolders"))

    # Manual text input
    root_path = st.sidebar.text_input(
        t("enter_path"),
        value=st.session_state["local_folder"],
        key="folder_input",
    )
    st.session_state["local_folder"] = root_path
    return root_path


# ---------------------------------------------------------------------------
# ZIP upload
# ---------------------------------------------------------------------------

def _render_zip_upload() -> str | None:
    """Render the ZIP uploader and return the extracted path (or *None*)."""

    uploaded_file = st.sidebar.file_uploader(
        t("upload_zip_help"),
        type=["zip"],
        help=t("upload_zip_tooltip"),
    )

    if uploaded_file is None:
        return None

    # Only extract when a *new* file is uploaded
    if (
        "zip_temp_dir" not in st.session_state
        or st.session_state.get("zip_name") != uploaded_file.name
    ):
        # ── Security: validate total uncompressed size ────────────
        zip_bytes = io.BytesIO(uploaded_file.getvalue())
        with zipfile.ZipFile(zip_bytes) as zf:
            total_size = sum(info.file_size for info in zf.infolist())
            if total_size > MAX_ZIP_SIZE:
                st.sidebar.error(t("zip_too_large"))
                return None

            # ── Security: reject path-traversal entries ───────────
            for info in zf.infolist():
                if ".." in info.filename or info.filename.startswith("/"):
                    st.sidebar.error(t("zip_invalid_entry"))
                    return None

        # ── Clean up previous temp directory ──────────────────────
        if "zip_temp_dir" in st.session_state:
            shutil.rmtree(st.session_state["zip_temp_dir"], ignore_errors=True)

        # ── Extract ───────────────────────────────────────────────
        temp_dir = tempfile.mkdtemp()
        zip_bytes.seek(0)
        with zipfile.ZipFile(zip_bytes) as zf:
            zf.extractall(temp_dir)

        # If the ZIP has a single root folder, descend into it
        contents = [
            d
            for d in os.listdir(temp_dir)
            if os.path.isdir(os.path.join(temp_dir, d))
        ]
        if len(contents) == 1:
            root_path = os.path.join(temp_dir, contents[0])
        else:
            root_path = temp_dir

        st.session_state["zip_temp_dir"] = root_path
        st.session_state["zip_name"] = uploaded_file.name

    return st.session_state["zip_temp_dir"]


# ---------------------------------------------------------------------------
# Import section
# ---------------------------------------------------------------------------

def render_import_section(state: dict, data_path: str) -> None:
    """Render the *Import new data* button and handle the import workflow.

    Parameters
    ----------
    state:
        The current application state dict (from :func:`load_state`).
    data_path:
        Path to the folder containing the Instagram export data.
    """
    if st.sidebar.button(t("import_new_data"), help=t("import_help")):
        new_data = load_dataset(data_path)

        label = st.sidebar.text_input(
            t("snapshot_label"),
            value="",
        )
        if not label:
            from datetime import datetime
            label = datetime.now().strftime("%Y-%m-%d")

        state, events = import_snapshot(state, new_data, label)
        save_state(state)

        has_changes = any([
            events.get("new_followers"),
            events.get("lost_followers"),
            events.get("new_following"),
            events.get("lost_following"),
        ])

        if has_changes or events.get("is_baseline"):
            st.sidebar.success(t("import_success"))
        else:
            st.sidebar.info(t("import_no_changes"))

        st.rerun()


# ---------------------------------------------------------------------------
# Theme settings
# ---------------------------------------------------------------------------

def render_theme_settings() -> dict:
    """Render the theme-customisation expander and return colour settings.

    Returns
    -------
    dict
        Keys: ``primary_col``, ``bg_color``, ``text_color``,
        ``card_bg``, ``btn_bg``, ``btn_txt``.
    """
    with st.sidebar.expander(t("theme_customization"), expanded=False):
        st.markdown(f"**{t('general_colors')}**")
        primary_col = st.color_picker(
            t("primary_color"), "#6200EE", help=t("primary_color_help")
        )
        bg_color = st.color_picker(t("app_background"), "#0E1117")
        text_color = st.color_picker(t("text_color"), "#FAFAFA")

        st.markdown(f"**{t('cards_windows')}**")
        card_bg = st.color_picker(t("card_background"), "#262730")

        st.markdown(f"**{t('interactive_elements')}**")
        btn_bg = st.color_picker(t("button_background"), "#6200EE")
        btn_txt = st.color_picker(t("button_text"), "#FFFFFF")

    return {
        "primary_col": primary_col,
        "bg_color": bg_color,
        "text_color": text_color,
        "card_bg": card_bg,
        "btn_bg": btn_bg,
        "btn_txt": btn_txt,
    }


# ---------------------------------------------------------------------------
# Comparison selectors
# ---------------------------------------------------------------------------

def render_comparison_selectors(
    snapshot_labels: list[str],
) -> tuple[str, str]:
    """Render the T0 / T1 date selectors in the sidebar.

    Parameters
    ----------
    snapshot_labels:
        Chronologically ordered list of snapshot label strings.

    Returns
    -------
    tuple[str, str]
        ``(t0_label, t1_label)`` – the selected start and end labels.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader(t("direct_comparison"))

    col_t0, col_t1 = st.sidebar.columns(2)
    with col_t0:
        t0_label = st.selectbox(
            t("start_t0"),
            snapshot_labels,
            index=0,
        )
    with col_t1:
        t1_label = st.selectbox(
            t("end_t1"),
            snapshot_labels,
            index=len(snapshot_labels) - 1,
        )

    # Validate chronological order
    if snapshot_labels.index(t0_label) >= snapshot_labels.index(t1_label):
        st.sidebar.error(t("date_validation_error"))

    return t0_label, t1_label


# ---------------------------------------------------------------------------
# Status / debug info
# ---------------------------------------------------------------------------

def render_status(state: dict, t1_label: str, comparison: dict) -> None:
    """Render the debug status section at the bottom of the sidebar.

    Parameters
    ----------
    state:
        The current application state dict.
    t1_label:
        The label of the currently selected T1 snapshot.
    comparison:
        Comparison data dict (as returned by
        :func:`state_manager.get_comparison_data`), expected to contain
        at least ``f2`` (followers at T1) and ``ing2`` (following at T1).
    """
    st.sidebar.markdown("---")
    st.sidebar.caption(f"{t('status_at')} {t1_label}")
    st.sidebar.text(f"{t('followers')}: {len(comparison['f2'])}")
    st.sidebar.text(f"{t('following')}: {len(comparison['ing2'])}")

    if len(comparison["ing2"]) == 0:
        st.sidebar.warning(t("warning_zero_following"))
