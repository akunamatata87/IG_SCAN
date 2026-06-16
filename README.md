# InstaAnalytics Pro

A robust, multi-platform Streamlit application designed for analyzing and tracking your Instagram follower and following data over time.

## 🚀 Features

- **Multi-Platform Data Sources**: Run the app locally via folder scanning or upload your data as a `.zip` archive.
- **Smart Data Persistence**: All snapshots and historical analysis are managed efficiently via a lightweight `world_state.json` file. No need to rescan gigabytes of historical data.
- **Auto Migration**: Automatically scans and migrates legacy data folders into the new, optimized persistence format.
- **Bilingual Interface**: Seamlessly switch between Italian (IT) and English (EN) directly from the header.
- **Rich Dashboards**: Includes 5 detailed tabs (Dashboard, Lost Followers, Relations, Trends, Timeline) complete with interactive Plotly visualizations and CSV exports.

## 🛠 Project Structure

- `app.py`: The main entry point and UI orchestrator.
- `state_manager.py`: Handles state persistence, data migration, diff tracking, and snapshot loading/saving.
- `data_loader.py`: Responsible for reading and extracting followers/following profiles from raw JSON exports.
- `i18n.py`: Internationalization module housing all IT/EN string definitions and toggle logic.
- `ui/`: Contains all Streamlit rendering components (`css.py`, `sidebar.py`, `dashboard.py`, `lost_tab.py`, `relations_tab.py`, `trend_tab.py`, `timeline_tab.py`).

## 🖥 Installation and Running (PC)

Ensure you have Python installed, then run:

```bash
pip install -r requirements.txt
```

To run the application easily, simply use the custom launcher (if generated), or start the Streamlit app manually:

```bash
python -m streamlit run app.py
```

## ☁️ Running on Cloud / Android

For non-PC environments, the folder-browsing component is hidden. Instead, use the sidebar to upload a `.zip` archive containing your Instagram JSON exports. Ensure your archive contains dated folders (e.g. `2026-03-20/`), each containing the corresponding `followers_*.json` and `following.json` files.
