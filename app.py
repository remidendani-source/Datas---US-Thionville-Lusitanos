# ============================================================
# THIONVILLE LUSITANOS — Dashboard Streamlit
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Thionville Lusitanos",
    page_icon="⚽",
    layout="wide"
)

# ──────────────────────────────────────────────────────────────────────────────
# THEME GLOBAL — FOND NOIR
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
  section.main, .block-container, [data-testid="stSidebar"] {
    background-color: #0d0d0d !important;
    color: #f0f0f0 !important;
  }
  [data-testid="stSidebar"] * { color: #f0f0f0 !important; }
  h1, h2, h3, h4, h5, h6, p, li, span, label, div { color: #f0f0f0 !important; }
  [data-testid="stMetricValue"] { color: #f0f0f0 !important; }
  [data-testid="stSelectbox"] select { background: #1a1a1a; color: #f0f0f0; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# COULEURS
# ──────────────────────────────────────────────────────────────────────────────
GOLD    = "#C9A84C"
GREEN   = "#27C677"
RED     = "#E24B4A"
BLUE    = "#4A90D9"
BG      = "#0d0d0d"
CARD_BG = "#1a1a1a"

def lyt(h=None):
    base = dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font_color="#f0f0f0",
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor=BG),
    )
    if h:
        base["height"] = h
    return base

# ──────────────────────────────────────────────────────────────────────────────
# CHARGEMENT
# ──────────────────────────────────────────────────────────────────────────────
FICHIER = "Team_Stats_Thionville_Lusitanos.xlsx"
TEAM    = "Thionville Lusitanos"

@st.cache_data
def load_data(path):
    def sheet(name):
        raw = pd.read_excel(path, sheet_name=name)
        df  = raw.iloc[2:].copy().reset_index(drop=True)
        df["Date"] = pd.to_datetime(df.iloc[:, 0], errors="coerce")
        return df
    return (sheet("Stats gen"), sheet("Stats off"), sheet("Stats def"),
            sheet("Stats pass"), sheet("Stats index"))

try:
    gen_all, off_all, defe_all, passe_all, idx_all = load_data(FICHIER)
    DATA_OK = True
except Exception as e:
    DATA_OK = False
    st.sidebar.error(f"Fichier introuvable : {e}")

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.title("⚽ Lusitanos Dashboard")
page = st.sidebar.radio("Navigation", [
    "🏠 Vue d'ensemble",
    "📈 Attaque",
    "🛡️ Défense",
    "🎯 Passes",
    "⚙️ Stats avancées",
    "📊 Référentiel N1",
])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : RÉFÉRENTIEL N1
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Référentiel N1":

    st.title("📊 Référentiel National 1 — KPI différenciants")
    st.markdown("Tableau de bord des 7 KPI qui distinguent les meilleures équipes du championnat National 1 2025-26.")

    # ── Définition des seuils ──────────────────────────────────────────────
    kpis = {
        "K1 · PPDA": ("≤ 10.5", "plus bas = mieux", True),
        "K2 · Récup. off./90": ("≥ 9.0", "plus haut = mieux", False),
        "K3 · Deep comp./90": ("≥ 5.0", "plus haut = mieux", False),
        "K4 · Pass. prog/90": ("≥ 65", "plus haut = mieux", False),
        "K5 · % pertes déf.": ("≤ 16%", "plus bas = mieux", True),
        "K6 · Tirs subis/90": ("≤ 10.0", "plus bas = mieux", True),
        "K7 · Ratio %R/%P": ("≥ 0.80", "plus haut = mieux", False),
    }

    cols = st.columns(7)
    for i, (kpi, (seuil, desc, inv)) in enumerate(kpis.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background:{CARD_BG};border:1px solid {GOLD};border-radius:8px;
                        padding:10px 8px;text-align:center;">
              <div style="font-size:11px;color:{GOLD};font-weight:700;margin-bottom:4px;">
                {kpi.split(' · ')[0]}
              </div>
              <div style="font-size:12px;font-weight:600;">{kpi.split(' · ')[1]}</div>
              <div style="font-size:18px;font-weight:700;color:{GOLD};margin:6px 0;">
                {seuil}
              </div>
              <div style="font-size:10px;color:#aaa;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Données du tableau ─────────────────────────────────────────────────
    data = [
        # cl, équipe, K1,    K2,    K3,   K4,   K5,   K6,    K7,   score
        (1,  "Dijon",           8.23,  11.60, 6.06, 74.6, 13,   7.27,  1.15, 7),
        (2,  "Sochaux",         8.95,  10.27, 5.52, 61.9, 15,   8.37,  0.93, 6),
        (3,  "Rouen",           9.09,  11.04, 5.66, 69.7, 13,   8.77,  1.08, 7),
        (4,  "Fleury 91 FC",    9.42,   9.73, 6.66, 71.4, 16,   9.90,  0.81, 6),
        (5,  "Versailles",      8.80,   9.47, 6.02, 65.8, 15,   9.67,  0.80, 7),
        (6,  "Orléans",        10.34,  10.95, 7.25, 69.5, 15,   9.45,  0.93, 7),
        (7,  "Le Puy F.43",    11.38,   8.20, 6.21, 72.6, 17,  10.05,  0.65, 3),
        (8,  "Caen",            8.91,   9.46, 5.68, 68.7, 13,   8.92,  1.00, 7),
        (9,  "Concarneau",     12.38,   7.99, 4.20, 65.9, 15,   8.13,  0.73, 3),
        (10, "Valenciennes",   10.45,  11.61, 4.99, 69.7, 13,   9.68,  1.15, 6),
        (11, "Aubagne",        10.34,   8.42, 4.25, 62.5, 19,  10.74,  0.58, 2),
        (12, "Villefranche",    9.86,   7.91, 3.57, 57.3, 19,  12.05,  0.58, 1),
        (13, "Quevilly Rouen", 13.31,   7.44, 3.29, 64.2, 17,   9.90,  0.59, 2),
        (14, "Paris 13 Atl.",  12.17,   8.96, 4.21, 62.4, 19,  11.51,  0.63, 1),
        (15, "Châteauroux",     9.42,   8.47, 4.28, 67.5, 16,  10.80,  0.75, 3),
        (16, "Bourg-en-Bresse",12.59,   9.14, 3.33, 64.0, 18,   8.97,  0.72, 3),
        (17, "Stade Briochin", 13.14,   8.86, 3.73, 67.2, 17,  12.10,  0.71, 2),
        (0,  "Moy. ligue",     10.52,   9.38, 5.00, 66.8, 16,   9.78,  0.76, None),
    ]

    seuils = {
        "K1": (None, 10.5),   # ≤ 10.5
        "K2": (9.0, None),    # ≥ 9.0
        "K3": (5.0, None),    # ≥ 5.0
        "K4": (65.0, None),   # ≥ 65
        "K5": (None, 16),     # ≤ 16%
        "K6": (None, 10.0),   # ≤ 10.0
        "K7": (0.80, None),   # ≥ 0.80
    }

    def color_cell(val, key):
        lo, hi = seuils[key]
        if hi is not None:   # ≤ seuil
            ok = val <= hi
        else:                # ≥ seuil
            ok = val >= lo
        return "#1a4a2e" if ok else "#4a1a1a"

    def score_color(s):
        if s is None: return "#333"
        if s >= 6: return "#1D6A42"
        if s >= 5: return "#4A7C2F"
        if s >= 3: return "#8B7020"
        return "#7A1E1E"

    def score_label(s):
        if s is None: return "—"
        return f"{s}/7"

    # ── Tableau HTML ───────────────────────────────────────────────────────
    rows_html = ""
    for row in data:
        cl, equipe, k1, k2, k3, k4, k5, k6, k7, score = row
        if cl == 0:  # ligne moyenne
            rank_cell = '<td style="color:#aaa;text-align:center;">—</td>'
            team_cell = f'<td style="color:#aaa;font-style:italic;">{equipe}</td>'
        else:
            rank_cell = f'<td style="text-align:center;font-weight:700;">{cl}</td>'
            team_cell = f'<td style="font-weight:500;">{equipe}</td>'

        def td(val, key, pct=False):
            bg = color_cell(val, key) if cl != 0 else "#1a1a1a"
            display = f"{val}%" if pct else str(val)
            return f'<td style="text-align:center;background:{bg};border-radius:4px;padding:4px 8px;">{display}</td>'

        sc_bg = score_color(score)
        sc_txt = score_label(score)
        score_cell = f'<td style="text-align:center;"><span style="background:{sc_bg};color:#fff;padding:3px 10px;border-radius:12px;font-weight:700;">{sc_txt}</span></td>'

        rows_html += f"""<tr style="border-bottom:1px solid #2a2a2a;">
          {rank_cell}{team_cell}
          {td(k1,"K1")}{td(k2,"K2")}{td(k3,"K3")}{td(k4,"K4")}
          {td(k5,"K5",pct=True)}{td(k6,"K6")}{td(k7,"K7")}
          {score_cell}
        </tr>"""

    table_html = f"""
    <style>
      .kpi-table {{ width:100%; border-collapse:separate; border-spacing:0 3px;
                    font-family:sans-serif; font-size:13px; }}
      .kpi-table th {{ background:#1e1e1e; color:{GOLD}; padding:8px 10px;
                       text-align:center; font-size:11px; border-bottom:2px solid {GOLD}; }}
      .kpi-table th.left {{ text-align:left; }}
      .kpi-table td {{ padding:5px 8px; color:#f0f0f0; }}
    </style>
    <table class="kpi-table">
      <thead><tr>
        <th style="width:30px;">Cl.</th>
        <th class="left" style="width:130px;">Équipe</th>
        <th>K1<br>PPDA<br>≤10.5</th>
        <th>K2<br>Récup off<br>≥9.0/90</th>
        <th>K3<br>Deep comp<br>≥5.0/90</th>
        <th>K4<br>Pass prog<br>≥65/90</th>
        <th>K5<br>%Pertes déf<br>≤16%</th>
        <th>K6<br>Tirs subis<br>≤10.0/90</th>
        <th>K7<br>Ratio %R/%P<br>≥0.80</th>
        <th>Score /7</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # ── Légende groupes ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    def legend_card(col, label, score_range, teams, bg):
        col.markdown(f"""
        <div style="background:{bg};border-radius:8px;padding:12px;text-align:center;">
          <div style="font-size:13px;font-weight:700;margin-bottom:4px;">{label}</div>
          <div style="font-size:22px;font-weight:800;color:{GOLD};">{score_range}</div>
          <div style="font-size:11px;color:#ccc;margin-top:6px;">{teams}</div>
        </div>
        """, unsafe_allow_html=True)

    legend_card(c1, "TOP 6 GARANTI", "6–7 / 7",
                "Dijon, Sochaux, Rouen, Fleury,<br>Versailles, Orléans", "#0f2e1a")
    legend_card(c2, "TOP 10 PROBABLE", "5–6 / 7",
                "Caen (7/7), Valenciennes (6/7)", "#1a2e0f")
    legend_card(c3, "MILIEU FLOTTANT", "3–4 / 7",
                "Le Puy, Concarneau, Châteauroux,<br>Bourg", "#2e2a0f")
    legend_card(c4, "BAS DE TABLEAU", "≤ 2 / 7",
                "Aubagne, Quevilly, Paris 13,<br>Villefranche, Briochin", "#2e0f0f")

    # ── Graphique radar top 3 vs bas 3 ────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Radar — Top 3 vs Bas 3 du championnat")

    categories = ["PPDA (inv.)", "Récup off", "Deep comp", "Pass prog (÷10)", "% Pertes (inv.)", "Tirs subis (inv.)", "Ratio %R/%P"]

    def normalize(vals):
        # normalise chaque valeur sur 0-10 pour le radar
        k1 = (10.5 - vals[0]) / (10.5 - 8.0) * 10  # PPDA inversé
        k2 = (vals[1] - 7.0) / (12.0 - 7.0) * 10
        k3 = (vals[2] - 3.0) / (7.5 - 3.0) * 10
        k4 = (vals[3] - 57.0) / (75.0 - 57.0) * 10
        k5 = (16 - vals[4]) / (16 - 13) * 10          # % pertes inversé
        k6 = (12.1 - vals[5]) / (12.1 - 7.27) * 10   # tirs subis inversé
        k7 = (vals[6] - 0.58) / (1.15 - 0.58) * 10
        return [max(0, min(10, v)) for v in [k1, k2, k3, k4, k5, k6, k7]]

    top3 = {
        "Dijon":     normalize([8.23, 11.60, 6.06, 74.6, 13, 7.27, 1.15]),
        "Sochaux":   normalize([8.95, 10.27, 5.52, 61.9, 15, 8.37, 0.93]),
        "Rouen":     normalize([9.09, 11.04, 5.66, 69.7, 13, 8.77, 1.08]),
    }
    bas3 = {
        "Villefranche": normalize([9.86,  7.91, 3.57, 57.3, 19, 12.05, 0.58]),
        "Paris 13":     normalize([12.17, 8.96, 4.21, 62.4, 19, 11.51, 0.63]),
        "St. Briochin": normalize([13.14, 8.86, 3.73, 67.2, 17, 12.10, 0.71]),
    }

    colors_top = [GREEN, "#5DCAA5", "#A8E6CF"]
    colors_bas  = [RED, "#E87A79", "#F4B8B8"]

    fig = go.Figure()
    for (name, vals), color in zip(top3.items(), colors_top):
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=categories + [categories[0]],
            fill="toself", name=name,
            line=dict(color=color, width=2),
            fillcolor=color.replace("#", "rgba(") + "0.15)",
            opacity=0.9
        ))
    for (name, vals), color in zip(bas3.items(), colors_bas):
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=categories + [categories[0]],
            fill="toself", name=name,
            line=dict(color=color, width=2, dash="dot"),
            fillcolor=color.replace("#", "rgba(") + "0.1)",
            opacity=0.8
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="#333", tickcolor="#aaa"),
            angularaxis=dict(gridcolor="#333", tickcolor="#f0f0f0"),
        ),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font_color="#f0f0f0",
        legend=dict(bgcolor=BG),
        height=480,
        margin=dict(l=60, r=60, t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Lecture du radar** : chaque axe est normalisé 0–10, où 10 = meilleur niveau de la ligue. Les KPI inversés (PPDA, % pertes, Tirs subis) sont retournés pour que 10 = meilleure performance.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGES EXISTANTES (données Thionville)
# ══════════════════════════════════════════════════════════════════════════════
elif not DATA_OK:
    st.warning("⚠️ Fichier Excel introuvable. Place `Team_Stats_Thionville_Lusitanos.xlsx` dans le même dossier que `app.py`.")

elif page == "🏠 Vue d'ensemble":
    st.title("🏠 Vue d'ensemble — Thionville Lusitanos")

    gen = gen_all.copy()
    gen.columns = list(range(len(gen.columns)))
    thi = gen[gen[4] == TEAM].copy().reset_index(drop=True)
    adv = gen[gen[4] != TEAM].copy().reset_index(drop=True)

    thi_j = [f"J{i+1}" for i in range(len(thi))]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buts marqués (moy.)", f"{pd.to_numeric(thi[6], errors='coerce').mean():.2f}")
    col2.metric("xG (moy.)", f"{pd.to_numeric(thi[7], errors='coerce').mean():.2f}")
    col3.metric("Possession (moy.)", f"{pd.to_numeric(thi[14], errors='coerce').mean():.1f}%")
    col4.metric("Matchs analysés", len(thi))

    goals_thi = pd.to_numeric(thi[6], errors="coerce")
    goals_adv = pd.to_numeric(adv[6], errors="coerce")
    xg_thi    = pd.to_numeric(thi[7], errors="coerce")

    fig = go.Figure()
    fig.add_bar(x=thi_j, y=goals_thi, name="Buts Thionville", marker_color=GOLD)
    fig.add_bar(x=thi_j, y=goals_adv.values[:len(thi)], name="Buts adversaire", marker_color=RED, opacity=0.7)
    fig.add_scatter(x=thi_j, y=xg_thi, name="xG Thionville", line=dict(color=GREEN, width=2, dash="dot"), mode="lines+markers")
    fig.update_layout(**lyt(300), title="Buts & xG par journée", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Attaque":
    st.title("📈 Attaque")
    off = off_all.copy()
    off.columns = list(range(len(off.columns)))
    thi = off[off[4] == TEAM].copy().reset_index(drop=True)
    thi_j = [f"J{i+1}" for i in range(len(thi))]

    shots  = pd.to_numeric(thi[7], errors="coerce")
    on_tgt = pd.to_numeric(thi[8], errors="coerce")
    xg     = pd.to_numeric(thi[6], errors="coerce")

    col1, col2, col3 = st.columns(3)
    col1.metric("Tirs/match (moy.)", f"{shots.mean():.1f}")
    col2.metric("Tirs cadrés/match", f"{on_tgt.mean():.1f}")
    col3.metric("xG/match", f"{xg.mean():.2f}")

    fig = go.Figure()
    fig.add_bar(x=thi_j, y=shots, name="Tirs totaux", marker_color=BLUE)
    fig.add_bar(x=thi_j, y=on_tgt, name="Tirs cadrés", marker_color=GREEN)
    fig.update_layout(**lyt(300), title="Tirs par journée", barmode="overlay")
    st.plotly_chart(fig, use_container_width=True)

elif page == "🛡️ Défense":
    st.title("🛡️ Défense")
    defe = defe_all.copy()
    defe.columns = list(range(len(defe.columns)))
    thi = defe[defe[4] == TEAM].copy().reset_index(drop=True)
    thi_j = [f"J{i+1}" for i in range(len(thi))]

    idx = idx_all.copy()
    idx.columns = list(range(len(idx.columns)))
    thi_idx = idx[idx[4] == TEAM].copy().reset_index(drop=True)

    # Buts concédés
    buts_conc = pd.to_numeric(thi[6], errors="coerce")
    col1, col2 = st.columns(2)
    col1.metric("Buts concédés (moy.)", f"{buts_conc.mean():.2f}")

    fig = go.Figure()
    fig.add_bar(x=thi_j, y=buts_conc, name="Buts concédés", marker_color=RED)
    fig.update_layout(**lyt(280), title="Buts concédés par journée")
    st.plotly_chart(fig, use_container_width=True)

    # PPDA depuis Stats index
    if len(thi_idx) > 0:
        # PPDA est généralement la colonne 6 dans Stats index
        ppda_vals = None
        for col_idx in range(6, min(15, len(thi_idx.columns))):
            try:
                vals = pd.to_numeric(thi_idx[col_idx], errors="coerce")
                if vals.mean() > 5 and vals.mean() < 20:
                    ppda_vals = vals
                    break
            except:
                pass

        if ppda_vals is not None:
            mean_ppda = ppda_vals.mean()
            st.subheader("PPDA par journée")
            st.metric("PPDA moyen", f"{mean_ppda:.2f}", delta=f"Réf. N1 ≤ 10.5")
            fig2 = go.Figure()
            fig2.add_bar(x=[f"J{i+1}" for i in range(len(ppda_vals))],
                         y=ppda_vals, name="PPDA", marker_color=BLUE)
            fig2.add_hline(y=mean_ppda, line=dict(color=GOLD, width=2, dash="dot"),
                           annotation_text=f"Moy. {mean_ppda:.2f}")
            fig2.add_hline(y=10.5, line=dict(color=GREEN, width=1, dash="dash"),
                           annotation_text="Seuil N1 (10.5)")
            fig2.update_layout(**lyt(280), title="PPDA — plus bas = pressing plus intense")
            st.plotly_chart(fig2, use_container_width=True)

elif page == "🎯 Passes":
    st.title("🎯 Passes")
    passe = passe_all.copy()
    passe.columns = list(range(len(passe.columns)))
    thi = passe[passe[4] == TEAM].copy().reset_index(drop=True)
    thi_j = [f"J{i+1}" for i in range(len(thi))]

    passes_tot = pd.to_numeric(thi[6], errors="coerce")
    passes_ok  = pd.to_numeric(thi[7], errors="coerce")

    col1, col2 = st.columns(2)
    col1.metric("Passes totales/match", f"{passes_tot.mean():.0f}")
    col2.metric("Passes réussies/match", f"{passes_ok.mean():.0f}")

    fig = go.Figure()
    fig.add_bar(x=thi_j, y=passes_tot, name="Passes totales", marker_color=BLUE, opacity=0.7)
    fig.add_bar(x=thi_j, y=passes_ok, name="Passes réussies", marker_color=GREEN)
    fig.update_layout(**lyt(300), title="Passes par journée", barmode="overlay")
    st.plotly_chart(fig, use_container_width=True)

    # Passes par possession depuis Stats index
    idx = idx_all.copy()
    idx.columns = list(range(len(idx.columns)))
    thi_idx = idx[idx[4] == TEAM].copy().reset_index(drop=True)

    if len(thi_idx) > 0:
        # Cherche avg passes per possession (typiquement ~3-8)
        avg_passes_col = None
        for col_idx in range(6, min(15, len(thi_idx.columns))):
            try:
                vals = pd.to_numeric(thi_idx[col_idx], errors="coerce")
                if vals.mean() > 2 and vals.mean() < 10:
                    avg_passes_col = vals
                    break
            except:
                pass

        if avg_passes_col is not None:
            st.subheader("Passes moyennes par possession")
            mean_val = avg_passes_col.mean()
            fig3 = go.Figure()
            fig3.add_bar(x=[f"J{i+1}" for i in range(len(avg_passes_col))],
                         y=avg_passes_col, marker_color=GOLD)
            fig3.add_hline(y=mean_val, line=dict(color=GREEN, width=2, dash="dot"),
                           annotation_text=f"Moy. {mean_val:.2f}")
            fig3.update_layout(**lyt(270), title="Avg passes per possession")
            st.plotly_chart(fig3, use_container_width=True)

elif page == "⚙️ Stats avancées":
    st.title("⚙️ Stats avancées")
    gen = gen_all.copy()
    gen.columns = list(range(len(gen.columns)))
    thi = gen[gen[4] == TEAM].copy().reset_index(drop=True)
    thi_j = [f"J{i+1}" for i in range(len(thi))]

    possession = pd.to_numeric(thi[14], errors="coerce")
    recup_tot  = pd.to_numeric(thi[19], errors="coerce")
    recup_haut = pd.to_numeric(thi[22], errors="coerce")

    col1, col2, col3 = st.columns(3)
    col1.metric("Possession moy.", f"{possession.mean():.1f}%")
    col2.metric("Récupérations/match", f"{recup_tot.mean():.0f}")
    col3.metric("Récup. zone haute/match", f"{recup_haut.mean():.1f}")

    fig = go.Figure()
    fig.add_scatter(x=thi_j, y=possession, mode="lines+markers",
                    name="Possession %", line=dict(color=GOLD, width=2))
    fig.update_layout(**lyt(280), title="Évolution de la possession")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_bar(x=thi_j, y=recup_tot, name="Récup. totales", marker_color=BLUE)
    fig2.add_bar(x=thi_j, y=recup_haut, name="Récup. zone haute", marker_color=GREEN)
    fig2.update_layout(**lyt(280), title="Récupérations par journée", barmode="group")
    st.plotly_chart(fig2, use_container_width=True)
