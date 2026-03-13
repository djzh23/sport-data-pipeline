import streamlit as st
import sys
sys.path.append(".")
from pipeline.extract import get_all_matches, LEAGUES
from pipeline.transform import add_match_results, build_standings
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="KoraStics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme System ─────────────────────────────────────
THEMES = {
    "🌙 Dark": {
        "bg":           "#0a0c10",
        "sidebar_bg":   "#111318",
        "card_bg":      "#13151c",
        "border":       "#1e2230",
        "border2":      "#1a1d27",
        "text_primary": "#ffffff",
        "text_secondary":"#888888",
        "text_muted":   "#444444",
        "row_hover":    "#13151c",
        "plot_bg":      "#0a0c10",
        "grid":         "#1a1d27",
        "standing_row_color": "#aaaaaa",
        "team_name_color":    "#e0e0e0",
        "pos_badge_bg": "#1e2230",
        "pos_badge_fg": "#555555",
    },
    "☀️ Light": {
        "bg":           "#f4f6fa",
        "sidebar_bg":   "#ffffff",
        "card_bg":      "#ffffff",
        "border":       "#e2e6f0",
        "border2":      "#e8ecf4",
        "text_primary": "#0f1117",
        "text_secondary":"#666666",
        "text_muted":   "#aaaaaa",
        "row_hover":    "#f0f2f8",
        "plot_bg":      "#ffffff",
        "grid":         "#e8ecf4",
        "standing_row_color": "#444444",
        "team_name_color":    "#111111",
        "pos_badge_bg": "#e8ecf4",
        "pos_badge_fg": "#999999",
    },
}

if "theme" not in st.session_state:
    st.session_state.theme = "🌙 Dark"

T = THEMES[st.session_state.theme]
is_dark = st.session_state.theme == "🌙 Dark"

def inject_css(T):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
}}

[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['border']} !important;
}}
.stApp {{ background: {T['bg']} !important; }}
.block-container {{ padding: 2.5rem 3rem !important; max-width: 1400px; }}

