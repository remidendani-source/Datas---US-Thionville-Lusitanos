# ============================================================
# US THIONVILLE LUSITANOS — Dashboard Streamlit
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(
    page_title="US Thionville Lusitanos",
    page_icon="⚽",
    layout="wide"
)

FICHIER = "Team_Stats_Thionville_Lusitanos.xlsx"
TEAM    = "Thionville Lusitanos"
COMP_LABELS = {
    "France. National 2": "National 2 · 2025-26",
    "France. Ligue 3":    "Ligue 3 · 2026-27",
}

@st.cache_data
def load_data(path):
    def sheet(name):
        raw = pd.read_excel(path, sheet_name=name)
        df  = raw.iloc[2:].copy().reset_index(drop=True)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return sheet("Stats gen"), sheet("Stats off"), sheet("Stats def"), \
           sheet("Stats pass"), sheet("Stats index")

gen_all, off_all, defe_all, passe_all, idx_all = load_data(FICHIER)

DARK  = "#000000"
CARD  = "#111111"
BORD  = "#2a2a2a"
TEXT  = "#ffffff"
MUTED = "#8b949e"
GREY  = "#9e9e9e"
RED   = "#ff2d55"
GREEN = "#00ff88"
GOLD  = "#ffd60a"

st.markdown(f"""
<style>
  .stApp,.main,[data-testid="stAppViewContainer"],[data-testid="stHeader"],
  section[data-testid="stSidebar"],[data-testid="stSidebarContent"]
  {{ background-color:{DARK} !important; }}
  .block-container {{ padding-top:1rem; background-color:{DARK} !important; }}
  h1,h2,h3,p,label,span {{ color:{TEXT} !important; }}
  .kpi {{ background:{CARD}; border:1px solid {BORD}; border-radius:10px; padding:16px 18px; text-align:center; margin-bottom:8px; }}
  .kpi-label {{ color:{MUTED}; font-size:12px; margin-bottom:4px; }}
  .kpi-value {{ color:{TEXT}; font-size:26px; font-weight:700; }}
  .kpi-pos {{ color:{GREEN}; font-size:11px; margin-top:3px; }}
  .kpi-neg {{ color:{RED};   font-size:11px; margin-top:3px; }}
  .kpi-neu {{ color:{MUTED}; font-size:11px; margin-top:3px; }}
  .section {{ color:{TEXT}; font-size:16px; font-weight:600; margin:18px 0 8px 0; }}
  [data-testid="stDataFrame"] {{ background:{CARD}; }}
</style>
""", unsafe_allow_html=True)

def lyt():
    return dict(
        paper_bgcolor=DARK, plot_bgcolor=DARK, font_color=TEXT,
        margin=dict(t=30, b=20, l=10, r=10),
        legend=dict(bgcolor=CARD, bordercolor=BORD, borderwidth=1, font=dict(color=TEXT)),
    )

def kpi(col, label, value, delta=None, inverse=False, fmt=".2f", suffix=""):
    val_str = f"{value:{fmt}}{suffix}"
    delta_html = ""
    if delta is not None:
        diff = value - delta
        if diff == 0:   cls, sign = "kpi-neu", "="
        elif (diff > 0 and not inverse) or (diff < 0 and inverse): cls, sign = "kpi-pos", "+"
        else: cls, sign = "kpi-neg", "+"
        delta_html = f'<div class="{cls}">{sign}{diff:{fmt}}{suffix} vs adv.</div>'
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{val_str}</div>{delta_html}</div>', unsafe_allow_html=True)

def section(text):
    st.markdown(f'<div class="section">{text}</div>', unsafe_allow_html=True)

def pct_bar_overlay(fig, x, y_total, y_reussi, name_total, name_reussi, color_total, color_reussi):
    pct = (y_reussi / y_total.replace(0, float("nan")) * 100).round(1)
    fig.add_trace(go.Bar(x=x, y=y_total, name=name_total, marker_color=color_total))
    fig.add_trace(go.Bar(x=x, y=y_reussi, name=name_reussi, marker_color=color_reussi,
        text=[f"{v}%" for v in pct], textposition="inside", insidetextanchor="middle",
        textfont=dict(color=DARK, size=11, family="Arial Black")))
    return fig

def mirror_row(label, tl_v, adv_v, tl_max, adv_max, pct=False):
    w_tl  = round(tl_v  / tl_max  * 100, 1) if tl_max  > 0 else 0
    w_adv = round(adv_v / adv_max * 100, 1) if adv_max > 0 else 0
    tl_str  = f"{tl_v:.0f}%"  if pct else str(round(tl_v, 1))
    adv_str = f"{adv_v:.0f}%" if pct else str(round(adv_v, 1))
    row  = '<div style="display:grid;grid-template-columns:55px 1fr 160px 1fr 55px;align-items:center;gap:4px;padding:6px 0;border-bottom:0.5px solid #2a2a2a;">'
    row += f'<div style="text-align:right;font-size:13px;color:#fff;">{tl_str}</div>'
    row += f'<div style="background:#2a2a2a;border-radius:3px;height:16px;overflow:hidden;"><div style="width:{w_tl}%;height:100%;background:#9e9e9e;margin-left:auto;border-radius:3px;"></div></div>'
    row += f'<div style="text-align:center;font-size:12px;color:#8b949e;padding:0 4px;">{label}</div>'
    row += f'<div style="background:#2a2a2a;border-radius:3px;height:16px;overflow:hidden;"><div style="width:{w_adv}%;height:100%;background:#ff2d55;border-radius:3px;"></div></div>'
    row += f'<div style="text-align:left;font-size:13px;color:#fff;">{adv_str}</div>'
    row += '</div>'
    return row

def build_mirror(rows_html, tl_label, adv_label):
    h  = f'<div style="display:grid;grid-template-columns:55px 1fr 160px 1fr 55px;gap:4px;padding-bottom:8px;border-bottom:1px solid #2a2a2a;margin-bottom:4px;">'
    h += f'<div style="text-align:right;font-size:12px;color:#9e9e9e;font-weight:700;">{tl_label}</div><div></div><div></div><div></div>'
    h += f'<div style="text-align:left;font-size:12px;color:#ff2d55;font-weight:700;">{adv_label}</div></div>'
    return '<div style="background:#111111;border:1px solid #2a2a2a;border-radius:10px;padding:14px;">' + h + rows_html + '</div>'

def make_mirror_section(data_list, tl_label, adv_label):
    rows = ""
    for item in data_list:
        label, tl_v, adv_v, mode = item[0], item[1], item[2], item[3]
        if mode == "pct":
            rows += mirror_row(label, tl_v, adv_v, 100, 100, pct=True)
        elif mode == "vs":
            total = tl_v + adv_v if (tl_v + adv_v) > 0 else 1
            rows += mirror_row(label, tl_v, adv_v, total, total)
        elif mode == "self":
            tl_ref, adv_ref = item[4], item[5]
            rows += mirror_row(label, tl_v, adv_v, tl_ref if tl_ref > 0 else 1, adv_ref if adv_ref > 0 else 1)
    return build_mirror(rows, tl_label, adv_label)

# ──────────────────────────────────────────────────────────────────────────────
# TERRAIN SVG
# ──────────────────────────────────────────────────────────────────────────────

