import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import zipfile
import tempfile
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="InstaAnalytics Pro",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR: PERSONALIZZAZIONE ---
st.sidebar.title("⚙️ Impostazioni")

# 1. Configurazione Dati
st.sidebar.subheader("📂 Dati")
import platform
_is_local = platform.system() == "Windows"

if _is_local:
    data_mode = st.sidebar.radio(
        "Sorgente dati:",
        ["📁 Cartella locale", "☁️ Carica ZIP"],
        horizontal=True
    )
else:
    data_mode = "☁️ Carica ZIP"

if data_mode == "📁 Cartella locale":
    # Inizializza il percorso di navigazione
    if 'local_folder' not in st.session_state:
        st.session_state['local_folder'] = r"p:\IG_SCAN\instagram_data"
    if 'browse_path' not in st.session_state:
        st.session_state['browse_path'] = os.path.dirname(st.session_state['local_folder'])

    with st.sidebar.expander("📂 Sfoglia cartella", expanded=False):
        browse = st.session_state['browse_path']

        # Mostra il percorso corrente
        st.caption(f"📍 {browse}")

        # Pulsante per salire di un livello
        parent = os.path.dirname(browse)
        if parent != browse:
            if st.button("⬆️ Cartella superiore"):
                st.session_state['browse_path'] = parent
                st.rerun()

        # Elenca le sottocartelle
        try:
            subdirs = sorted([d for d in os.listdir(browse) if os.path.isdir(os.path.join(browse, d)) and not d.startswith('.')])
        except PermissionError:
            subdirs = []
            st.warning("Accesso negato a questa cartella.")

        if subdirs:
            selected = st.selectbox("Sottocartelle:", subdirs, key="browse_select")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📂 Apri"):
                    st.session_state['browse_path'] = os.path.join(browse, selected)
                    st.rerun()
            with col_b:
                if st.button("✅ Seleziona"):
                    st.session_state['local_folder'] = os.path.join(browse, selected)
                    st.session_state['browse_path'] = os.path.join(browse, selected)
                    st.rerun()
        else:
            st.info("Nessuna sottocartella.")

    root_path = st.sidebar.text_input(
        "Oppure inserisci il percorso:",
        value=st.session_state['local_folder'],
        key="folder_input"
    )
    st.session_state['local_folder'] = root_path
else:
    uploaded_file = st.sidebar.file_uploader(
        "Carica il file ZIP con i dati Instagram:",
        type=["zip"],
        help="Il file ZIP deve contenere sottocartelle nominate per data (es. 2026-03-20, 2026-04-03, ...)"
    )
    if uploaded_file is not None:
        # Estrai solo se è un file nuovo o diverso dal precedente
        if 'zip_temp_dir' not in st.session_state or st.session_state.get('zip_name') != uploaded_file.name:
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue())) as zf:
                zf.extractall(temp_dir)
            # Se lo ZIP contiene una sola cartella radice (es. "instagram_data/"), entra dentro
            contents = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            if len(contents) == 1:
                root_path = os.path.join(temp_dir, contents[0])
            else:
                root_path = temp_dir
            st.session_state['zip_temp_dir'] = root_path
            st.session_state['zip_name'] = uploaded_file.name
        root_path = st.session_state['zip_temp_dir']
    else:
        root_path = None

# 2. Personalizzazione Colori
st.sidebar.markdown("---")
with st.sidebar.expander("🎨 Personalizzazione Tema", expanded=False):
    st.markdown("**Colori Generali**")
    primary_col = st.color_picker("Colore Primario", "#6200EE", help="Titoli, bordi e accent")
    bg_color = st.color_picker("Sfondo App", "#0E1117")
    text_color = st.color_picker("Colore Testo", "#FAFAFA")
    
    st.markdown("**Schede e Finestre**")
    card_bg = st.color_picker("Sfondo Schede", "#262730")
    
    st.markdown("**Elementi Interattivi**")
    btn_bg = st.color_picker("Sfondo Bottoni", "#6200EE")
    btn_txt = st.color_picker("Testo Bottoni", "#FFFFFF")

