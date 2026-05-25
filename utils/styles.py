import streamlit as st
from config.settings import CURRENCY

def inject_fitgenuss_styles():
    """
    Inyecta estilos CSS altamente personalizados en la aplicación Streamlit 
    para lograr una experiencia de usuario (UX) sumamente fluida y una estética premium.
    Combina elementos de diseño moderno como bordes redondeados, sombras sutiles
    y colores de marca (Verde Matcha y Rosa Dulce).
    """
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Marcellus&display=swap');

    :root {
        --fg-rose: #C77B7B;
        --fg-rose-deep: #AA5E5E;
        --fg-olive: #6F6C3A;
        --fg-olive-soft: #8D8952;
        --fg-cream: #FCF8F2;
        --fg-paper: #FFFDF9;
        --fg-ink: #1F1D1B;
        --fg-muted: #6F6A63;
        --fg-border: #E8DDD1;
    }

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Manrope', sans-serif;
        color: var(--fg-ink);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Marcellus', serif;
        color: var(--fg-ink);
        letter-spacing: 0.02em;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}

    .stApp {
        background: radial-gradient(circle at 15% 8%, #fff8f5 0%, #fcf8f2 38%, #f7f1e8 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f6efe5 0%, #f8f3eb 100%);
        border-right: 1px solid var(--fg-border);
        padding-top: 1rem;
    }

    .kpi-card {
        background: var(--fg-paper);
        border: 1px solid var(--fg-border);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 12px 24px rgba(31, 29, 27, 0.06);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 30px rgba(31, 29, 27, 0.1);
        border-color: #dcb7a3;
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--fg-rose), var(--fg-olive));
    }

    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--fg-muted);
        text-transform: uppercase;
        margin-bottom: 10px;
        letter-spacing: 0.08em;
    }

    .kpi-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: var(--fg-ink);
        line-height: 1;
    }

    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    .badge-success { background-color: #edf5e8; color: #466235; }
    .badge-warning { background-color: #f7f0d8; color: #886c1b; }
    .badge-danger { background-color: #fce9e9; color: #9a4646; }

    .fitgenuss-banner {
        background: linear-gradient(135deg, #7a4a4a 0%, #b26a6a 45%, #7a743f 100%);
        color: white;
        padding: 2.2rem;
        border-radius: 22px;
        box-shadow: 0 14px 28px rgba(95, 66, 66, 0.25);
        margin-bottom: 2rem;
        position: relative;
    }

    .fitgenuss-banner h1 {
        color: #fff;
        margin-top: 0;
        margin-bottom: 0.7rem;
        font-size: 2.4rem;
        font-weight: 700;
    }

    .fitgenuss-banner p {
        color: rgba(255, 255, 255, 0.92);
        font-size: 1.05rem;
        max-width: 680px;
        margin-bottom: 0;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: linear-gradient(90deg, var(--fg-rose), var(--fg-rose-deep));
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.55rem 1.5rem;
        transition: all 0.2s;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 16px rgba(170, 94, 94, 0.25);
    }

    input, select, textarea {
        border-radius: 10px !important;
        border-color: var(--fg-border) !important;
    }

    input:focus, textarea:focus, select:focus {
        border-color: var(--fg-rose) !important;
        box-shadow: 0 0 0 1px var(--fg-rose) !important;
    }

    .fg-login-intro {
        text-align: center;
        margin: 0.2rem auto 1.2rem auto;
    }

    .fg-login-chip {
        display: inline-block;
        border: 1px solid #e6cbc5;
        color: var(--fg-rose-deep);
        background: #fff6f4;
        border-radius: 999px;
        padding: 0.3rem 0.9rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.8rem;
    }

    .fg-login-title {
        font-family: 'Marcellus', serif;
        color: var(--fg-ink);
        font-size: 2.2rem;
        margin: 0;
    }

    .fg-login-subtitle {
        color: var(--fg-muted);
        margin-top: 0.4rem;
        margin-bottom: 1rem;
        font-size: 0.96rem;
    }

    .fg-login-features {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        flex-wrap: wrap;
    }

    .fg-login-features span {
        border: 1px solid var(--fg-border);
        background: #fff;
        color: var(--fg-olive);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .login-container {
        max-width: 460px;
        margin: 1.2rem auto 2rem auto;
        padding: 34px 32px;
        background: rgba(255, 253, 249, 0.95);
        border: 1px solid #e6dacc;
        border-radius: 22px;
        box-shadow: 0 24px 40px rgba(31, 29, 27, 0.09);
    }

    .login-form-title {
        margin-bottom: 0.8rem;
        color: var(--fg-ink);
        font-weight: 700;
        font-size: 1rem;
    }

    @media (max-width: 860px) {
        .login-container {
            margin-top: 0.8rem;
            padding: 26px 22px;
            border-radius: 18px;
        }

        .fg-login-title {
            font-size: 1.8rem;
        }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_kpi_card(title: str, value: str, col_ref):
    """
    Renderiza una tarjeta KPI premium utilizando el componente Markdown de Streamlit
    dentro de una columna específica.
    """
    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """
    col_ref.markdown(card_html, unsafe_allow_html=True)
