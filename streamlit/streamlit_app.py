"""
Churn Radar — interface Streamlit pour l'API FastAPI de prédiction de churn.

- Onglet "Prédiction"  → un client, formulaire + jauge de probabilité
- Onglet "Batch"       → upload CSV, prédiction en masse
- Onglet "Modèle"      → métriques du modèle en prod (GET /model-info)

Pré-requis : l'API FastAPI (app.py) doit tourner à côté, ex. `uvicorn app:app --reload`.
"""

# ╔════════════════════════════════════════════════════════════╗
# ║ 🚚 IMPORTS
# ╚════════════════════════════════════════════════════════════╝
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
DEFAULT_API_URL = "https://churn-baseline-916856991986.europe-west1.run.app"


def env_file_value(key: str) -> str | None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return None

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip("\"'")

    return None


def default_api_url() -> str:
    """
    Ordre de priorité : st.secrets (Streamlit Cloud) > variable d'env >
    .env local > URL Cloud Run par défaut.
    """
    try:
        return st.secrets["API_URL"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("API_URL") or env_file_value("API_URL") or DEFAULT_API_URL


# ╔════════════════════════════════════════════════════════════╗
# ║ ⚙️ CONFIG
# ╚════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="Churn Radar",
    page_icon="📡",
    layout="wide",
)

ACCENT_SAFE = "#34d399"  # vert émeraude — client fidèle
ACCENT_WATCH = "#fbbf24"  # ambre — à surveiller
ACCENT_RISK = "#fb7185"  # rose/rouge — risque de churn
ACCENT_BRAND = "#38bdf8"  # cyan — boutons, éléments interactifs

# Dataset brut utilisé dans le notebook (../data/... vu depuis le notebook,
# donc data/... vu depuis la racine du projet). Ajuste si ton arborescence diffère.
# DATASET_PATH = Path("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
# Toute prédiction (unitaire ou batch) doit envoyer exactement ces clés.
REQUIRED_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
]