def make_pitch_svg(pct_high, pct_med, pct_low, color_hex, journee="", adversaire="", width=190, height=300):
    def op(pct):
        return round(0.10 + (pct / 100) * 0.65, 2)

    H, W = height, width
    zh   = H // 3  # hauteur zone

    gs_w = int(W * 0.62); gs_h = int(H * 0.15); gs_x = (W - gs_w) // 2
    ss_w = int(W * 0.37); ss_h = int(H * 0.06); ss_x = (W - ss_w) // 2
    bw   = int(W * 0.19); bh   = int(H * 0.025); bx = (W - bw) // 2
    cx   = W // 2;        cy   = H // 2;          cr = int(min(W, H) * 0.14)
    pp   = int(gs_h * 0.55)

    # Conteneur total : terrain + étiquette haut + étiquette bas + flèche
    TOTAL_H = H + 50
    ARROW_X = W + 10  # flèche à droite du terrain

    s = f'<svg width="{W+30}" height="{TOTAL_H}" viewBox="0 0 {W+30} {TOTAL_H}" xmlns="http://www.w3.org/2000/svg">'

    # Fond + bandes
    s += f'<rect x="0" y="25" width="{W}" height="{H}" fill="#6a9e4a"/>'
    for i in range(5):
        if i % 2 == 0:
            s += f'<rect x="0" y="{25+i*H//5}" width="{W}" height="{H//5}" fill="#5e8f40"/>'

    # Zones colorées
    s += f'<rect x="0" y="25" width="{W}" height="{zh}" fill="{color_hex}" opacity="{op(pct_high)}"/>'
    s += f'<rect x="0" y="{25+zh}" width="{W}" height="{zh}" fill="{color_hex}" opacity="{op(pct_med)}"/>'
    s += f'<rect x="0" y="{25+2*zh}" width="{W}" height="{zh}" fill="{color_hex}" opacity="{op(pct_low)}"/>'

    # Séparations zones
    s += f'<line x1="0" y1="{25+zh}"   x2="{W}" y2="{25+zh}"   stroke="white" stroke-width="1" stroke-dasharray="5,4" opacity="0.7"/>'
    s += f'<line x1="0" y1="{25+2*zh}" x2="{W}" y2="{25+2*zh}" stroke="white" stroke-width="1" stroke-dasharray="5,4" opacity="0.7"/>'

    # Bordure
    s += f'<rect x="0" y="25" width="{W}" height="{H}" fill="none" stroke="white" stroke-width="2"/>'

    # Ligne médiane
    s += f'<line x1="0" y1="{25+cy}" x2="{W}" y2="{25+cy}" stroke="white" stroke-width="1.5"/>'

    # Cercle central
    s += f'<circle cx="{cx}" cy="{25+cy}" r="{cr}" fill="none" stroke="white" stroke-width="1.5"/>'
    s += f'<circle cx="{cx}" cy="{25+cy}" r="2" fill="white"/>'

    # Surface haut (adversaire)
    s += f'<rect x="{gs_x}" y="25" width="{gs_w}" height="{gs_h}" fill="none" stroke="white" stroke-width="1.5"/>'
    s += f'<rect x="{ss_x}" y="25" width="{ss_w}" height="{ss_h}" fill="none" stroke="white" stroke-width="1.5"/>'
    s += f'<rect x="{bx}" y="{25-bh}" width="{bw}" height="{bh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s += f'<circle cx="{cx}" cy="{25+pp}" r="2" fill="white"/>'

    # Surface bas (notre but)
    s += f'<rect x="{gs_x}" y="{25+H-gs_h}" width="{gs_w}" height="{gs_h}" fill="none" stroke="white" stroke-width="1.5"/>'
    s += f'<rect x="{ss_x}" y="{25+H-ss_h}" width="{ss_w}" height="{ss_h}" fill="none" stroke="white" stroke-width="1.5"/>'
    s += f'<rect x="{bx}" y="{25+H}" width="{bw}" height="{bh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s += f'<circle cx="{cx}" cy="{25+H-pp}" r="2" fill="white"/>'

    # Badges %
    for i, (p, y_badge) in enumerate([(pct_high, 25+zh//2-11), (pct_med, 25+zh+zh//2-11), (pct_low, 25+2*zh+zh//2-11)]):
        s += f'<rect x="3" y="{y_badge}" width="42" height="21" fill="rgba(0,0,0,0.65)" rx="3"/>'
        s += f'<text x="24" y="{y_badge+15}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="white">{p:.0f}%</text>'

    # Flèche attaque (bas → haut) à droite du terrain
    ax = W + 4
    ay_start = 25 + H - 10
    ay_end   = 25 + 10
    s += f'<line x1="{ax}" y1="{ay_start}" x2="{ax}" y2="{ay_end}" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>'
    s += f'<polygon points="{ax},{ay_end} {ax-4},{ay_end+10} {ax+4},{ay_end+10}" fill="rgba(255,255,255,0.5)"/>'
    s += f'<text x="{ax}" y="{ay_start+12}" text-anchor="middle" font-family="Arial,sans-serif" font-size="8" fill="rgba(255,255,255,0.4)">ATT.</text>'

    # Journée + adversaire
    if journee:
        s += f'<text x="{cx}" y="16" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="white">{journee}</text>'
    if adversaire:
        adv_short = adversaire[:16]
        s += f'<text x="{cx}" y="{25+H+bh+14}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" fill="rgba(255,255,255,0.7)">{adv_short}</text>'

    s += '</svg>'
    return s

def render_pitches(rows_data, color_hex, cols_per_row=4):
    for i in range(0, len(rows_data), cols_per_row):
        batch = rows_data[i:i+cols_per_row]
        cols  = st.columns(len(batch))
        for j, d in enumerate(batch):
            svg = make_pitch_svg(
                pct_high=d["high"], pct_med=d["med"], pct_low=d["low"],
                color_hex=color_hex,
                journee=d.get("journee", ""),
                adversaire=d.get("adversaire", ""),
                width=170, height=270
            )
            cols[j].markdown(svg, unsafe_allow_html=True)

def get_pitch_data(df_gen, adv_names_list, journees_list, col_low, col_med, col_high, col_total):
    rows = []
    for i, row in df_gen.iterrows():
        total = row[col_total] if row[col_total] > 0 else 1
        rows.append({
            "journee":    journees_list[i],
            "adversaire": adv_names_list[i],
            "high": row[col_high] / total * 100,
            "med":  row[col_med]  / total * 100,
            "low":  row[col_low]  / total * 100,
        })
    return rows

def pitch_from_filtered(df_filtered, adv_map, col_low, col_med, col_high, col_total):
    """Génère données terrains à partir d'un df filtré."""
    rows = []
    for i, row in df_filtered.iterrows():
        total = row[col_total] if row[col_total] > 0 else 1
        journee = str(row["Journée"])
        adv_name = adv_map.get(row["Match"], "")
        rows.append({
            "journee": journee, "adversaire": adv_name,
            "high": row[col_high] / total * 100,
            "med":  row[col_med]  / total * 100,
            "low":  row[col_low]  / total * 100,
        })
    return rows

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    logo_path = Path(__file__).parent / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=120)
    st.markdown("## US Thionville Lusitanos")
    st.divider()

    comps_dispo  = sorted(gen_all["Competition"].dropna().unique().tolist())
    comp_options = {COMP_LABELS.get(c, c): c for c in comps_dispo}
    saison_label = st.selectbox("🏆 Saison", list(comp_options.keys()))
    saison_comp  = comp_options[saison_label]

    n_matchs = len(gen_all[(gen_all["Competition"] == saison_comp) & (gen_all["Team"] == TEAM)])
    st.markdown(f"<span style='color:{MUTED};font-size:13px;'>📊 {n_matchs} matchs analysés</span>", unsafe_allow_html=True)
    st.divider()

    page = st.radio("Menu", [
        "🏠 Vue d'ensemble",
        "🎯 Finition",
        "🛡️ Pressing",
        "🔁 En possession",
        "📅 Analyse par match",
    ])

# ──────────────────────────────────────────────────────────────────────────────
# FILTRAGE SAISON
# ──────────────────────────────────────────────────────────────────────────────

def fc(df): return df[df["Competition"] == saison_comp].copy()

gen   = fc(gen_all);  off  = fc(off_all);  defe  = fc(defe_all)
passe = fc(passe_all); idx = fc(idx_all)

thi_gen  = gen[gen["Team"] == TEAM].sort_values("Journée").reset_index(drop=True)
adv_gen  = gen[gen["Team"] != TEAM].sort_values("Journée").reset_index(drop=True)
thi_off  = off[off["Team"] == TEAM].sort_values("Journée").reset_index(drop=True)
adv_off  = off[off["Team"] != TEAM].sort_values("Journée").reset_index(drop=True)
thi_def  = defe[defe["Team"] == TEAM].sort_values("Journée").reset_index(drop=True)
adv_def  = defe[defe["Team"] != TEAM].sort_values("Journée").reset_index(drop=True)
thi_pass = passe[passe["Team"] == TEAM].sort_values("Journée").reset_index(drop=True)
adv_pass = passe[passe["Team"] != TEAM].sort_values("Journée").reset_index(drop=True)
thi_idx  = idx[idx["Team"] == TEAM].sort_values("Journée").reset_index(drop=True)
adv_idx  = idx[idx["Team"] != TEAM].sort_values("Journée").reset_index(drop=True)

if len(thi_gen) == 0:
    st.warning("Aucune donnée disponible pour cette saison.")
    st.stop()

adv_names    = [adv_gen[adv_gen["Match"] == thi_gen.iloc[i]["Match"]]["Team"].values[0] for i in range(len(thi_gen))]
journees     = [str(j) for j in thi_gen["Journée"]]
journees_adv = [f"{journees[i]}\n{adv_names[i]}" for i in range(len(thi_gen))]

# Map match → adversaire
adv_map = {thi_gen.iloc[i]["Match"]: adv_names[i] for i in range(len(thi_gen))}

def get_result(rt, ra):
    if rt["Goals"] > ra["Goals"]: return "V"
    if rt["Goals"] == ra["Goals"]: return "N"
    return "D"

resultats     = [get_result(thi_gen.iloc[i], adv_gen[adv_gen["Match"] == thi_gen.iloc[i]["Match"]].iloc[0]) for i in range(len(thi_gen))]
bar_colors    = [{"V": GREEN, "N": GOLD, "D": RED}[r] for r in resultats]
buts_adv_list = [adv_gen[adv_gen["Match"] == row["Match"]]["Goals"].values[0] for _, row in thi_gen.iterrows()]

thi_gen["pct_recup_high"] = thi_gen["Recoveries High"] / thi_gen["Recoveries"].replace(0, float("nan")) * 100
thi_gen["pct_losses_low"] = thi_gen["Losses Low "]     / thi_gen["Losses"].replace(0, float("nan"))      * 100
thi_gen["ratio_pression"] = (thi_gen["pct_recup_high"] / thi_gen["pct_losses_low"].replace(0, float("nan"))).round(2)
thi_off["CPA_with_shots"] = thi_off["Corners with shots"] + thi_off["Free kicks with shots"]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — VUE D'ENSEMBLE
# ══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Vue d'ensemble":
    st.markdown(f"# 🏠 Vue d'ensemble — {saison_label}")

    section("Résultats")
    cols_res = st.columns(len(thi_gen))
    for i, row in thi_gen.iterrows():
        adv_row = adv_gen[adv_gen["Match"] == row["Match"]].iloc[0]
        res = resultats[i]
        couleur = {"V": GREEN, "N": GOLD, "D": RED}[res]
        emoji   = {"V": "🟢", "N": "🟠", "D": "🔴"}[res]
        cols_res[i].markdown(
            f'<div style="background:{CARD};border:1px solid {couleur};border-radius:10px;'
            f'padding:10px 8px;text-align:center;">'
            f'<div style="font-size:11px;color:{MUTED};">{journees[i]}</div>'
            f'<div style="font-size:11px;color:{TEXT};margin:2px 0;">{adv_names[i][:12]}</div>'
            f'<div style="font-size:20px;font-weight:700;color:{couleur};">{int(row["Goals"])}–{int(adv_row["Goals"])}</div>'
            f'<div style="font-size:11px;">{emoji}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi(c1, "⚽ Buts / match",      thi_gen["Goals"].mean(),           adv_gen["Goals"].mean(),           fmt=".2f")
    kpi(c2, "🚫 Buts concédés / m", thi_def["Conceded goals"].mean(),  None,                              fmt=".2f", inverse=True)
    kpi(c3, "🎯 xG / match",        thi_gen["xG"].mean(),              adv_gen["xG"].mean(),              fmt=".2f")
    kpi(c4, "🔵 Possession moy.",   thi_gen["% Possession"].mean(),    adv_gen["% Possession"].mean(),    fmt=".1f", suffix="%")
    kpi(c5, "💨 Tirs / match",      thi_gen["Shots"].mean(),           adv_gen["Shots"].mean(),           fmt=".1f")
    kpi(c6, "🤼 Duels gagnés %",    thi_gen["% Duels won"].mean(),     adv_gen["% Duels won"].mean(),     fmt=".1f", suffix="%")

    st.markdown("")
    section("Comparaison des moyennes — US Thionville vs Adversaires")
    ov_data = [
        ("Buts / match",      thi_gen["Goals"].mean(),             adv_gen["Goals"].mean(),             "vs"),
        ("xG / match",        thi_gen["xG"].mean(),                adv_gen["xG"].mean(),                "vs"),
        ("Tirs / match",      thi_gen["Shots"].mean(),             adv_gen["Shots"].mean(),             "vs"),
        ("Tirs cadrés / m",   thi_gen["Shots on target"].mean(),   adv_gen["Shots on target"].mean(),   "vs"),
        ("Possession %",      thi_gen["% Possession"].mean(),      adv_gen["% Possession"].mean(),      "pct"),
        ("Passes / match",    thi_gen["Passes"].mean(),            adv_gen["Passes"].mean(),            "vs"),
        ("Passes réuss. %",   thi_gen["% Passes accurate"].mean(), adv_gen["% Passes accurate"].mean(), "pct"),
        ("Récupérations / m", thi_gen["Recoveries"].mean(),        adv_gen["Recoveries"].mean(),        "vs"),
        ("Pertes / match",    thi_gen["Losses"].mean(),            adv_gen["Losses"].mean(),            "vs"),
        ("Duels gagnés %",    thi_gen["% Duels won"].mean(),       adv_gen["% Duels won"].mean(),       "pct"),
    ]
    st.markdown(make_mirror_section(ov_data, "TL", "Adversaires"), unsafe_allow_html=True)

    st.markdown("")

    # ── Terrains avec filtre matchs ──
    section("Pertes & Récupérations par zone")

    # Filtre multi-matchs
    match_labels_sel = [f"{journees[i]} — {adv_names[i]}" for i in range(len(thi_gen))]
    selected = st.multiselect(
        "Filtrer par match(s) — laisser vide pour afficher les moyennes",
        options=match_labels_sel,
        default=[]
    )

    if selected:
        # Indices des matchs sélectionnés
        sel_idx = [match_labels_sel.index(s) for s in selected]
        df_sel  = thi_gen.iloc[sel_idx].reset_index(drop=True)
        adv_sel = [adv_names[i] for i in sel_idx]
        jour_sel = [journees[i] for i in sel_idx]

        # Calcul moyennes sur sélection
        tot_loss = df_sel["Losses"].mean()
        tot_rec  = df_sel["Recoveries"].mean()

        loss_high = df_sel["Losses High"].mean()   / tot_loss * 100
        loss_med  = df_sel["Losses Medium"].mean() / tot_loss * 100
        loss_low  = df_sel["Losses Low "].mean()   / tot_loss * 100

        rec_high  = df_sel["Recoveries High"].mean()   / tot_rec * 100
        rec_med   = df_sel["Recoveries Medium"].mean() / tot_rec * 100
        rec_low   = df_sel["Recoveries Low"].mean()    / tot_rec * 100

        titre_sel = ", ".join(selected)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f"**Pertes** — {titre_sel}")
            svg = make_pitch_svg(loss_high, loss_med, loss_low, "#ff5500", width=280, height=440)
            st.markdown(f'<div style="display:flex;justify-content:center;">{svg}</div>', unsafe_allow_html=True)
        with col_r:
            st.markdown(f"**Récupérations** — {titre_sel}")
            svg = make_pitch_svg(rec_high, rec_med, rec_low, "#00dd55", width=280, height=440)
            st.markdown(f'<div style="display:flex;justify-content:center;">{svg}</div>', unsafe_allow_html=True)
    else:
        # Moyennes saison
        tot_loss = thi_gen["Losses"].mean()
        tot_rec  = thi_gen["Recoveries"].mean()

        loss_high = thi_gen["Losses High"].mean()   / tot_loss * 100
        loss_med  = thi_gen["Losses Medium"].mean() / tot_loss * 100
        loss_low  = thi_gen["Losses Low "].mean()   / tot_loss * 100

        rec_high  = thi_gen["Recoveries High"].mean()   / tot_rec * 100
        rec_med   = thi_gen["Recoveries Medium"].mean() / tot_rec * 100
        rec_low   = thi_gen["Recoveries Low"].mean()    / tot_rec * 100

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**Pertes** — Moyennes saison")
            svg = make_pitch_svg(loss_high, loss_med, loss_low, "#ff5500", width=280, height=440)
            st.markdown(f'<div style="display:flex;justify-content:center;">{svg}</div>', unsafe_allow_html=True)
        with col_r:
            st.markdown("**Récupérations** — Moyennes saison")
            svg = make_pitch_svg(rec_high, rec_med, rec_low, "#00dd55", width=280, height=440)
            st.markdown(f'<div style="display:flex;justify-content:center;">{svg}</div>', unsafe_allow_html=True)

    st.markdown("")
    section("xG attendu — marqué vs concédé — par journée")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=journees_adv, y=thi_gen["xG"], name="xG TL", marker_color=GREY, text=thi_gen["xG"].round(2), textposition="outside"))
    fig2.add_trace(go.Bar(x=journees_adv, y=adv_gen["xG"], name="xG Adversaires", marker_color=RED, text=adv_gen["xG"].round(2), textposition="outside"))
    fig2.update_layout(**lyt(), barmode="group", height=300)
    fig2.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — FINITION
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🎯 Finition":
    st.markdown(f"# 🎯 Finition — {saison_label}")
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "⚽ Buts / match",  thi_gen["Goals"].mean(),             adv_gen["Goals"].mean(),             fmt=".2f")
    kpi(c2, "🎯 xG / match",    thi_off["xG"].mean(),                adv_off["xG"].mean(),                fmt=".2f")
    kpi(c3, "💨 Tirs / match",  thi_off["Shots"].mean(),             adv_off["Shots"].mean(),             fmt=".1f")
    kpi(c4, "🎯 Tirs cadrés %", thi_off["% Shots on target"].mean(), adv_off["% Shots on target"].mean(), fmt=".1f", suffix="%")
    st.markdown("")

    section("Buts marqués vs xG  (🟢V · 🟠N · 🔴D)")
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=journees_adv, y=thi_gen["Goals"], name="Buts", marker_color=bar_colors, text=thi_gen["Goals"].astype(int), textposition="outside"))
    fig5.add_trace(go.Scatter(x=journees_adv, y=thi_gen["xG"], name="xG", mode="lines+markers", line=dict(color=GREY, width=2), marker=dict(size=7)))
    fig5.update_layout(**lyt(), height=300); fig5.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig5, use_container_width=True)

    section("Tirs totaux vs cadrés par journée")
    fig7 = go.Figure()
    fig7 = pct_bar_overlay(fig7, journees_adv, thi_gen["Shots"], thi_gen["Shots on target"], "Total", "Cadrés", "rgba(158,158,158,.35)", GREY)
    fig7.update_layout(**lyt(), barmode="overlay", height=260); fig7.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig7, use_container_width=True)

    section("Distance moyenne des tirs (m) par journée")
    fig29 = go.Figure()
    fig29.add_trace(go.Bar(x=journees_adv, y=thi_idx["Average shot distance"], name="US Thionville", marker_color=GREY, text=thi_idx["Average shot distance"].round(1), textposition="outside"))
    fig29.add_trace(go.Bar(x=journees_adv, y=adv_idx["Average shot distance"], name="Adversaires", marker_color=RED, text=adv_idx["Average shot distance"].round(1), textposition="outside"))
    fig29.update_layout(**lyt(), barmode="group", height=290); fig29.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig29, use_container_width=True)

    section("Tirs par phase de jeu par journée")
    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=journees_adv, y=thi_off["Positional attacks with shots"], name="Att. positionnelle", marker_color=GREY))
    fig_p.add_trace(go.Bar(x=journees_adv, y=thi_off["Counterattacks with shots"], name="Contre-attaque", marker_color=RED))
    fig_p.add_trace(go.Bar(x=journees_adv, y=thi_off["CPA_with_shots"], name="CPA", marker_color=GOLD))
    fig_p.update_layout(**lyt(), barmode="group", height=300); fig_p.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig_p, use_container_width=True)

    section("% attaques avec tir — TL vs Adversaires")
    eff_types = ["Positionnelles", "Contres", "Corners", "Coups francs"]
    eff_t = [thi_off["% Positional attacks with shots"].mean(), thi_off["% Counterattacks with shots"].mean(), thi_off["% Corners with shots"].mean(), thi_off["% Free kicks with shots"].mean()]
    eff_a = [adv_off["% Positional attacks with shots"].mean(), adv_off["% Counterattacks with shots"].mean(), adv_off["% Corners with shots"].mean(), adv_off["% Free kicks with shots"].mean()]
    fig11 = go.Figure()
    fig11.add_trace(go.Bar(x=eff_types, y=eff_t, name="US Thionville", marker_color=GREY, text=[f"{v:.1f}%" for v in eff_t], textposition="outside"))
    fig11.add_trace(go.Bar(x=eff_types, y=eff_a, name="Adversaires", marker_color=RED, text=[f"{v:.1f}%" for v in eff_a], textposition="outside"))
    fig11.update_layout(**lyt(), barmode="group", height=310); fig11.update_yaxes(range=[0,100], gridcolor=BORD)
    st.plotly_chart(fig11, use_container_width=True)

    section("Attaques positionnelles — total vs avec tir")
    fig12 = go.Figure()
    fig12 = pct_bar_overlay(fig12, journees_adv, thi_off["Positional attacks"], thi_off["Positional attacks with shots"], "Total", "Avec tir", "rgba(158,158,158,.35)", GREY)
    fig12.update_layout(**lyt(), barmode="overlay", height=260); fig12.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig12, use_container_width=True)

    section("Centres — total vs réussis")
    fig13 = go.Figure()
    fig13 = pct_bar_overlay(fig13, journees_adv, thi_off["Crosses"], thi_off["Crosses accurate"], "Total", "Réussis", "rgba(158,158,158,.35)", GREY)
    fig13.update_layout(**lyt(), barmode="overlay", height=260); fig13.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig13, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — PRESSING
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🛡️ Pressing":
    st.markdown(f"# 🛡️ Pressing — {saison_label}")
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "🚫 Buts concédés / m",  thi_def["Conceded goals"].mean(),               None,                                           fmt=".2f", inverse=True)
    kpi(c2, "📉 Tirs subis / m",     thi_def["Shots against"].mean(),                adv_def["Shots against"].mean(),                fmt=".1f", inverse=True)
    kpi(c3, "🛡️ Tacles réussis %",  thi_def["% Sliding tackles successful"].mean(), adv_def["% Sliding tackles successful"].mean(), fmt=".1f", suffix="%")
    kpi(c4, "✋ Interceptions / m",  thi_def["Interceptions"].mean(),                adv_def["Interceptions"].mean(),                fmt=".1f")
    kpi(c5, "🤼 Duels gagnés / m",   thi_gen["Duels won"].mean(),                    adv_gen["Duels won"].mean(),                    fmt=".1f")
    st.markdown("")

    section("Récupérations par zone — par journée")
    rec_data = get_pitch_data(thi_gen, adv_names, journees, "Recoveries Low", "Recoveries Medium", "Recoveries High", "Recoveries")
    render_pitches(rec_data, "#00dd55", cols_per_row=4)
    st.markdown("")

    section("PPDA par journée  (↓ = pression haute)")
    ppda_moy = thi_idx["PPDA"].mean()
    fig_ppda = go.Figure()
    fig_ppda.add_trace(go.Bar(x=journees_adv, y=thi_idx["PPDA"], name="PPDA TL", marker_color=GREY, text=thi_idx["PPDA"].round(2), textposition="outside"))
    fig_ppda.add_hline(y=ppda_moy, line_dash="dash", line_color=GOLD, annotation_text=f"Moyenne : {ppda_moy:.2f}", annotation_font_color=GOLD, annotation_position="top right")
    fig_ppda.update_layout(**lyt(), height=300); fig_ppda.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig_ppda, use_container_width=True)

    section("Ratio % récupérations en zone offensive ÷ % pertes en zone défensive")
    st.caption("Ratio > 1 🟢 = dynamique favorable  |  Ratio < 1 🔴 = inverse")
    ratio_moy    = thi_gen["ratio_pression"].mean()
    ratio_colors = [GREEN if v >= 1.0 else GOLD if v >= 0.7 else RED for v in thi_gen["ratio_pression"]]
    fig_ratio = go.Figure()
    fig_ratio.add_trace(go.Bar(x=journees_adv, y=thi_gen["ratio_pression"], name="Ratio", marker_color=ratio_colors, text=thi_gen["ratio_pression"].astype(str), textposition="outside"))
    fig_ratio.add_hline(y=1.0, line_dash="dash", line_color=GOLD, annotation_text="Équilibre : 1.0", annotation_font_color=GOLD, annotation_position="top right")
    fig_ratio.add_hline(y=ratio_moy, line_dash="dot", line_color=GREY, annotation_text=f"Moy. : {ratio_moy:.2f}", annotation_font_color=TEXT, annotation_position="bottom right")
    fig_ratio.update_layout(**lyt(), height=300); fig_ratio.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig_ratio, use_container_width=True)

    section("% récupérations en zone offensive par journée  (seuil : 13%)")
    pct_recup_off = thi_gen["pct_recup_high"].round(1)
    SEUIL = 13.0
    fig_ro = go.Figure()
    fig_ro.add_trace(go.Bar(x=journees_adv, y=pct_recup_off, name="% Récup. zone off.", marker_color=[GREEN if v >= SEUIL else RED for v in pct_recup_off], text=[f"{v}%" for v in pct_recup_off], textposition="outside", textfont=dict(color=TEXT)))
    fig_ro.add_hline(y=SEUIL, line_dash="dash", line_color=RED, annotation_text=f"Seuil : {SEUIL}%", annotation_font_color=RED, annotation_position="top right")
    fig_ro.add_hline(y=pct_recup_off.mean(), line_dash="dot", line_color=GREY, annotation_text=f"Moy. : {pct_recup_off.mean():.1f}%", annotation_font_color=TEXT, annotation_position="bottom right")
    fig_ro.update_layout(**lyt(), height=300); fig_ro.update_yaxes(gridcolor=BORD, range=[0, max(pct_recup_off)*1.3])
    st.caption(f"🟢 ≥ {SEUIL}% · 🔴 < {SEUIL}%")
    st.plotly_chart(fig_ro, use_container_width=True)

    section("Pertes de balle vs Récupérations par journée")
    fig9 = go.Figure()
    fig9.add_trace(go.Bar(x=journees_adv, y=thi_gen["Losses"], name="Pertes", marker_color=RED))
    fig9.add_trace(go.Bar(x=journees_adv, y=thi_gen["Recoveries"], name="Récupérations", marker_color=GREY))
    fig9.update_layout(**lyt(), barmode="group", height=260); fig9.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig9, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section("Duels défensifs gagnés (%) par journée")
        fig16 = go.Figure()
        fig16.add_trace(go.Scatter(x=journees_adv, y=thi_def["% Defensive duels won"], mode="lines+markers", line=dict(color=GREY, width=2), fill="tozeroy", fillcolor="rgba(158,158,158,.1)", name="Duels déf %"))
        moy = thi_def["% Defensive duels won"].mean()
        fig16.add_hline(y=moy, line_dash="dash", line_color=GOLD, annotation_text=f"moy. {moy:.1f}%", annotation_font_color=GOLD)
        fig16.update_layout(**lyt(), height=260); fig16.update_yaxes(range=[40,90], gridcolor=BORD)
        st.plotly_chart(fig16, use_container_width=True)
    with col_b:
        section("Duels aériens gagnés (%) par journée")
        fig17 = go.Figure()
        fig17.add_trace(go.Scatter(x=journees_adv, y=thi_def["% Aerial duels won"], mode="lines+markers", line=dict(color=GREY, width=2), fill="tozeroy", fillcolor="rgba(158,158,158,.1)", name="Duels aér %"))
        moy2 = thi_def["% Aerial duels won"].mean()
        fig17.add_hline(y=moy2, line_dash="dash", line_color=GOLD, annotation_text=f"moy. {moy2:.1f}%", annotation_font_color=GOLD)
        fig17.update_layout(**lyt(), height=260); fig17.update_yaxes(range=[20,90], gridcolor=BORD)
        st.plotly_chart(fig17, use_container_width=True)

    section("Buts marqués vs concédés par journée")
    fig8 = go.Figure()
    fig8.add_trace(go.Scatter(x=journees_adv, y=thi_gen["Goals"], name="Marqués", mode="lines+markers", line=dict(color=GREY, width=2)))
    fig8.add_trace(go.Scatter(x=journees_adv, y=buts_adv_list, name="Concédés", mode="lines+markers", line=dict(color=RED, width=2)))
    fig8.update_layout(**lyt(), height=260); fig8.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig8, use_container_width=True)

    section("Buts concédés & tirs subis par journée")
    fig15 = make_subplots(specs=[[{"secondary_y": True}]])
    fig15.add_trace(go.Bar(x=journees_adv, y=thi_def["Conceded goals"], name="Buts concédés", marker_color=RED, text=thi_def["Conceded goals"].astype(int), textposition="outside"), secondary_y=False)
    fig15.add_trace(go.Scatter(x=journees_adv, y=thi_def["Shots against"], name="Tirs subis", mode="lines+markers", line=dict(color=GREY, width=2)), secondary_y=True)
    fig15.update_layout(**lyt(), height=300); fig15.update_yaxes(gridcolor=BORD, secondary_y=False)
    st.plotly_chart(fig15, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        section("Interceptions & Dégagements par journée")
        fig18 = go.Figure()
        fig18.add_trace(go.Bar(x=journees_adv, y=thi_def["Interceptions"], name="Interceptions", marker_color=GREEN))
        fig18.add_trace(go.Bar(x=journees_adv, y=thi_def["Clearances"], name="Dégagements", marker_color=GREY))
        fig18.update_layout(**lyt(), barmode="group", height=260); fig18.update_yaxes(gridcolor=BORD)
        st.plotly_chart(fig18, use_container_width=True)
    with col_d:
        section("Discipline — cartons par journée")
        fig19 = go.Figure()
        fig19.add_trace(go.Bar(x=journees_adv, y=thi_def["Yellow cards"], name="Jaunes", marker_color=GOLD))
        fig19.add_trace(go.Bar(x=journees_adv, y=thi_def["Red cards"], name="Rouges", marker_color=RED))
        fig19.update_layout(**lyt(), barmode="stack", height=260); fig19.update_yaxes(gridcolor=BORD)
        st.plotly_chart(fig19, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — EN POSSESSION
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🔁 En possession":
    st.markdown(f"# 🔁 En possession — {saison_label}")
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "📊 Passes / match",     thi_pass["Passes"].mean(),                 adv_pass["Passes"].mean(),                fmt=".0f")
    kpi(c2, "✅ Précision globale",   thi_pass["% Passes accurate"].mean(),      adv_pass["% Passes accurate"].mean(),     fmt=".1f", suffix="%")
    kpi(c3, "➡️ Passes prog. / m",  thi_pass["Progressive passes"].mean(),      adv_pass["Progressive passes"].mean(),    fmt=".1f")
    kpi(c4, "🏁 Passes tiers final", thi_pass["Passes to final third"].mean(),   adv_pass["Passes to final third"].mean(), fmt=".1f")
    st.markdown("")

    section("Pertes de balle par zone — par journée")
    loss_data = get_pitch_data(thi_gen, adv_names, journees, "Losses Low ", "Losses Medium", "Losses High", "Losses")
    render_pitches(loss_data, "#ff5500", cols_per_row=4)
    st.markdown("")

    section("Tempo du match (actions / min) par journée")
    fig26 = go.Figure()
    fig26.add_trace(go.Bar(x=journees_adv, y=thi_idx["Match tempo"], name="US Thionville", marker_color=GREY, text=thi_idx["Match tempo"].round(2), textposition="outside"))
    fig26.add_trace(go.Scatter(x=journees_adv, y=adv_idx["Match tempo"], name="Adversaires", mode="lines+markers", line=dict(color=RED, dash="dot", width=2)))
    fig26.update_layout(**lyt(), height=290); fig26.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig26, use_container_width=True)

    section("Passes totales vs réussies par journée")
    fig20 = go.Figure()
    fig20 = pct_bar_overlay(fig20, journees_adv, thi_pass["Passes"], thi_pass["Passes accurate"], "Total", "Réussies", "rgba(158,158,158,.35)", GREY)
    fig20.update_layout(**lyt(), barmode="overlay", height=280); fig20.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig20, use_container_width=True)

    section("Passes par possession — TL vs Adversaires")
    ppp_moy = thi_idx["Average passes per possession"].mean()
    fig_ppp = go.Figure()
    fig_ppp.add_trace(go.Bar(x=journees_adv, y=thi_idx["Average passes per possession"], name="US Thionville", marker_color=GREY, text=thi_idx["Average passes per possession"].round(2), textposition="outside"))
    fig_ppp.add_trace(go.Scatter(x=journees_adv, y=adv_idx["Average passes per possession"], name="Adversaires", mode="lines+markers", line=dict(color=RED, width=2, dash="dot")))
    fig_ppp.add_hline(y=ppp_moy, line_dash="dash", line_color=GOLD, annotation_text=f"Moy. TL : {ppp_moy:.2f}", annotation_font_color=GOLD, annotation_position="top right")
    fig_ppp.update_layout(**lyt(), height=300); fig_ppp.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig_ppp, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section("Précision par type de passe (% moy.)")
        pct_lbl = ["Avant", "Latérales", "Arrière", "Longues", "Tiers final", "Progressives"]
        pct_t = [thi_pass["% Forward passes accurate"].mean(), thi_pass["% Lateral passes accurate"].mean(), thi_pass["% Back passes accurate"].mean(), thi_pass["% Long passes accurate"].mean(), thi_pass["% Passes to final third accurate"].mean(), thi_pass["% Progressive passes accurate"].mean()]
        pct_a = [adv_pass["% Forward passes accurate"].mean(), adv_pass["% Lateral passes accurate"].mean(), adv_pass["% Back passes accurate"].mean(), adv_pass["% Long passes accurate"].mean(), adv_pass["% Passes to final third accurate"].mean(), adv_pass["% Progressive passes accurate"].mean()]
        fig22 = go.Figure()
        fig22.add_trace(go.Bar(x=pct_lbl, y=pct_t, name="US Thionville", marker_color=GREY, text=[f"{v:.1f}%" for v in pct_t], textposition="outside"))
        fig22.add_trace(go.Bar(x=pct_lbl, y=pct_a, name="Adversaires", marker_color=RED, text=[f"{v:.1f}%" for v in pct_a], textposition="outside"))
        fig22.update_layout(**lyt(), barmode="group", height=290); fig22.update_yaxes(range=[0,115], gridcolor=BORD)
        st.plotly_chart(fig22, use_container_width=True)
    with col_b:
        section("Hors-jeu par journée")
        fig14 = go.Figure(go.Bar(x=journees_adv, y=thi_off["Offsides"], marker_color=GOLD, text=thi_off["Offsides"].astype(int), textposition="outside"))
        fig14.update_layout(**lyt(), height=290); fig14.update_yaxes(gridcolor=BORD)
        st.plotly_chart(fig14, use_container_width=True)

    section("Passes vers le tiers final — total vs réussies")
    fig23 = go.Figure()
    fig23 = pct_bar_overlay(fig23, journees_adv, thi_pass["Passes to final third"], thi_pass["Passes to final third accurate"], "Total", "Réussies", "rgba(158,158,158,.35)", GREY)
    fig23.update_layout(**lyt(), barmode="overlay", height=250); fig23.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig23, use_container_width=True)

    section("Passes progressives — total vs réussies")
    fig24 = go.Figure()
    fig24 = pct_bar_overlay(fig24, journees_adv, thi_pass["Progressive passes"], thi_pass["Progressive passes accurate"], "Total", "Réussies", "rgba(158,158,158,.35)", GREY)
    fig24.update_layout(**lyt(), barmode="overlay", height=250); fig24.update_yaxes(gridcolor=BORD)
    st.plotly_chart(fig24, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — ANALYSE PAR MATCH
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📅 Analyse par match":
    st.markdown("# 📅 Analyse par match")

    match_options = {journees[i]: thi_gen.iloc[i]["Match"] for i in range(len(thi_gen))}
    journee_sel   = st.selectbox("Sélectionner une journée", list(match_options.keys()),
        format_func=lambda j: f"{j} — vs {adv_names[journees.index(j)]}")
    match_sel = match_options[journee_sel]

    i_match = thi_gen[thi_gen["Match"] == match_sel].index[0]
    r_tg = thi_gen.loc[i_match]; r_ag = adv_gen[adv_gen["Match"] == match_sel].iloc[0]
    r_to = thi_off[thi_off["Match"] == match_sel].iloc[0]; r_ao = adv_off[adv_off["Match"] == match_sel].iloc[0]
    r_td = thi_def[thi_def["Match"] == match_sel].iloc[0]; r_ad = adv_def[adv_def["Match"] == match_sel].iloc[0]
    r_tp = thi_pass[thi_pass["Match"] == match_sel].iloc[0]; r_ap = adv_pass[adv_pass["Match"] == match_sel].iloc[0]
    r_ti = thi_idx[thi_idx["Match"] == match_sel].iloc[0];  r_ai = adv_idx[adv_idx["Match"] == match_sel].iloc[0]

    adv_name  = r_ag["Team"]
    res       = get_result(r_tg, r_ag)
    emoji_res = {"V": "🟢 Victoire", "N": "🟠 Nul", "D": "🔴 Défaite"}[res]

    st.markdown(f"### {journee_sel} — US Thionville Lusitanos **{int(r_tg['Goals'])} – {int(r_ag['Goals'])}** {adv_name} — {emoji_res}")
    st.caption(f"{r_tg['Date'].strftime('%d/%m/%Y')} · {int(r_tg['Duration'])} min · Schéma : {r_tg['Scheme']}")

    section("Comparaison des métriques clés")
    passes_tl  = int(r_tg["Passes"]) if int(r_tg["Passes"]) > 0 else 1
    passes_adv = int(r_ag["Passes"]) if int(r_ag["Passes"]) > 0 else 1

    match_metrics = [
        ("Buts",              int(r_tg["Goals"]),                  int(r_ag["Goals"]),              "vs"),
        ("xG",                round(r_tg["xG"],2),                 round(r_ag["xG"],2),             "vs"),
        ("Tirs",              int(r_tg["Shots"]),                  int(r_ag["Shots"]),              "vs"),
        ("Tirs cadrés",       int(r_tg["Shots on target"]),        int(r_ag["Shots on target"]),    "self", int(r_tg["Shots"]), int(r_ag["Shots"])),
        ("Possession %",      round(r_tg["% Possession"],1),       round(r_ag["% Possession"],1),   "pct"),
        ("Passes",            int(r_tg["Passes"]),                 int(r_ag["Passes"]),             "vs"),
        ("Passes réussies %", round(r_tg["% Passes accurate"],1),  round(r_ag["% Passes accurate"],1), "pct"),
        ("Passes réussies",   int(r_tg["Passes accurate"]),        int(r_ag["Passes accurate"]),    "self", passes_tl, passes_adv),
        ("Pertes de balle",   int(r_tg["Losses"]),                 int(r_ag["Losses"]),             "vs"),
        ("Récupérations",     int(r_tg["Recoveries"]),             int(r_ag["Recoveries"]),         "vs"),
        ("Duels gagnés %",    round(r_tg["% Duels won"],1),        round(r_ag["% Duels won"],1),    "pct"),
        ("Att. posit.",       int(r_to["Positional attacks"]),      int(r_ao["Positional attacks"]), "vs"),
        ("Centres",           int(r_to["Crosses"]),                int(r_ao["Crosses"]),            "vs"),
        ("Interceptions",     int(r_td["Interceptions"]),          int(r_ad["Interceptions"]),      "vs"),
        ("Dégagements",       int(r_td["Clearances"]),             int(r_ad["Clearances"]),         "vs"),
        ("Fautes",            int(r_td["Fouls"]),                  int(r_ad["Fouls"]),              "vs"),
    ]

    rows_html = ""
    for item in match_metrics:
        label, tl, adv_v, mode = item[0], item[1], item[2], item[3]
        if mode == "pct":    pct_tl, pct_adv = tl, adv_v
        elif mode == "vs":
            total = tl + adv_v if (tl + adv_v) > 0 else 1
            pct_tl = tl / total * 100; pct_adv = adv_v / total * 100
        elif mode == "self":
            tl_ref, adv_ref = item[4], item[5]
            pct_tl = tl / (tl_ref if tl_ref > 0 else 1) * 100
            pct_adv = adv_v / (adv_ref if adv_ref > 0 else 1) * 100
        row  = '<div style="display:grid;grid-template-columns:80px 1fr 160px 1fr 80px;align-items:center;gap:6px;padding:5px 0;border-bottom:0.5px solid #2a2a2a;">'
        row += f'<div style="text-align:right;font-size:14px;font-weight:500;color:#fff;">{tl}</div>'
        row += f'<div style="background:#2a2a2a;border-radius:3px;height:18px;overflow:hidden;"><div style="width:{pct_tl:.1f}%;height:100%;background:#9e9e9e;margin-left:auto;border-radius:3px;"></div></div>'
        row += f'<div style="text-align:center;font-size:12px;color:#8b949e;font-weight:500;">{label}</div>'
        row += f'<div style="background:#2a2a2a;border-radius:3px;height:18px;overflow:hidden;"><div style="width:{pct_adv:.1f}%;height:100%;background:#ff2d55;border-radius:3px;"></div></div>'
        row += f'<div style="text-align:left;font-size:14px;font-weight:500;color:#fff;">{adv_v}</div>'
        row += '</div>'
        rows_html += row

    hh  = '<div style="background:#111111;border:1px solid #2a2a2a;border-radius:10px;padding:16px;">'
    hh += '<div style="display:grid;grid-template-columns:80px 1fr 160px 1fr 80px;gap:6px;padding-bottom:8px;border-bottom:1px solid #2a2a2a;margin-bottom:4px;">'
    hh += '<div style="text-align:right;font-size:12px;color:#9e9e9e;font-weight:600;">TL</div><div></div><div></div><div></div>'
    hh += f'<div style="text-align:left;font-size:12px;color:#ff2d55;font-weight:600;">{adv_name}</div></div>' + rows_html + '</div>'
    st.markdown(hh, unsafe_allow_html=True)

    st.markdown("")

    # Tableaux en pleine largeur empilés (plus lisible)
    section("Phases de jeu")
    off_data = [
        ("xG",               r_to["xG"],r_ao["xG"],"vs"),
        ("Tirs",             r_to["Shots"],r_ao["Shots"],"vs"),
        ("Tirs cadrés",      r_to["Shots on target"],r_ao["Shots on target"],"self",int(r_tg["Shots"]),int(r_ag["Shots"])),
        ("Dist.moy.tir(m)",  r_ti["Average shot distance"],r_ai["Average shot distance"],"vs"),
        ("Att. posit.",      r_to["Positional attacks"],r_ao["Positional attacks"],"vs"),
        ("Att.posit.+tir",   r_to["Positional attacks with shots"],r_ao["Positional attacks with shots"],"vs"),
        ("% att.posit.tir",  r_to["% Positional attacks with shots"],r_ao["% Positional attacks with shots"],"pct"),
        ("Contres",          r_to["Counterattacks"],r_ao["Counterattacks"],"vs"),
        ("Contres+tir",      r_to["Counterattacks with shots"],r_ao["Counterattacks with shots"],"vs"),
        ("% contres tir",    r_to["% Counterattacks with shots"],r_ao["% Counterattacks with shots"],"pct"),
        ("Corners",          r_to["Corners"],r_ao["Corners"],"vs"),
        ("Corners+tir",      r_to["Corners with shots"],r_ao["Corners with shots"],"vs"),
        ("% corners tir",    r_to["% Corners with shots"],r_ao["% Corners with shots"],"pct"),
        ("Coups francs",     r_to["Free kicks"],r_ao["Free kicks"],"vs"),
        ("CF+tir",           r_to["Free kicks with shots"],r_ao["Free kicks with shots"],"vs"),
        ("% CF tir",         r_to["% Free kicks with shots"],r_ao["% Free kicks with shots"],"pct"),
        ("Centres",          r_to["Crosses"],r_ao["Crosses"],"vs"),
        ("Centres réussis",  r_to["Crosses accurate"],r_ao["Crosses accurate"],"vs"),
        ("% centres réuss.", r_to["% Crosses accurate"],r_ao["% Crosses accurate"],"pct"),
    ]
    st.markdown(make_mirror_section(off_data, "TL", adv_name[:20]), unsafe_allow_html=True)

    st.markdown("")
    section("Actions défensives")
    tl_rec  = max(r_tg["Recoveries Low"] + r_tg["Recoveries Medium"] + r_tg["Recoveries High"], 1)
    adv_rec = max(r_ag["Recoveries Low"] + r_ag["Recoveries Medium"] + r_ag["Recoveries High"], 1)
    def_data = [
        ("PPDA",              r_ti["PPDA"],r_ai["PPDA"],"vs"),
        ("Tacles réussis %",  r_td["% Sliding tackles successful"],r_ad["% Sliding tackles successful"],"pct"),
        ("Duels déf.gag.%",   r_td["% Defensive duels won"],r_ad["% Defensive duels won"],"pct"),
        ("Duels aér.gag.%",   r_td["% Aerial duels won"],r_ad["% Aerial duels won"],"pct"),
        ("Cartons jaunes",    float(r_td["Yellow cards"]),float(r_ad["Yellow cards"]),"vs"),
        ("Cartons rouges",    float(r_td["Red cards"]),float(r_ad["Red cards"]),"vs"),
        ("Récupérations",     r_tg["Recoveries"],r_ag["Recoveries"],"vs"),
        ("Récup.hautes %",    r_tg["Recoveries High"]/tl_rec*100,r_ag["Recoveries High"]/adv_rec*100,"pct"),
        ("Récup.méd.%",       r_tg["Recoveries Medium"]/tl_rec*100,r_ag["Recoveries Medium"]/adv_rec*100,"pct"),
        ("Récup.basses%",     r_tg["Recoveries Low"]/tl_rec*100,r_ag["Recoveries Low"]/adv_rec*100,"pct"),
        ("Duels",             r_tg["Duels"],r_ag["Duels"],"vs"),
        ("Duels gagnés",      r_tg["Duels won"],r_ag["Duels won"],"vs"),
        ("% Duels gagnés",    r_tg["% Duels won"],r_ag["% Duels won"],"pct"),
    ]
    st.markdown(make_mirror_section(def_data, "TL", adv_name[:20]), unsafe_allow_html=True)

    st.markdown("")
    section("Passing")
    ptl = float(r_tp["Passes"]) if float(r_tp["Passes"]) > 0 else 1
    pad = float(r_ap["Passes"]) if float(r_ap["Passes"]) > 0 else 1
    pass_data = [
        ("Tempo",            r_ti["Match tempo"],r_ai["Match tempo"],"vs"),
        ("% longues balles", r_ti["Long pass %"],r_ai["Long pass %"],"pct"),
        ("Long.moy.passe",   r_ti["Average pass length"],r_ai["Average pass length"],"vs"),
        ("Passes/possession",r_ti["Average passes per possession"],r_ai["Average passes per possession"],"vs"),
        ("Passes",           r_tp["Passes"],r_ap["Passes"],"vs"),
        ("Passes réussies",  r_tp["Passes accurate"],r_ap["Passes accurate"],"self",ptl,pad),
        ("% passes réuss.",  r_tp["% Passes accurate"],r_ap["% Passes accurate"],"pct"),
        ("Passes avant",     r_tp["Forward passes"],r_ap["Forward passes"],"vs"),
        ("% passes av.",     r_tp["% Forward passes accurate"],r_ap["% Forward passes accurate"],"pct"),
        ("Passes arrière",   r_tp["Back passes"],r_ap["Back passes"],"vs"),
        ("% passes ar.",     r_tp["% Back passes accurate"],r_ap["% Back passes accurate"],"pct"),
        ("Passes latérales", r_tp["Lateral passes"],r_ap["Lateral passes"],"vs"),
        ("% passes lat.",    r_tp["% Lateral passes accurate"],r_ap["% Lateral passes accurate"],"pct"),
        ("Passes longues",   r_tp["Long passes"],r_ap["Long passes"],"vs"),
        ("% passes long.",   r_tp["% Long passes accurate"],r_ap["% Long passes accurate"],"pct"),
        ("Passes tiers fin.",r_tp["Passes to final third"],r_ap["Passes to final third"],"vs"),
        ("% TF réussies",    r_tp["% Passes to final third accurate"],r_ap["% Passes to final third accurate"],"pct"),
        ("Passes prog.",     r_tp["Progressive passes"],r_ap["Progressive passes"],"vs"),
        ("% passes prog.",   r_tp["% Progressive passes accurate"],r_ap["% Progressive passes accurate"],"pct"),
        ("Smart passes",     r_tp["Smart passes"],r_ap["Smart passes"],"vs"),
        ("% smart passes",   r_tp["% Smart passes accurate"],r_ap["% Smart passes accurate"],"pct"),
    ]
    st.markdown(make_mirror_section(pass_data, "TL", adv_name[:20]), unsafe_allow_html=True)