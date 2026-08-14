"""
DataForge
Main Streamlit Application
"""

import os
import streamlit as st


# ==========================================================
# DIRECTORIES
# ==========================================================

ROOT = os.path.dirname(__file__)

REPORTS_DIR = os.path.join(ROOT, "reports")
MODELS_DIR = os.path.join(ROOT, "models")
ASSETS_DIR = os.path.join(ROOT, "assets")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="DataForge",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# SESSION STATE
# ==========================================================

defaults = {

    "df_raw": None,

    "df_clean": None,

    "trained_models": {},

    "metrics": {},

    "activity_log": {

        "cleaning": [],

        "visualizations": [],

        "models": []

    }

}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("DataForge")

page = st.sidebar.radio(

    "Navigation",

    [

        "Dashboard",

        "Home",

        "Data Cleaning",

        "Visualization",

        "Model Training",

        "Registry",

        "Deployment",

        "Reports",

        "Export"

    ]

)