# --- CUSTOM CSS DINAMICO ---
# Nota: Le parentesi grafe del CSS sono raddoppiate {{ }} per non confondersi con le f-string Python
css_style = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    /* Font generale */
    html, body, [class*="css"]  {{ 
        font-family: 'Roboto', sans-serif; 
        color: {text_color};
    }}
    
    /* Sfondo App */
    .stApp {{
        background-color: {bg_color};
    }}

    /* Colori Titoli */
    h1, h2, h3, h4 {{ 
        color: {primary_col} !important; 
        font-weight: 700; 
    }}

    /* Stile delle Metriche (Card) */
    div[data-testid="stMetric"] {{
        background-color: {card_bg}; 
        border-radius: 10px; 
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        border-left: 5px solid {primary_col};
        color: {text_color};
    }}
    
    /* Label delle metriche */
    div[data-testid="stMetricLabel"] p {{
        color: {text_color} !important;
        opacity: 0.8;
    }}
    
    /* Valore delle metriche */
    div[data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}

    /* Stile delle Tabelle (Card) */
    div[data-testid="stDataFrame"] {{ 
        background-color: {card_bg}; 
        padding: 15px; 
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}

    /* Bottoni (Streamlit buttons) */
    .stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_txt} !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        opacity: 0.9;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}

    /* Tabs attivi */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: {card_bg} !important;
        border-bottom: 2px solid {primary_col} !important;
        color: {primary_col} !important;
    }}
    
    /* Link nelle tabelle */
    a {{
        color: {primary_col} !important;
        text-decoration: none;
    }}
    </style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- FUNZIONI DI CARICAMENTO DATI ---