# ╔════════════════════════════════════════════════════════════╗
# ║ 🎨 STYLE — glassmorphism
# ╚════════════════════════════════════════════════════════════╝
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

        /* Fond animé : dégradé sombre qui respire lentement */
        .stApp {
            background: radial-gradient(circle at 15% 20%, #1b2440 0%, transparent 45%),
                        radial-gradient(circle at 85% 80%, #2a1b3d 0%, transparent 45%),
                        #0b0f19;
            background-size: 200% 200%;
            animation: drift 18s ease-in-out infinite;
        }
        @keyframes drift {
            0%   { background-position: 0% 0%; }
            50%  { background-position: 100% 100%; }
            100% { background-position: 0% 0%; }
        }

        section[data-testid="stSidebar"] {
            background: rgba(11, 15, 25, 0.9);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        /* Carte en verre réutilisable — appliquée via st.markdown(..., unsafe_allow_html=True) */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 18px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
        }
        .glass-card h3 { margin-top: 0; color: #e5e7eb; }

        .risk-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.95rem;
        }
        .pulse-dot {
            width: 10px; height: 10px; border-radius: 50%;
            animation: pulse 1.6s ease-in-out infinite;
        }
        @keyframes pulse {
            0%   { box-shadow: 0 0 0 0 rgba(251, 113, 133, 0.55); }
            70%  { box-shadow: 0 0 0 10px rgba(251, 113, 133, 0); }
            100% { box-shadow: 0 0 0 0 rgba(251, 113, 133, 0); }
        }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1.5rem;
        }

        .stButton > button, .stFormSubmitButton > button {
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            color: #0b0f19;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.55rem 1.4rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35);
        }

        /* On ne cache PAS le header en entier : la flèche pour ré-ouvrir
        la sidebar une fois repliée vit dedans. On cache juste le menu
        hamburger et le footer, et on rend le header transparent. */
        #MainMenu, footer { visibility: hidden; }
        header[data-testid="stHeader"] { background: transparent; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def glass_card(title: str, body_html: str):
    """Affiche une carte en verre avec un titre et du HTML libre à l'intérieur."""
    st.markdown(
        f'<div class="glass-card"><h3>{title}</h3>{body_html}</div>',
        unsafe_allow_html=True,
    )


# ╔════════════════════════════════════════════════════════════╗
# ║ 🔐 SESSION STATE
# ╚════════════════════════════════════════════════════════════╝
def init_session_state():
    defaults = {
        "base_url": default_api_url(),
        "access_token": None,
        "refresh_token": None,
        "username": None,
        "authenticated": False,
        "demo_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout():
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.username = None
    st.session_state.authenticated = False


# ╔════════════════════════════════════════════════════════════╗
# ║ 🌐 APPELS API
# ╚════════════════════════════════════════════════════════════╝
def api_login(base_url: str, username: str, password: str) -> dict:
    """POST /login attend un form-data (OAuth2PasswordRequestForm), pas du JSON."""
    resp = requests.post(
        f"{base_url}/login",
        data={"username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def check_demo_mode(base_url: str) -> bool:
    """
    Interroge GET /health pour savoir si l'API tourne en DEMO_MODE.
    Si l'API est injoignable, on part du principe que l'auth est requise
    (fail-safe : mieux vaut demander un login inutile que d'exposer
    l'app par erreur).
    """
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        resp.raise_for_status()
        return bool(resp.json().get("demo_mode", False))
    except requests.exceptions.RequestException:
        return False


def authenticated_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """
    Fait un appel API avec le token courant. Si l'API renvoie 401 (token
    expiré), tente un refresh silencieux via /refresh puis rejoue l'appel
    une seule fois. Si le refresh échoue aussi, on déconnecte l'utilisateur.
    """
    url = f"{st.session_state.base_url}{endpoint}"
    headers = kwargs.pop("headers", {})
    if st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"

    resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)

    if resp.status_code == 401 and st.session_state.refresh_token:
        refresh_resp = requests.post(
            f"{st.session_state.base_url}/refresh",
            json={"refresh_token": st.session_state.refresh_token},
            timeout=10,
        )
        if refresh_resp.ok:
            tokens = refresh_resp.json()
            st.session_state.access_token = tokens["access_token"]
            st.session_state.refresh_token = tokens["refresh_token"]
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
            resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        else:
            logout()

    return resp


def response_json(resp: requests.Response, label: str):
    try:
        return resp.json()
    except requests.exceptions.JSONDecodeError:
        content_type = resp.headers.get("content-type", "inconnu")
        preview = resp.text.strip().replace("\n", " ")[:240]
        st.error(
            f"{label} a répondu avec du contenu non JSON "
            f"(status {resp.status_code}, content-type {content_type})."
        )
        if "Placeholder | Cloud Run" in resp.text:
            st.warning(
                "Cloud Run sert encore la page placeholder : le backend FastAPI "
                "n'est pas déployé correctement sur ce service."
            )
        elif preview:
            st.code(preview)
        return None


# ╔════════════════════════════════════════════════════════════╗
# ║ 🧭 SIDEBAR — connexion
# ╚════════════════════════════════════════════════════════════╝
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Connexion API")
        st.caption(f"API : `{st.session_state.base_url}`")

        if st.session_state.demo_mode:
            # En démo publique : l'URL est fixée par le déployeur, pas
            # modifiable par le visiteur (évite qu'il pointe l'app vers
            # une API tierce de son choix).
            st.markdown(
                f'<div class="risk-badge" style="background: rgba(56,189,248,0.15); '
                f'color: {ACCENT_BRAND};">🌐 Mode démo — accès libre</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "L'authentification est désactivée sur cette instance de démonstration."
            )
            return

        if st.session_state.authenticated:
            st.markdown(
                f'<div class="risk-badge" style="background: rgba(52,211,153,0.15); '
                f'color: {ACCENT_SAFE};">🟢 Connecté — {st.session_state.username}</div>',
                unsafe_allow_html=True,
            )
            st.button("Se déconnecter", on_click=logout, use_container_width=True)
        else:
            with st.form("login_form"):
                username = st.text_input("Utilisateur", value="admin")
                password = st.text_input("Mot de passe", type="password")
                submitted = st.form_submit_button(
                    "Se connecter", use_container_width=True
                )

            if submitted:
                try:
                    tokens = api_login(
                        str(st.session_state.base_url), username, password
                    )
                    st.session_state.access_token = tokens["access_token"]
                    st.session_state.refresh_token = tokens["refresh_token"]
                    st.session_state.username = username
                    st.session_state.authenticated = True
                    st.rerun()
                except requests.exceptions.HTTPError:
                    st.error("Identifiants invalides.")
                except requests.exceptions.RequestException:
                    st.error(
                        f"Impossible de joindre l'API sur {st.session_state.base_url}."
                    )


# ╔════════════════════════════════════════════════════════════╗
# ║ 📈 JAUGE DE PROBABILITÉ
# ╚════════════════════════════════════════════════════════════╝
def build_gauge(probability: float, is_churn: bool) -> go.Figure:
    color = ACCENT_RISK if is_churn else ACCENT_SAFE

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(probability * 100, 1),
            number={"suffix": "%", "font": {"size": 44, "color": "white"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "rgba(255,255,255,0.4)"},
                "bar": {"color": color, "thickness": 0.3},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(52,211,153,0.18)"},
                    {"range": [40, 70], "color": "rgba(251,191,36,0.18)"},
                    {"range": [70, 100], "color": "rgba(251,113,133,0.18)"},
                ],
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        height=260,
        margin=dict(l=20, r=20, t=30, b=10),
    )
    return fig


def render_verdict(prediction: int, probability: float):
    is_churn = prediction == 1

    if is_churn and probability >= 0.7:
        label, color, advice = (
            "🔴 Risque élevé de départ",
            ACCENT_RISK,
            "Contact prioritaire recommandé : offre de rétention ou appel commercial.",
        )
    elif is_churn:
        label, color, advice = (
            "🟠 Signal de churn détecté",
            ACCENT_WATCH,
            "À surveiller — un geste commercial léger peut suffire.",
        )
    else:
        label, color, advice = (
            "🟢 Client stable",
            ACCENT_SAFE,
            "Rien à signaler pour l'instant.",
        )

    st.markdown(
        f"""
        <div class="risk-badge" style="background: {color}22; color: {color};">
            <span class="pulse-dot" style="background: {color};"></span>{label}
        </div>
        <p style="color:#9ca3af; margin-top:0.6rem;">{advice}</p>
        """,
        unsafe_allow_html=True,
    )

    if is_churn:
        st.toast("Client à risque détecté", icon="⚠️")
    else:
        st.balloons()


# ╔════════════════════════════════════════════════════════════╗
# ║ 🔮 ONGLET — PRÉDICTION UNITAIRE
# ╚════════════════════════════════════════════════════════════╝
def render_prediction_tab():
    st.markdown("#### Profil du client")

    with st.form("predict_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**👤 Profil**")
            gender = st.selectbox("Genre", ["Female", "Male"])
            senior = st.selectbox("Senior", ["Non", "Oui"])
            partner = st.selectbox("En couple", ["Yes", "No"])
            dependents = st.selectbox("Personnes à charge", ["Yes", "No"])
            tenure = st.slider("Ancienneté (mois)", 0, 72, 12)

        with col2:
            st.markdown("**📡 Services**")
            phone = st.selectbox("Téléphone", ["Yes", "No"])
            multiple_lines = st.selectbox(
                "Lignes multiples", ["No", "Yes", "No phone service"]
            )
            internet = st.selectbox("Internet", ["DSL", "Fiber optic", "No"])
            online_security = st.selectbox(
                "Sécurité en ligne", ["No", "Yes", "No internet service"]
            )
            online_backup = st.selectbox(
                "Sauvegarde en ligne", ["No", "Yes", "No internet service"]
            )
            device_protection = st.selectbox(
                "Protection appareil", ["No", "Yes", "No internet service"]
            )
            tech_support = st.selectbox(
                "Support technique", ["No", "Yes", "No internet service"]
            )
            streaming_tv = st.selectbox(
                "Streaming TV", ["No", "Yes", "No internet service"]
            )
            streaming_movies = st.selectbox(
                "Streaming films", ["No", "Yes", "No internet service"]
            )

        with col3:
            st.markdown("**💳 Contrat & facturation**")
            contract = st.selectbox(
                "Contrat", ["Month-to-month", "One year", "Two year"]
            )
            paperless = st.selectbox("Facture dématérialisée", ["Yes", "No"])
            payment = st.selectbox(
                "Moyen de paiement",
                [
                    "Electronic check",
                    "Mailed check",
                    "Bank transfer (automatic)",
                    "Credit card (automatic)",
                ],
            )
            monthly_charges = st.number_input(
                "Facture mensuelle (€)",
                min_value=0.0,
                max_value=200.0,
                value=65.0,
                step=0.5,
            )

        submitted = st.form_submit_button(
            "🔍 Lancer la prédiction", use_container_width=True
        )

    if not submitted:
        return

    payload = {
        "gender": gender,
        "SeniorCitizen": 1 if senior == "Oui" else 0,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone,
        "MultipleLines": multiple_lines,
        "InternetService": internet,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
        "MonthlyCharges": monthly_charges,
    }

    try:
        resp = authenticated_request("POST", "/predict", json=payload)
    except requests.exceptions.RequestException:
        st.error(f"Impossible de joindre l'API sur {st.session_state.base_url}.")
        return

    if resp.status_code == 401:
        st.error("L'API demande une authentification. Active DEMO_MODE=true côté API pour un accès public.")
        return
    if not resp.ok:
        st.error(f"Erreur API ({resp.status_code}) : {resp.text}")
        return

    result = response_json(resp, "L'API /predict")
    if result is None:
        return

    st.markdown("---")
    col_gauge, col_verdict = st.columns([1, 1])
    with col_gauge:
        st.plotly_chart(
            build_gauge(result["probability"], bool(result["churn"])),
            use_container_width=True,
        )
    with col_verdict:
        st.markdown("<br>", unsafe_allow_html=True)
        render_verdict(result["prediction"], result["probability"])


# ╔════════════════════════════════════════════════════════════╗
# ║ 📦 ONGLET — BATCH
# ╚════════════════════════════════════════════════════════════╝
def render_batch_tab():
    st.markdown("#### Prédiction en masse")
    st.caption(
        "Le CSV doit contenir exactement les colonnes attendues par l'API "
        "(voir `ChurnInput` dans `schemas.py`)."
    )

    uploaded = st.file_uploader("Fichier CSV clients", type="csv")
    if uploaded is None:
        return

    df = pd.read_csv(uploaded)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Colonnes manquantes dans le CSV : {missing}")
        return

    st.dataframe(df.head(), use_container_width=True)

    if not st.button("🚀 Lancer les prédictions batch"):
        return

    df["SeniorCitizen"] = df["SeniorCitizen"].astype(int)
    df["MonthlyCharges"] = df["MonthlyCharges"].astype(float)

    payload = {"data": df[REQUIRED_COLUMNS].to_dict(orient="records")}

    try:
        resp = authenticated_request("POST", "/predict-batch", json=payload)
    except requests.exceptions.RequestException:
        st.error(f"Impossible de joindre l'API sur {st.session_state.base_url}.")
        return

    if resp.status_code == 401:
        st.error("L'API demande une authentification. Active DEMO_MODE=true côté API pour un accès public.")
        return
    if not resp.ok:
        st.error(f"Erreur API ({resp.status_code}) : {resp.text}")
        return

    results = response_json(resp, "L'API /predict-batch")
    if results is None:
        return

    # ⚠️ L'API /predict-batch ne renvoie pas d'identifiant client : on
    # suppose que l'ordre des résultats suit l'ordre des lignes envoyées.
    # Si tu ajoutes un jour un customerID au CSV, pense à le faire remonter
    # côté API pour fiabiliser ce merge.
    df["Prédiction"] = [r["label"] for r in results]
    df["Probabilité"] = [r["probability"] for r in results]

    def highlight_risk(row):
        color = ACCENT_RISK if row["Prédiction"] == "Churn" else ACCENT_SAFE
        return [f"background-color: {color}22"] * len(row)

    st.dataframe(df.style.apply(highlight_risk, axis=1), use_container_width=True)

    n_risk = sum(1 for r in results if r["churn"])
    st.markdown(
        f'<div class="glass-card"><h3>Résumé</h3>'
        f'<p style="color:#e5e7eb;">{n_risk} client(s) à risque sur {len(results)}</p></div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        "⬇️ Télécharger les résultats",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="predictions_churn.csv",
        mime="text/csv",
    )


# ╔════════════════════════════════════════════════════════════╗
# ║ 🔍 ONGLET — DATASET (avant / après nettoyage + visus)
# ╚════════════════════════════════════════════════════════════╝
@st.cache_data
def load_raw_dataset(path: str) -> pd.DataFrame:
    return pd.read_csv(path)



@st.cache_data
def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Conversion de TotalCharges en numérique
    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce",
    )

    # Suppression des valeurs manquantes
    df = df.dropna(subset=["TotalCharges"])

    # Suppression de l'identifiant client
    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])

    return df


