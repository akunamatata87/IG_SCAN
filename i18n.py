"""
i18n.py – Internationalization module for InstaAnalytics Pro.

Provides Italian ('it') and English ('en') translations for all
user-facing strings, a helper function ``t(key)`` to retrieve them,
and a Streamlit widget ``render_language_toggle()`` for switching
language at runtime.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Translation table
# ---------------------------------------------------------------------------

STRINGS: dict[str, dict[str, str]] = {
    "it": {
        # General
        "title": "📸 InstaAnalytics Pro",
        "settings": "Impostazioni",
        "data": "Dati",
        "data_source": "Sorgente dati:",
        "local_folder": "📁 Cartella locale",
        "upload_zip": "☁️ Carica ZIP",

        # Sidebar – Folder browsing
        "browse_folder": "📂 Sfoglia cartella",
        "parent_folder": "⬆️ Cartella superiore",
        "subfolders": "Sottocartelle:",
        "open": "📂 Apri",
        "select": "✅ Seleziona",
        "no_subfolders": "Nessuna sottocartella.",
        "folder_access_denied": "Accesso negato a questa cartella.",
        "enter_path": "Oppure inserisci il percorso:",
        "upload_zip_help": "Carica il file ZIP con i dati Instagram:",
        "upload_zip_tooltip": (
            "Il file ZIP deve contenere sottocartelle nominate per data "
            "(es. 2026-03-20, 2026-04-03, ...)"
        ),

        # Sidebar – Theme
        "theme_customization": "🎨 Personalizzazione Tema",
        "general_colors": "Colori Generali",
        "primary_color": "Colore Primario",
        "primary_color_help": "Titoli, bordi e accent",
        "app_background": "Sfondo App",
        "text_color": "Colore Testo",
        "cards_windows": "Schede e Finestre",
        "card_background": "Sfondo Schede",
        "interactive_elements": "Elementi Interattivi",
        "button_background": "Sfondo Bottoni",
        "button_text": "Testo Bottoni",

        # Sidebar – Comparison
        "direct_comparison": "📅 Confronto Diretto",
        "start_t0": "Inizio (T0)",
        "end_t1": "Fine (T1)",
        "status_at": "Stato al:",
        "warning_zero_following": "⚠️ Attenzione: 0 Following rilevati.",

        # Import
        "import_new_data": "📥 Importa nuovi dati",
        "import_help": "Seleziona la cartella con i dati esportati da Instagram",
        "import_success": "Importazione completata!",
        "import_no_changes": (
            "Nessuna modifica rilevata rispetto all'ultimo snapshot."
        ),
        "import_error": "Errore durante l'importazione.",
        "snapshot_label": "Etichetta snapshot (opzionale):",

        # Migration
        "migration_detected": (
            "📂 Rilevati dati legacy ({count} cartelle). "
            "Migrazione automatica in corso..."
        ),
        "migration_complete": (
            "✅ Migrazione completata! {count} snapshot importati."
        ),
        "migration_error": "Errore durante la migrazione.",

        # State Management
        "state_management": "💾 Gestione Stato",
        "download_state": "⬇️ Scarica Stato Attuale",
        "upload_state": "⬆️ Carica Stato (Backup)",
        "upload_state_help": "Carica un file world_state di backup",
        "state_uploaded": "Stato caricato con successo!",

        # Tabs
        "tab_dashboard": "📊 Dashboard",
        "tab_lost": "💔 Persi (T0-T1)",
        "tab_relations": "⚖️ Relazioni",
        "tab_trend": "📈 Trend",
        "tab_timeline": "📅 Cronologia",

        # Dashboard
        "followers": "Followers",
        "following": "Following",
        "new": "Nuovi",
        "lost": "Persi",
        "audience_composition": "Composizione Audience",
        "friends": "Amici",
        "fans": "Fan",
        "not_following_back": "Non ricambiano",
        "theme_tip": (
            "💡 Usa il menu a sinistra per cambiare i colori "
            "dell'applicazione!"
        ),

        # Lost tab
        "lost_between": "Utenti persi tra {d1} e {d2}",
        "no_lost": "Nessun follower perso in questo intervallo!",
        "abandon_date": "Data Abbandono",
        "download_csv": "📥 Scarica CSV",

        # Relations tab
        "not_following_back_title": "👻 Non ricambiano",
        "fans_title": "🌟 Fan",
        "detection_date": "Data Rilevamento",
        "no_users_in_category": "Nessun utente in questa categoria.",

        # Trend tab
        "trend_over_time": "Andamento nel tempo",
        "ratio": "Rapporto Followers/Following",

        # Timeline tab
        "full_timeline": "📅 Cronologia Completa Eventi",
        "search_user": "Cerca utente:",
        "search_placeholder": "es. mario",
        "filter_event": "Filtra evento:",
        "need_two_dates": (
            "Servono almeno 2 date per creare una cronologia."
        ),

        # Event types
        "event_new_follower": "🟢 Nuovo Follower",
        "event_unfollower": "🔴 Unfollower",
        "event_new_following": "🔵 Seguito da te",
        "event_unfollowed": "⚪ Smesso di seguire",

        # Common
        "username": "Username",
        "link": "Link",
        "event": "Evento",
        "date": "Data",
        "processing_timeline": "Elaborazione cronologia completa...",
        "no_data_folder": (
            "Cartella dati non trovata. Inserisci il percorso corretto "
            "nella sidebar."
        ),
        "no_subfolders_found": (
            "Nessuna sottocartella trovata nella directory."
        ),
        "upload_zip_prompt": (
            "Carica un file ZIP dalla sidebar per iniziare l'analisi."
        ),
        "zip_instructions_title": "Come preparare il file ZIP",
        "zip_step_1": (
            "Crea una cartella con sottocartelle nominate per data "
            "(es. `2026-03-20`, `2026-04-03`, ...)"
        ),
        "zip_step_2": (
            "In ogni sottocartella metti i file `followers_1.json` "
            "e `following.json`"
        ),
        "zip_step_3": (
            "Comprimi tutto in un file ZIP e caricalo qui!"
        ),
        "zip_too_large": "File ZIP troppo grande (max 500MB).",
        "zip_invalid_entry": "Voce ZIP non valida rilevata.",
        "json_parse_error": "Errore nel parsing del file JSON: {path}",
        "date_validation_error": (
            "La data di inizio (T0) deve essere precedente alla data "
            "di fine (T1)."
        ),
        "no_state_file": (
            "Nessun dato trovato. Importa i tuoi dati Instagram "
            "per iniziare."
        ),
    },

    "en": {
        # General
        "title": "📸 InstaAnalytics Pro",
        "settings": "Settings",
        "data": "Data",
        "data_source": "Data source:",
        "local_folder": "📁 Local folder",
        "upload_zip": "☁️ Upload ZIP",

        # Sidebar – Folder browsing
        "browse_folder": "📂 Browse folder",
        "parent_folder": "⬆️ Parent folder",
        "subfolders": "Subfolders:",
        "open": "📂 Open",
        "select": "✅ Select",
        "no_subfolders": "No subfolders.",
        "folder_access_denied": "Access denied to this folder.",
        "enter_path": "Or enter the path:",
        "upload_zip_help": "Upload ZIP file with Instagram data:",
        "upload_zip_tooltip": (
            "The ZIP file must contain subfolders named by date "
            "(e.g. 2026-03-20, 2026-04-03, ...)"
        ),

        # Sidebar – Theme
        "theme_customization": "🎨 Theme Customization",
        "general_colors": "General Colors",
        "primary_color": "Primary Color",
        "primary_color_help": "Titles, borders and accents",
        "app_background": "App Background",
        "text_color": "Text Color",
        "cards_windows": "Cards & Windows",
        "card_background": "Card Background",
        "interactive_elements": "Interactive Elements",
        "button_background": "Button Background",
        "button_text": "Button Text",

        # Sidebar – Comparison
        "direct_comparison": "📅 Direct Comparison",
        "start_t0": "Start (T0)",
        "end_t1": "End (T1)",
        "status_at": "Status at:",
        "warning_zero_following": "⚠️ Warning: 0 Following detected.",

        # Import
        "import_new_data": "📥 Import new data",
        "import_help": "Select the folder with exported Instagram data",
        "import_success": "Import completed!",
        "import_no_changes": (
            "No changes detected from the last snapshot."
        ),
        "import_error": "Error during import.",
        "snapshot_label": "Snapshot label (optional):",

        # Migration
        "migration_detected": (
            "📂 Legacy data detected ({count} folders). "
            "Auto-migration in progress..."
        ),
        "migration_complete": (
            "✅ Migration complete! {count} snapshots imported."
        ),
        "migration_error": "Error during migration.",

        # State Management
        "state_management": "💾 State Management",
        "download_state": "⬇️ Download Current State",
        "upload_state": "⬆️ Upload State (Backup)",
        "upload_state_help": "Upload a backup world_state file",
        "state_uploaded": "State successfully uploaded!",

        # Tabs
        "tab_dashboard": "📊 Dashboard",
        "tab_lost": "💔 Lost (T0-T1)",
        "tab_relations": "⚖️ Relations",
        "tab_trend": "📈 Trend",
        "tab_timeline": "📅 Timeline",

        # Dashboard
        "followers": "Followers",
        "following": "Following",
        "new": "New",
        "lost": "Lost",
        "audience_composition": "Audience Composition",
        "friends": "Friends",
        "fans": "Fans",
        "not_following_back": "Not following back",
        "theme_tip": (
            "💡 Use the left menu to change the app colors!"
        ),

        # Lost tab
        "lost_between": "Users lost between {d1} and {d2}",
        "no_lost": "No followers lost in this period!",
        "abandon_date": "Abandon Date",
        "download_csv": "📥 Download CSV",

        # Relations tab
        "not_following_back_title": "👻 Not following back",
        "fans_title": "🌟 Fans",
        "detection_date": "Detection Date",
        "no_users_in_category": "No users in this category.",

        # Trend tab
        "trend_over_time": "Trend over time",
        "ratio": "Followers/Following Ratio",

        # Timeline tab
        "full_timeline": "📅 Full Event Timeline",
        "search_user": "Search user:",
        "search_placeholder": "e.g. mario",
        "filter_event": "Filter event:",
        "need_two_dates": (
            "At least 2 dates are needed to create a timeline."
        ),

        # Event types
        "event_new_follower": "🟢 New Follower",
        "event_unfollower": "🔴 Unfollower",
        "event_new_following": "🔵 You followed",
        "event_unfollowed": "⚪ You unfollowed",

        # Common
        "username": "Username",
        "link": "Link",
        "event": "Event",
        "date": "Date",
        "processing_timeline": "Processing full timeline...",
        "no_data_folder": (
            "Data folder not found. Enter the correct path in the sidebar."
        ),
        "no_subfolders_found": (
            "No subfolders found in the directory."
        ),
        "upload_zip_prompt": (
            "Upload a ZIP file from the sidebar to start the analysis."
        ),
        "zip_instructions_title": "How to prepare the ZIP file",
        "zip_step_1": (
            "Create a folder with subfolders named by date "
            "(e.g. `2026-03-20`, `2026-04-03`, ...)"
        ),
        "zip_step_2": (
            "In each subfolder put the files `followers_1.json` "
            "and `following.json`"
        ),
        "zip_step_3": (
            "Compress everything into a ZIP file and upload it here!"
        ),
        "zip_too_large": "ZIP file too large (max 500MB).",
        "zip_invalid_entry": "Invalid ZIP entry detected.",
        "json_parse_error": "Error parsing JSON file: {path}",
        "date_validation_error": (
            "Start date (T0) must be before end date (T1)."
        ),
        "no_state_file": (
            "No data found. Import your Instagram data to get started."
        ),
    },
}


# ---------------------------------------------------------------------------
# Translation helper
# ---------------------------------------------------------------------------

def t(key: str, **kwargs: object) -> str:
    """Return the translated string for *key* in the active language.

    The active language is read from ``st.session_state['lang']`` and
    defaults to ``'it'`` (Italian).

    Parameters
    ----------
    key:
        The translation key to look up in :data:`STRINGS`.
    **kwargs:
        Optional format arguments.  When provided the translated string
        is passed through :py:meth:`str.format` so that placeholders
        like ``{count}`` or ``{d1}`` are replaced.

    Returns
    -------
    str
        The translated (and optionally formatted) string, or *key*
        itself if no translation is found.
    """
    lang: str = st.session_state.get("lang", "it")
    value: str = STRINGS.get(lang, STRINGS["it"]).get(key, key)
    if kwargs:
        value = value.format(**kwargs)
    return value


# ---------------------------------------------------------------------------
# Language toggle widget
# ---------------------------------------------------------------------------

def render_language_toggle() -> None:
    """Render a compact 🇮🇹 / 🇬🇧 language switcher in the sidebar.

    The button for the currently active language is rendered with a
    visible marker (``●``) so the user can tell which language is
    selected.  Clicking the other button switches the language and
    triggers a full Streamlit rerun.
    """
    current_lang: str = st.session_state.get("lang", "it")
    col_it, col_en = st.columns(2)

    with col_it:
        label_it = "● 🇮🇹" if current_lang == "it" else "🇮🇹"
        if st.button(label_it, key="lang_it", width="stretch"):
            st.session_state["lang"] = "it"
            st.rerun()

    with col_en:
        label_en = "● 🇬🇧" if current_lang == "en" else "🇬🇧"
        if st.button(label_en, key="lang_en", width="stretch"):
            st.session_state["lang"] = "en"
            st.rerun()