def get_json_data(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_profiles(json_data):
    """
    Estrae username cercando in tutte le possibili posizioni note dei file Instagram.
    """
    profiles = set()
    if not json_data: return profiles

    # 1. Normalizza il dato in una lista
    data_list = []
    
    if isinstance(json_data, list):
        data_list = json_data
    elif isinstance(json_data, dict):
        # Cerca le chiavi note contenenti la lista
        keys_to_check = ['relationships_following', 'relationships_followers']
        for k in keys_to_check:
            if k in json_data:
                data_list = json_data[k]
                break
        
        # Se non trova le chiavi note, cerca la prima lista valida nel dizionario
        if not data_list:
            for key, val in json_data.items():
                if isinstance(val, list):
                    data_list = val
                    break
    
    # 2. Estrai username da ogni elemento della lista
    for entry in data_list:
        if not isinstance(entry, dict): continue
        
        username = None
        
        # TENTATIVO 1: Cerca in string_list_data -> value (Tipico di followers_1.json)
        if 'string_list_data' in entry:
            for item in entry['string_list_data']:
                if 'value' in item:
                    username = item['value']
                    break
        
        # TENTATIVO 2: Cerca in title (Tipico di following.json nel tuo formato)
        if not username and 'title' in entry:
            username = entry['title']
            
        # TENTATIVO 3: Cerca value diretto (Formati vecchi)
        if not username and 'value' in entry:
            username = entry['value']

        if username:
            profiles.add(username)
            
    return profiles

def load_dataset(folder_path):
    data = {'followers': set(), 'following': set()}
    
    # Mappa nomi file target
    target_files = {
        'followers': ['followers_1.json', 'followers.json'],
        'following': ['following.json']
    }
    
    # Cerca i file ricorsivamente
    found_paths = {}
    
    for root, _, files in os.walk(folder_path):
        # Se abbiamo trovato entrambi, interrompiamo la ricerca
        if 'followers' in found_paths and 'following' in found_paths:
            break
            
        for filename in files:
            # Cerca followers se non ancora trovato
            if 'followers' not in found_paths:
                if filename in target_files['followers']:
                    found_paths['followers'] = os.path.join(root, filename)
            
            # Cerca following se non ancora trovato
            if 'following' not in found_paths:
                if filename in target_files['following']:
                    found_paths['following'] = os.path.join(root, filename)
    
    # Carica i dati dai percorsi trovati
    for key, path in found_paths.items():
        json_raw = get_json_data(path)
        extracted = extract_profiles(json_raw)
        if extracted:
            data[key] = extracted
            
    return data

@st.cache_data
def process_timeline(subfolders):
    events = []
    if not subfolders: return pd.DataFrame()
    
    prev_date = os.path.basename(subfolders[0])
    prev_data = load_dataset(subfolders[0])
    
    for current_path in subfolders[1:]:
        curr_date = os.path.basename(current_path)
        curr_data = load_dataset(current_path)
        
        # Followers
        new_followers = curr_data['followers'] - prev_data['followers']
        lost_followers = prev_data['followers'] - curr_data['followers']
        
        # Following
        new_following = curr_data['following'] - prev_data['following']
        lost_following = prev_data['following'] - curr_data['following']
        
        for u in new_followers:
            events.append({"Data": curr_date, "Username": u, "Evento": "🟢 Nuovo Follower", "Link": f"https://instagram.com/{u}"})
        for u in lost_followers:
            events.append({"Data": curr_date, "Username": u, "Evento": "🔴 Unfollower", "Link": f"https://instagram.com/{u}"})
        for u in new_following:
            events.append({"Data": curr_date, "Username": u, "Evento": "🔵 Seguito da te", "Link": f"https://instagram.com/{u}"})
        for u in lost_following:
            events.append({"Data": curr_date, "Username": u, "Evento": "⚪ Smesso di seguire", "Link": f"https://instagram.com/{u}"})

        prev_data = curr_data
        prev_date = curr_date
        
    return pd.DataFrame(events)

# --- APP LOGIC ---

st.title("📸 InstaAnalytics Pro")

if root_path is None:
    st.info("☁️ Carica un file ZIP dalla sidebar per iniziare l'analisi.")
    st.markdown("""
    ### 📦 Come preparare il file ZIP
    1. Crea una cartella con sottocartelle nominate per data (es. `2026-03-20`, `2026-04-03`, ...)
    2. In ogni sottocartella metti i file `followers_1.json` e `following.json`
    3. Comprimi tutto in un file ZIP e caricalo qui!
    """)
    st.stop()

if not os.path.exists(root_path):
    st.warning("Cartella dati non trovata. Inserisci il percorso corretto nella sidebar.")
    st.stop()

subfolders = sorted([f.path for f in os.scandir(root_path) if f.is_dir()])
if not subfolders:
    st.error("Nessuna sottocartella trovata nella directory.")
    st.stop()

folder_names = [os.path.basename(f) for f in subfolders]

# DATE CONFRONTO
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Confronto Diretto")
c1, c2 = st.sidebar.columns(2)
with c1: d1_name = st.selectbox("Inizio (T0)", folder_names, index=0)
with c2: d2_name = st.selectbox("Fine (T1)", folder_names, index=len(folder_names)-1)

# CARICAMENTO
path_1 = os.path.join(root_path, d1_name)
path_2 = os.path.join(root_path, d2_name)

data_1 = load_dataset(path_1)
data_2 = load_dataset(path_2)

f1, ing1 = data_1['followers'], data_1['following']
f2, ing2 = data_2['followers'], data_2['following']

# CALCOLI
lost = f1 - f2
gained = f2 - f1
nfb = ing2 - f2 
fans = f2 - ing2

# DEBUG INFO
st.sidebar.markdown("---")
st.sidebar.caption(f"Stato al: {d2_name}")
st.sidebar.text(f"Followers: {len(f2)}")
st.sidebar.text(f"Following: {len(ing2)}")

if len(ing2) == 0:
    st.sidebar.error("⚠️ Attenzione: 0 Following rilevati.")

# --- ANALISI CRONOLOGIA GLOBALE (per date precise) ---
with st.spinner("Elaborazione cronologia completa..."):
    df_time = process_timeline(subfolders)

# --- TABS E VISUALIZZAZIONE ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💔 Persi (T0-T1)", "⚖️ Relazioni", "📈 Trend", "📅 Cronologia"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Followers", len(f2), len(f2)-len(f1))
    col2.metric("Following", len(ing2), len(ing2)-len(ing1))
    col3.metric("Nuovi", len(gained))
    col4.metric("Persi", len(lost), delta_color="inverse")
    
    st.markdown("---")
    cp, ci = st.columns([2,1])
    with cp:
        st.markdown("#### Composizione Audience")
        df_pie = pd.DataFrame({
            'Tipo': ['Amici', 'Fan', 'Non ricambiano'],
            'Valore': [len(f2 & ing2), len(fans), len(nfb)]
        })
        # I colori del grafico sono gestiti da Plotly, ma usiamo il layout trasparente per adattarsi
        fig = px.pie(df_pie, values='Valore', names='Tipo', hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')
    with ci:
        st.info("💡 Usa il menu a sinistra per cambiare i colori dell'applicazione!")

with tab2:
    st.subheader(f"Utenti persi tra {d1_name} e {d2_name}")
    if lost:
        df = pd.DataFrame(list(lost), columns=["Username"])
        
        # Recupera la data esatta dell'evento "Unfollower" dalla timeline
        if not df_time.empty:
            # Filtra eventi Unfollower nel range temporale selezionato (d1 < data <= d2)
            # Nota: Consideriamo string comparison per le date basata sull'ordine delle cartelle
            mask_lost = (df_time["Evento"] == "🔴 Unfollower") & \
                        (df_time["Data"] > d1_name) & \
                        (df_time["Data"] <= d2_name)
            df_dates = df_time[mask_lost][["Username", "Data"]]
            # Merge per aggiungere la data
            df = df.merge(df_dates, on="Username", how="left")
            df["Data"] = df["Data"].fillna(d2_name) # Fallback alla data finale se non trovato
            df = df.rename(columns={"Data": "Data Abbandono"})
        else:
            df["Data Abbandono"] = d2_name

        df['Link'] = "https://instagram.com/" + df['Username']
        st.dataframe(df, column_config={"Link": st.column_config.LinkColumn()}, hide_index=True, width="stretch")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", csv, "unfollowers.csv", "text/csv")
    else:
        st.success("Nessun follower perso in questo intervallo!")

with tab3:
    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("👻 Non ricambiano")
        if nfb:
            df = pd.DataFrame(list(nfb), columns=["Username"])
            df['Data Rilevamento'] = d2_name
            df['Link'] = "https://instagram.com/" + df['Username']
            st.dataframe(df, column_config={"Link": st.column_config.LinkColumn()}, hide_index=True, width="stretch")
    with c_b:
        st.subheader("🌟 Fan")
        if fans:
            df = pd.DataFrame(list(fans), columns=["Username"])
            df['Data Rilevamento'] = d2_name
            df['Link'] = "https://instagram.com/" + df['Username']
            st.dataframe(df, column_config={"Link": st.column_config.LinkColumn()}, hide_index=True, width="stretch")

with tab4:
    st.subheader("Andamento nel tempo")
    trend = []
    for f in subfolders:
        d = load_dataset(f)
        trend.append({"Data": os.path.basename(f), "Followers": len(d['followers']), "Following": len(d['following'])})
    
    fig = px.line(pd.DataFrame(trend), x="Data", y=["Followers", "Following"], markers=True)
    fig.update_layout(plot_bgcolor=card_bg, paper_bgcolor=card_bg, font_color=text_color)
    st.plotly_chart(fig, width='stretch')

with tab5:
    st.subheader("📅 Cronologia Completa Eventi")
    
    # df_time è già calcolato sopra
    
    if not df_time.empty:
        col_s, col_f = st.columns(2)
        search = col_s.text_input("Cerca utente:", placeholder="es. mario")
        ev_types = col_f.multiselect("Filtra evento:", df_time["Evento"].unique(), default=df_time["Evento"].unique())
        
        mask = df_time["Evento"].isin(ev_types)
        if search:
            mask = mask & df_time["Username"].str.contains(search, case=False)
            
        st.dataframe(
            df_time[mask].sort_values(by="Data", ascending=False),
            column_config={"Link": st.column_config.LinkColumn()},
            hide_index=True,
            width="stretch"
        )
    else:
        st.info("Servono almeno 2 date per creare una cronologia.")