/* KPI Cards */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 1.8rem 0 2.5rem;
}}
.kpi {{
    background: {T['card_bg']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 26px 20px;
    text-align: center;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.kpi:hover {{ box-shadow: 0 4px 24px rgba(0,0,0,0.1); }}
.kpi-val {{
    font-size: 2.6rem;
    font-weight: 800;
    color: {T['text_primary']};
    line-height: 1;
    letter-spacing: -0.03em;
}}
.kpi-label {{
    font-size: 0.72rem;
    color: {T['text_muted']};
    margin-top: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}}
.kpi-sub {{ font-size: 0.78rem; margin-top: 6px; font-weight: 500; }}

/* Section headers */
.section-hdr {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {T['text_muted']};
    margin: 2.5rem 0 1.2rem;
    padding-bottom: 10px;
    border-bottom: 1px solid {T['border2']};
}}

/* Page titles */
.page-title {{
    font-size: 2rem;
    font-weight: 800;
    color: {T['text_primary']};
    letter-spacing: -0.03em;
    margin-bottom: 0.3rem;
    line-height: 1.1;
}}
.page-subtitle {{
    font-size: 0.88rem;
    color: {T['text_secondary']};
    margin-bottom: 2rem;
    font-weight: 400;
}}

/* Standings table */
.standing-header {{
    display: grid;
    grid-template-columns: 36px 30px 1fr 50px 50px 50px 50px 50px 50px 60px;
    align-items: center;
    padding: 8px 18px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {T['text_muted']};
    margin-bottom: 4px;
}}
.standing-row {{
    display: grid;
    grid-template-columns: 36px 30px 1fr 50px 50px 50px 50px 50px 50px 60px;
    align-items: center;
    padding: 12px 18px;
    border-radius: 10px;
    margin-bottom: 3px;
    font-size: 0.9rem;
    color: {T['standing_row_color']};
    border: 1px solid transparent;
    transition: background 0.15s;
}}
.standing-row:hover {{ background: {T['row_hover']} !important; }}
.col-c {{ text-align: center; }}
.team-logo {{ width: 24px; height: 24px; object-fit: contain; }}
.team-name {{
    font-weight: 600;
    color: {T['team_name_color']};
    font-size: 0.92rem;
}}
.pos-badge {{
    width: 24px; height: 24px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    background: {T['pos_badge_bg']};
    color: {T['pos_badge_fg']};
}}
.pos-cl {{ background: #0d3d1a !important; color: #22c55e !important; }}
.pos-el {{ background: #0d1e3a !important; color: #3b82f6 !important; }}
.pos-rel {{ background: #3d0d0d !important; color: #ef4444 !important; }}
.zone-cl {{ background: rgba(34,197,94,0.05) !important; border-color: rgba(34,197,94,0.12) !important; }}
.zone-el {{ background: rgba(59,130,246,0.05) !important; border-color: rgba(59,130,246,0.12) !important; }}
.zone-rel {{ background: rgba(239,68,68,0.05) !important; border-color: rgba(239,68,68,0.12) !important; }}
.diff-pos {{ color: #22c55e; font-weight: 700; }}
.diff-neg {{ color: #ef4444; font-weight: 700; }}
.diff-zero {{ color: {T['text_muted']}; }}
.pkt {{ font-weight: 800; color: {T['text_primary']}; font-size: 1rem; }}

/* Match cards */
.match-card {{
    display: grid;
    grid-template-columns: 1fr 100px 1fr;
    align-items: center;
    padding: 15px 28px;
    margin-bottom: 5px;
    background: {T['card_bg']};
    border-radius: 12px;
    border: 1px solid {T['border']};
    transition: box-shadow 0.15s;
}}
.match-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}

/* Metrics */
[data-testid="stMetric"] {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 14px !important;
    padding: 20px !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.72rem !important;
    color: {T['text_muted']} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: {T['text_primary']} !important;
}}

/* Streamlit overrides */
h1, h2, h3 {{ color: {T['text_primary']} !important; }}
p, li {{ font-size: 0.95rem !important; color: {T['text_secondary']}; }}
.stSelectbox label, .stRadio label {{ font-size: 0.85rem !important; color: {T['text_secondary']} !important; }}

/* ── Sidebar nav radio ── */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {{
    gap: 3px !important;
    padding: 0 8px !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    background: transparent !important;
    border-radius: 9px !important;
    padding: 10px 12px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: {T['text_secondary']} !important;
    transition: background 0.15s, color 0.15s !important;
    width: 100% !important;
    border: none !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background: {T['border']} !important;
    color: {T['text_primary']} !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {{
    display: flex !important;
    align-items: center !important;
}}

/* ── Selectbox – both sidebar and main ── */
.stSelectbox > div > div {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
    color: {T['text_primary']} !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}}
/* Dropdown list */
[data-testid="stSelectbox"] ul,
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
}}
div[data-baseweb="menu"] li,
div[data-baseweb="popover"] li {{
    background: {T['card_bg']} !important;
    color: {T['text_primary']} !important;
    font-size: 0.88rem !important;
}}
div[data-baseweb="menu"] li:hover,
div[data-baseweb="popover"] li:hover {{
    background: {T['border']} !important;
}}
div[data-baseweb="menu"] li[aria-selected="true"],
div[data-baseweb="popover"] li[aria-selected="true"] {{
    background: {T['border2']} !important;
    color: {T['text_primary']} !important;
    font-weight: 600 !important;
}}

/* ── Theme toggle pills ── */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-type="horizontal"] label {{
    padding: 5px 10px !important;
    font-size: 0.78rem !important;
    border-radius: 20px !important;
    border: 1px solid {T['border']} !important;
}}

/* ── Top header bar ── */
header[data-testid="stHeader"] {{
    background: {T['bg']} !important;
    border-bottom: 1px solid {T['border']} !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {T['border']} !important;
    border-radius: 12px !important;
    overflow: hidden;
}}

/* ── Slider ── */
[data-testid="stSlider"] > div > div {{
    color: {T['text_primary']} !important;
}}

/* ── Button ── */
[data-testid="stSidebar"] button[kind="secondary"] {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['border']} !important;
    color: {T['text_primary']} !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    margin: 0 8px !important;
    width: calc(100% - 16px) !important;
}}

/* ── Mobile Responsive ── */
@media (max-width: 768px) {{
    .block-container {{
        padding: 1.2rem 1rem !important;
    }}
    .kpi-grid {{
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 10px !important;
        margin: 1rem 0 1.5rem !important;
    }}
    .kpi-val {{
        font-size: 1.9rem !important;
    }}
    .kpi {{
        padding: 18px 14px !important;
    }}
    .page-title {{
        font-size: 1.4rem !important;
    }}
    .page-subtitle {{
        font-size: 0.78rem !important;
        margin-bottom: 1rem !important;
    }}
    .section-hdr {{
        margin: 1.5rem 0 0.8rem !important;
    }}
    /* Top header: stack vertically */
    .top-header {{
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 10px !important;
    }}
    .top-header-badges {{
        flex-wrap: wrap !important;
        gap: 6px !important;
    }}
    /* Standings: hide middle columns, keep pos/logo/team/pts */
    .standing-header,
    .standing-row {{
        grid-template-columns: 36px 30px 1fr 60px !important;
        padding: 10px 10px !important;
    }}
    .standing-row > div:nth-child(4),
    .standing-row > div:nth-child(5),
    .standing-row > div:nth-child(6),
    .standing-row > div:nth-child(7),
    .standing-row > div:nth-child(8),
    .standing-row > div:nth-child(9),
    .standing-header > div:nth-child(4),
    .standing-header > div:nth-child(5),
    .standing-header > div:nth-child(6),
    .standing-header > div:nth-child(7),
    .standing-header > div:nth-child(8),
    .standing-header > div:nth-child(9) {{
        display: none !important;
    }}
    .team-name {{
        font-size: 0.78rem !important;
    }}
    /* Match cards */
    .match-card {{
        grid-template-columns: 1fr 70px 1fr !important;
        padding: 10px 12px !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

inject_css(T)

LEAGUE_COLORS = {
    "Bundesliga 🇩🇪": "#e30613",
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "#6f2da8",
    "La Liga 🇪🇸": "#ee8707",
}

TEAM_IDS = {
    "FC Bayern München": 5, "Borussia Dortmund": 4, "TSG 1899 Hoffenheim": 3,
    "VfB Stuttgart": 10, "RB Leipzig": 721, "Bayer 04 Leverkusen": 3,
    "Eintracht Frankfurt": 19, "SC Freiburg": 17, "FC Augsburg": 16,
    "Hamburger SV": 18, "1. FC Union Berlin": 28368, "Borussia Mönchengladbach": 18,
    "SV Werder Bremen": 12, "1. FC Köln": 1, "1. FSV Mainz 05": 15,
    "FC St. Pauli 1910": 712, "VfL Wolfsburg": 11, "1. FC Heidenheim 1846": 44,
    "Arsenal FC": 57, "Chelsea FC": 61, "Liverpool FC": 64,
    "Manchester City FC": 65, "Manchester United FC": 66, "Tottenham Hotspur FC": 73,
    "Real Madrid CF": 86, "FC Barcelona": 81, "Club Atlético de Madrid": 78,
    "Athletic Club": 77, "Real Sociedad de Fútbol": 92, "Villarreal CF": 94,
}

# ── Sidebar ───────────────────────────────────────────
with st.sidebar:

    # App Logo + Name
    st.markdown(f"""
    <div style="padding:20px 16px 16px;border-bottom:1px solid {T['border']};margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,#e30613,#ff6b35);
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;flex-shrink:0;">⚽</div>
            <div>
                <div style="font-size:1.1rem;font-weight:800;color:{T['text_primary']};
                            letter-spacing:-0.02em;line-height:1.1;">KoraStics</div>
                <div style="font-size:0.65rem;color:{T['text_muted']};font-weight:500;
                            letter-spacing:0.08em;text-transform:uppercase;">
                    Football Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Liga Auswahl
    st.markdown(f"""
    <div style="padding:0 12px;margin-bottom:4px;">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:{T['text_muted']};">Liga</div>
    </div>
    """, unsafe_allow_html=True)

    selected_league = st.selectbox(
        "Liga", list(LEAGUES.keys()), label_visibility="collapsed"
    )
    color = LEAGUE_COLORS[selected_league]
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    # Liga color stripe
    st.markdown(f"""
    <div style="height:2px;background:linear-gradient(90deg,{color},transparent);
                border-radius:2px;margin:8px 12px 16px;"></div>
    """, unsafe_allow_html=True)

    # Navigation label
    st.markdown(f"""
    <div style="padding:0 12px;margin-bottom:4px;">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:{T['text_muted']};">Navigation</div>
    </div>
    """, unsafe_allow_html=True)

    NAV_ICONS = {"Übersicht": "◎", "Tabelle": "≡", "Spieltage": "▦", "Team-Analyse": "◈"}
    page = st.radio(
        "nav", ["Übersicht", "Tabelle", "Spieltage", "Team-Analyse"],
        label_visibility="collapsed",
        format_func=lambda x: f"{NAV_ICONS[x]}  {x}"
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Theme label
    st.markdown(f"""
    <div style="padding:0 12px;margin-bottom:4px;">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:{T['text_muted']};">Erscheinungsbild</div>
    </div>
    """, unsafe_allow_html=True)

    theme_choice = st.radio(
        "theme", list(THEMES.keys()), horizontal=True,
        index=list(THEMES.keys()).index(st.session_state.theme),
        label_visibility="collapsed"
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button("🔄  Daten aktualisieren", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"""
    <div style="margin-top:20px;padding-top:14px;border-top:1px solid {T['border']};">
        <div style="font-size:0.7rem;color:{T['text_muted']};line-height:1.8;padding:0 4px;">
            Daten: football-data.org<br>
            Python · DuckDB · Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)
# ── Daten laden ───────────────────────────────────────
@st.cache_data(show_spinner="Lade Ligadaten...")
def load_league(league_name: str):
    cfg = LEAGUES[league_name]
    raw = get_all_matches(cfg["code"], cfg["season"])
    if raw.empty:
        return pd.DataFrame(), pd.DataFrame()
    df = add_match_results(raw)
    df = df[df["status"] == "FINISHED"].copy()
    standings = build_standings(df)
    return df, standings

df, standings = load_league(selected_league)
if df.empty:
    st.error("Keine Daten verfügbar.")
    st.stop()

# ── Plotly Base Layout ────────────────────────────────
def plotly_layout(height=360):
    return dict(
        plot_bgcolor=T["plot_bg"], paper_bgcolor=T["plot_bg"],
        font=dict(color=T["text_secondary"], family="Inter", size=13),
        height=height,
        margin=dict(l=48, r=24, t=24, b=48),
        xaxis=dict(gridcolor=T["grid"], linecolor=T["grid"], tickfont=dict(size=12, color=T["text_muted"])),
        yaxis=dict(gridcolor=T["grid"], linecolor=T["grid"], tickfont=dict(size=12, color=T["text_muted"])),
        hoverlabel=dict(bgcolor=T["card_bg"], bordercolor=T["border"], font=dict(family="Inter", size=13)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color=T["text_secondary"])),
    )

league_short = selected_league.replace("🇩🇪","").replace("🏴󠁧󠁢󠁥󠁮󠁧󠁿","").replace("🇪🇸","").strip()

# ── App Top Header ────────────────────────────────────
matchday_info = f"Spieltag {int(df['matchday'].max())} · {len(df)} Spiele"
st.markdown(f"""
<div class="top-header" style="display:flex;align-items:center;justify-content:space-between;
            padding:14px 0 20px;border-bottom:1px solid {T['border']};margin-bottom:8px;">
    <div style="display:flex;align-items:center;gap:14px;">
        <div style="width:40px;height:40px;border-radius:12px;
                    background:linear-gradient(135deg,#e30613,#ff6b35);
                    display:flex;align-items:center;justify-content:center;
                    font-size:20px;flex-shrink:0;">⚽</div>
        <div>
            <div style="font-size:1.5rem;font-weight:800;color:{T['text_primary']};
                        letter-spacing:-0.03em;line-height:1;">KoraStics</div>
            <div style="font-size:0.75rem;color:{T['text_muted']};font-weight:500;
                        letter-spacing:0.06em;text-transform:uppercase;margin-top:2px;">
                Football Analytics Platform</div>
        </div>
    </div>
    <div class="top-header-badges" style="display:flex;align-items:center;gap:8px;">
        <div style="background:{T['card_bg']};border:1px solid {T['border']};
                    border-radius:20px;padding:6px 14px;font-size:0.78rem;
                    color:{T['text_secondary']};font-weight:500;">
            {selected_league}
        </div>
        <div style="background:{T['card_bg']};border:1px solid {T['border']};
                    border-radius:20px;padding:6px 14px;font-size:0.78rem;
                    color:{T['text_muted']};font-weight:500;">
            {matchday_info}
        </div>
        <div style="background:{T['card_bg']};border:1px solid {T['border']};
                    border-radius:20px;padding:6px 14px;font-size:0.78rem;
                    color:{T['text_muted']};font-weight:500;">
            2025/26
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# ÜBERSICHT
# ══════════════════════════════════════════════════════
if page == "Übersicht":
    st.markdown(f'<div class="page-title">⚽ {selected_league}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Saison 2025/26 · {len(df)} Spiele gespielt · Spieltag {int(df["matchday"].max())} von 34</div>', unsafe_allow_html=True)

    total_goals = int(df["total_goals"].sum())
    avg_goals = df["total_goals"].mean()
    home_pct = len(df[df["result"] == "home_win"]) / len(df) * 100
    top_idx = df["total_goals"].idxmax()
    top_score = f"{int(df.loc[top_idx,'home_goals'])}:{int(df.loc[top_idx,'away_goals'])}"
    top_teams = f"{df.loc[top_idx,'home_team'].split()[-1]} – {df.loc[top_idx,'away_team'].split()[-1]}"

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi"><div class="kpi-val">{len(df)}</div><div class="kpi-label">Spiele</div></div>
        <div class="kpi"><div class="kpi-val">{total_goals}</div><div class="kpi-label">Tore</div><div class="kpi-sub" style="color:{color}">Ø {avg_goals:.2f} / Spiel</div></div>
        <div class="kpi"><div class="kpi-val">{home_pct:.0f}%</div><div class="kpi-label">Heimsiege</div></div>
        <div class="kpi"><div class="kpi-val">{top_score}</div><div class="kpi-label">Höchstes Ergebnis</div><div class="kpi-sub" style="color:#666">{top_teams}</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-hdr">Ergebnis-Verteilung</div>', unsafe_allow_html=True)
        rc = df["result"].value_counts()
        lmap = {"home_win": "Heimsieg", "away_win": "Auswärtssieg", "draw": "Unentschieden"}
        fig_pie = go.Figure(go.Pie(
            labels=[lmap.get(x, x) for x in rc.index], values=rc.values, hole=0.58,
            marker=dict(colors=[color, "#2a2d3a", "#3a3d4a"], line=dict(color="#0a0c10", width=2)),
            textfont=dict(size=12, family="Inter"),
            hovertemplate="%{label}: <b>%{value}</b> Spiele (%{percent})<extra></extra>"
        ))
        fig_pie.update_layout(**plotly_layout(320))
        fig_pie.update_layout(
            annotations=[dict(text=f"<b>{len(df)}</b><br><span>Spiele</span>", x=0.5, y=0.5,
                              showarrow=False, font=dict(color="white", size=15, family="Inter"))]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-hdr">Tore pro Spieltag</div>', unsafe_allow_html=True)
        gpmd = df.groupby("matchday")["total_goals"].sum().reset_index()
        avg_l = gpmd["total_goals"].mean()
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=gpmd["matchday"], y=gpmd["total_goals"], mode="lines+markers",
            line=dict(color=color, width=2), marker=dict(size=5, color=color),
            fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.08)",
            hovertemplate="Spieltag %{x}: <b>%{y} Tore</b><extra></extra>"
        ))
        fig_line.add_hline(y=avg_l, line_dash="dot", line_color="#333",
                           annotation_text=f"Ø {avg_l:.1f}", annotation_font_color="#555",
                           annotation_font_size=11)
        fig_line.update_layout(**plotly_layout(320))
        fig_line.update_layout(xaxis_title="Spieltag", yaxis_title="Tore")
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown('<div class="section-hdr">Top 5 torreichste Spiele</div>', unsafe_allow_html=True)
    top5 = df.nlargest(5, "total_goals").copy()
    top5["Spiel"] = top5["home_team"] + "  " + top5["home_goals"].astype(int).astype(str) + " : " + top5["away_goals"].astype(int).astype(str) + "  " + top5["away_team"]
    st.dataframe(top5[["matchday","Spiel","total_goals"]].rename(columns={"matchday":"Spieltag","total_goals":"Tore"}),
                 use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════
# TABELLE
# ══════════════════════════════════════════════════════
elif page == "Tabelle":
    st.markdown(f'<div class="page-title">Tabelle · {league_short}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Stand nach Spieltag {int(df["matchday"].max())}</div>', unsafe_allow_html=True)

    std = standings.copy().reset_index()
    std.columns = ["pos"] + list(std.columns[1:])
    std["pos"] = range(1, len(std)+1)

    st.markdown("""
    <div class="standing-header">
        <div>#</div><div></div><div>Verein</div>
        <div class="col-c">Sp</div><div class="col-c">S</div><div class="col-c">U</div>
        <div class="col-c">N</div><div class="col-c">T</div><div class="col-c">GT</div>
        <div class="col-c">Pkt</div>
    </div>
    """, unsafe_allow_html=True)

    for _, row in std.iterrows():
        pos = int(row["pos"])
        diff = int(row["goal_diff"])
        diff_cls = "diff-pos" if diff > 0 else "diff-neg" if diff < 0 else "diff-zero"
        diff_str = f"+{diff}" if diff > 0 else str(diff)

        if pos <= 4:   zone, badge = "zone-cl", "pos-cl"
        elif pos == 5: zone, badge = "zone-el", "pos-el"
        elif pos >= 16: zone, badge = "zone-rel", "pos-rel"
        else:          zone, badge = "", ""

        logo_id = TEAM_IDS.get(row["team"], "")
        logo_html = f'<img class="team-logo" src="https://crests.football-data.org/{logo_id}.png" onerror="this.style.display=\'none\'">' if logo_id else "<span style='font-size:16px'>⚽</span>"

        st.markdown(f"""
        <div class="standing-row {zone}">
            <div><span class="pos-badge {badge}">{pos}</span></div>
            <div>{logo_html}</div>
            <div class="team-name">{row["team"]}</div>
            <div class="col-c">{int(row["played"])}</div>
            <div class="col-c">{int(row["wins"])}</div>
            <div class="col-c">{int(row["draws"])}</div>
            <div class="col-c">{int(row["losses"])}</div>
            <div class="col-c">{int(row["scored"])}</div>
            <div class="col-c">{int(row["conceded"])}</div>
            <div class="col-c pkt">{int(row["points"])}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.success("🟢 Champions League · Platz 1–4")
    c2.info("🔵 Europa League · Platz 5")
    c3.error("🔴 Abstieg · Platz 16–18")

# ══════════════════════════════════════════════════════
# SPIELTAGE
# ══════════════════════════════════════════════════════
elif page == "Spieltage":
    st.markdown(f'<div class="page-title">Spieltage · {league_short}</div>', unsafe_allow_html=True)

    max_md = int(df["matchday"].max())
    matchday = st.slider("Spieltag", 1, max_md, max_md, label_visibility="collapsed")
    st.markdown(f'<div class="page-subtitle">Spieltag {matchday} von {max_md}</div>', unsafe_allow_html=True)

    filtered = df[df["matchday"] == matchday].copy()
    c1, c2, c3 = st.columns(3)
    c1.metric("Spiele", len(filtered))
    c2.metric("Tore", int(filtered["total_goals"].sum()))
    c3.metric("Ø Tore", f"{filtered['total_goals'].mean():.1f}")

    st.markdown('<div class="section-hdr">Ergebnisse</div>', unsafe_allow_html=True)
    for _, row in filtered.sort_values("total_goals", ascending=False).iterrows():
        h = int(row["home_goals"])
        a = int(row["away_goals"])
        hw = f"font-weight:700;color:{T['text_primary']}" if row["result"] == "home_win" else f"color:{T['text_secondary']}"
        aw = f"font-weight:700;color:{T['text_primary']}" if row["result"] == "away_win" else f"color:{T['text_secondary']}"
        score_color = color if row["result"] != "draw" else T["text_secondary"]
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 90px 1fr;align-items:center;
                    padding:13px 16px;margin-bottom:4px;background:{T['card_bg']};
                    border-radius:10px;border:1px solid {T['border']};">
            <div style="text-align:right;font-size:0.88rem;{hw}">{row["home_team"]}</div>
            <div style="text-align:center;font-size:1.2rem;font-weight:700;
                        color:{score_color};letter-spacing:0.05em">{h} : {a}</div>
            <div style="text-align:left;font-size:0.88rem;{aw}">{row["away_team"]}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TEAM-ANALYSE
# ══════════════════════════════════════════════════════
elif page == "Team-Analyse":
    st.markdown(f'<div class="page-title">Team-Analyse · {league_short}</div>', unsafe_allow_html=True)

    teams_list = sorted(standings["team"].tolist())
    selected_team = st.selectbox("Team", teams_list, label_visibility="collapsed")

    tm = df[(df["home_team"] == selected_team) | (df["away_team"] == selected_team)].copy()
    home_m = tm[tm["home_team"] == selected_team]
    away_m = tm[tm["away_team"] == selected_team]

    scored   = int(home_m["home_goals"].sum() + away_m["away_goals"].sum())
    conceded = int(home_m["away_goals"].sum() + away_m["home_goals"].sum())
    pts      = int(standings[standings["team"] == selected_team]["points"].values[0])
    pos      = int(standings[standings["team"] == selected_team].index[0])
    wins     = int(standings[standings["team"] == selected_team]["wins"].values[0])
    draws    = int(standings[standings["team"] == selected_team]["draws"].values[0])
    losses   = int(standings[standings["team"] == selected_team]["losses"].values[0])

    logo_id = TEAM_IDS.get(selected_team, "")
    if logo_id:
        st.markdown(f'<img src="https://crests.football-data.org/{logo_id}.png" style="height:52px;margin-bottom:14px;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.5))">', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Platz", f"#{pos}")
    c2.metric("Punkte", pts)
    c3.metric("Siege", wins)
    c4.metric("Tore", scored)
    c5.metric("Gegentore", conceded)

    rows = []
    for _, row in tm.iterrows():
        is_home = row["home_team"] == selected_team
        opponent = row["away_team"] if is_home else row["home_team"]
        s  = row["home_goals"] if is_home else row["away_goals"]
        c_ = row["away_goals"] if is_home else row["home_goals"]
        rl = (
            "Sieg" if (is_home and row["result"] == "home_win") or (not is_home and row["result"] == "away_win")
            else "Niederlage" if (is_home and row["result"] == "away_win") or (not is_home and row["result"] == "home_win")
            else "Unentschieden"
        )
        rows.append({
            "matchday": int(row["matchday"]), "opponent": opponent,
            "scored": int(s) if pd.notna(s) else 0,
            "conceded": int(c_) if pd.notna(c_) else 0,
            "result": rl, "venue": "Heim" if is_home else "Auswärts",
        })

    tg = pd.DataFrame(rows).sort_values("matchday")
    res_colors = {"Sieg": "#22c55e", "Niederlage": "#ef4444", "Unentschieden": "#888"}

    # Chart 1: Tore
    st.markdown('<div class="section-hdr">Tore pro Spieltag</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tg["matchday"], y=tg["scored"], name="Erzielt",
        marker=dict(color=color, line_width=0),
        customdata=tg[["opponent","result","venue","conceded"]],
        hovertemplate="<b>Spieltag %{x}</b><br>%{customdata[0]} · %{customdata[2]}<br><b>%{customdata[1]}</b><br>Erzielt: %{y}  Kassiert: %{customdata[3]}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=tg["matchday"], y=-tg["conceded"], name="Kassiert",
        marker=dict(color="#2a2d3a", line_width=0),
        customdata=tg[["opponent","result","venue","scored"]],
        hovertemplate="<b>Spieltag %{x}</b><br>%{customdata[0]} · %{customdata[2]}<br><b>%{customdata[1]}</b><br>Kassiert: %{y}  Erzielt: %{customdata[3]}<extra></extra>"
    ))
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.08)", line_width=1)
    layout = plotly_layout(340)
    layout["barmode"] = "relative"
    layout["hovermode"] = "x unified"
    layout["xaxis"] = dict(title="Spieltag", gridcolor="#1a1d27", linecolor="#1a1d27", tickmode="linear", dtick=2, tickfont=dict(size=11, color="#666"))
    layout["yaxis"] = dict(title="Tore", gridcolor="#1a1d27", linecolor="#1a1d27", tickfont=dict(size=11, color="#666"))
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    # Chart 2: Punkte
    st.markdown('<div class="section-hdr">Punkte-Verlauf</div>', unsafe_allow_html=True)
    tg["pts_gained"] = tg["result"].map({"Sieg": 3, "Unentschieden": 1, "Niederlage": 0})
    tg["cum_pts"] = tg["pts_gained"].cumsum()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=tg["matchday"], y=tg["cum_pts"], mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(color=[res_colors[r] for r in tg["result"]], size=10, line=dict(color="#0a0c10", width=2)),
        customdata=tg[["opponent","result","venue","pts_gained"]],
        hovertemplate="<b>Spieltag %{x}</b><br>%{customdata[0]} · %{customdata[2]}<br><b>%{customdata[1]}</b> (+%{customdata[3]} Pkt)<br>Gesamt: <b>%{y} Punkte</b><extra></extra>"
    ))
    fig2.add_annotation(
        x=tg["matchday"].iloc[-1], y=tg["cum_pts"].iloc[-1],
        text=f"  <b>{pts} Pkt</b>", showarrow=False,
        font=dict(color=color, size=13, family="Inter")
    )
    layout2 = plotly_layout(300)
    layout2["hovermode"] = "x"
    layout2["xaxis"] = dict(title="Spieltag", gridcolor="#1a1d27", linecolor="#1a1d27", tickmode="linear", dtick=2, tickfont=dict(size=11, color="#666"))
    layout2["yaxis"] = dict(title="Punkte", gridcolor="#1a1d27", linecolor="#1a1d27", tickfont=dict(size=11, color="#666"))
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

    # Bilanz + Spielliste
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.markdown('<div class="section-hdr">Bilanz</div>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Pie(
            labels=["Siege","Unentschieden","Niederlagen"], values=[wins, draws, losses], hole=0.62,
            marker=dict(colors=["#22c55e","#555","#ef4444"], line=dict(color="#0a0c10", width=2)),
            textfont=dict(size=11, family="Inter"),
            hovertemplate="%{label}: %{value}<extra></extra>"
        ))
        fig3.update_layout(**plotly_layout(270))
        fig3.update_layout(
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11), orientation="h", y=-0.15),
            annotations=[dict(text=f"<b>{wins}</b><br>Siege", x=0.5, y=0.5,
                              showarrow=False, font=dict(color="white", size=15, family="Inter"))]
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-hdr">Alle Spiele</div>', unsafe_allow_html=True)
        disp = tg.copy()
        disp["Ergebnis"] = disp["scored"].astype(str) + " : " + disp["conceded"].astype(str)
        disp = disp.rename(columns={"matchday":"Sp","venue":"Ort","opponent":"Gegner","result":"Typ"})[["Sp","Ort","Gegner","Ergebnis","Typ"]]
        st.dataframe(disp.sort_values("Sp"), use_container_width=True, hide_index=True, height=270)