def dataset_expanders(df: pd.DataFrame):
    """Les 5 mêmes blocs qu'inspect_df() dans le notebook, repliés par défaut."""
    with st.expander("📏 Dimensions"):
        st.write(f"{df.shape[0]} lignes × {df.shape[1]} colonnes")

    with st.expander("🧬 Types de données"):
        st.dataframe(df.dtypes.astype(str).to_frame("dtype"), use_container_width=True)

    with st.expander("⚠️ Valeurs manquantes"):
        missing = pd.DataFrame(
            {
                "n_missing": df.isna().sum(),
                "pct_missing": (df.isna().mean() * 100).round(2),
            }
        )
        missing = missing[missing["n_missing"] > 0].sort_values(
            "n_missing", ascending=False
        )
        if missing.empty:
            st.write("Aucune valeur manquante détectée.")
        else:
            st.dataframe(missing, use_container_width=True)

    with st.expander("🔂 Doublons"):
        st.write(f"{df.duplicated().sum()} ligne(s) dupliquée(s)")

    with st.expander("👀 Aperçu (5 lignes)"):
        st.dataframe(df.head(5), use_container_width=True)


def dark_fig(figsize):
    """Crée une figure matplotlib au fond transparent, lisible sur fond sombre."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for spine in ax.spines.values():
        spine.set_color("#374151")
    ax.tick_params(colors="#9ca3af")
    ax.xaxis.label.set_color("#e5e7eb")
    ax.yaxis.label.set_color("#e5e7eb")
    ax.title.set_color("#e5e7eb")
    return fig, ax


def plot_correlation(df: pd.DataFrame):
    fig, ax = dark_fig((5, 4))
    sns.heatmap(
        df.select_dtypes(include="number").corr(),
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True,
        ax=ax,
    )
    ax.set_title("Corrélations entre variables numériques")
    return fig


def plot_pairplot(df: pd.DataFrame):
    g = sns.pairplot(
        df,
        vars=["tenure", "MonthlyCharges", "TotalCharges"],
        hue="Churn",
        palette={"No": ACCENT_SAFE, "Yes": ACCENT_RISK},
        plot_kws={"alpha": 0.5, "s": 15},
    )
    g.figure.patch.set_alpha(0)
    for ax in g.axes.flat:
        if ax is not None:
            ax.set_facecolor("none")
            ax.tick_params(colors="#9ca3af")
            ax.xaxis.label.set_color("#e5e7eb")
            ax.yaxis.label.set_color("#e5e7eb")
    return g.figure


def plot_boxplot(df: pd.DataFrame, col: str):
    fig, ax = dark_fig((4.5, 3))
    sns.boxplot(
        data=df,
        x="Churn",
        y=col,
        ax=ax,
        palette={"No": ACCENT_SAFE, "Yes": ACCENT_RISK},
    )
    ax.set_title(f"{col} selon le churn")
    return fig


def render_dataset_tab():
    if not DATASET_PATH.exists():
        st.error(f"Dataset du projet introuvable : {DATASET_PATH}")
        return

    df_raw = load_raw_dataset(str(DATASET_PATH))

    # Copie uniquement pour les visualisations
    df_viz = df_raw.copy()

    # TotalCharges est stocké en object dans le CSV brut.
    # On le convertit seulement pour permettre les graphiques.
    df_viz["TotalCharges"] = pd.to_numeric(
        df_viz["TotalCharges"],
        errors="coerce",
    )

    st.markdown("---")
    st.markdown("#### Visualisations exploratoires (avant cleaning)")
    st.caption(
        "Les visualisations utilisent les données brutes. "
        "`TotalCharges` est uniquement convertie en numérique pour permettre les graphiques."
    )

    if st.button("📊 Générer les visualisations"):

        # ── Corrélations ─────────────────────────────
        st.markdown("##### Matrice de corrélation")

        col_left, col_chart, col_right = st.columns([1, 2, 1])

        with col_chart:
            fig = plot_correlation(df_viz)
            st.pyplot(fig, use_container_width=True)

        plt.close(fig)

        # ── Pairplot ─────────────────────────────────
        st.markdown("##### Relations entre variables")

        col_left, col_chart, col_right = st.columns([1, 2.5, 1])

        with col_chart:
            fig = plot_pairplot(df_viz)
            st.pyplot(fig, use_container_width=True)

        plt.close(fig)

        # ── Boxplots ─────────────────────────────────
        st.markdown("##### Distribution selon le churn")

        cols = st.columns(3)

        for container, feature in zip(
            cols,
            ["tenure", "MonthlyCharges", "TotalCharges"],
        ):
            with container:
                fig = plot_boxplot(df_viz, feature)
                st.pyplot(fig, use_container_width=True)

            plt.close(fig)


# ╔════════════════════════════════════════════════════════════╗
# ║ 📊 ONGLET — MODÈLE
# ╚════════════════════════════════════════════════════════════╝
def render_model_tab():
    try:
        resp = authenticated_request("GET", "/model-info")
    except requests.exceptions.RequestException:
        st.error(f"Impossible de joindre l'API sur {st.session_state.base_url}.")
        return

    if not resp.ok:
        st.error(f"Erreur API ({resp.status_code}) : {resp.text}")
        return

    info = response_json(resp, "L'API /model-info")
    if info is None:
        return

    glass_card(
        info["model_name"],
        f'<p style="color:#9ca3af;">{info["model_description"]}<br>'
        f'Type : {info["model_type"]} — {info["model_length"]} lignes d\'entraînement</p>',
    )

    metrics = {
        "Recall": info["model_recall"],
        "Precision": info["model_precision"],
        "Accuracy": info["model_accuracy"],
        "F1": info["model_f1"],
        "ROC AUC": info["model_roc_auc"],
    }

    cols = st.columns(len(metrics))
    for col, (name, value) in zip(cols, metrics.items()):
        with col:
            st.markdown(
                f'<div class="glass-card" style="text-align:center;">'
                f'<p style="color:#9ca3af; margin-bottom:0.2rem;">{name}</p>'
                f'<p style="font-size:1.8rem; font-weight:700; color:{ACCENT_BRAND}; margin:0;">'
                f"{value:.0%}</p></div>",
                unsafe_allow_html=True,
            )

    fig = go.Figure(
        go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker_color=ACCENT_BRAND,
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        yaxis={"range": [0, 1], "gridcolor": "rgba(255,255,255,0.08)"},
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=False)


# ╔════════════════════════════════════════════════════════════╗
# ║ 🚀 MAIN
# ╚════════════════════════════════════════════════════════════╝
def main():
    init_session_state()
    inject_css()

    st.session_state.demo_mode = check_demo_mode(str(st.session_state.base_url))
    if st.session_state.demo_mode:
        st.session_state.authenticated = True

    render_sidebar()

    st.markdown(
        '<h1 style="color:white;">📡 Churn Radar</h1>'
        '<p style="color:#9ca3af; margin-top:-0.8rem;">'
        "Détection de signaux de désabonnement en temps réel</p>",
        unsafe_allow_html=True,
    )

    tab_predict, tab_batch, tab_dataset, tab_model = st.tabs(
        ["🔮 Prédiction", "📦 Batch", "🔍 Dataset", "📊 Modèle"]
    )
    with tab_predict:
        render_prediction_tab()
    with tab_batch:
        render_batch_tab()
    with tab_dataset:
        render_dataset_tab()
    with tab_model:
        render_model_tab()


if __name__ == "__main__":
    main()
