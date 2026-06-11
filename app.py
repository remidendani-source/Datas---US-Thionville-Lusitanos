# ============================================================
# US THIONVILLE LUSITANOS — Dashboard Streamlit
# ============================================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import math as _math

st.set_page_config(page_title="US Thionville Lusitanos", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

FICHIER = "Team_Stats_Thionville_Lusitanos.xlsx"
TEAM    = "Thionville Lusitanos"
COMP_LABELS = {
    "France. National 2": "National 2 · 2025-26",
    "France. Ligue 3":    "Ligue 3 · 2026-27",
}
ALL_PLAYERS = [
    "Muamer Aljic","Samir Bouzar","Cachito Wanduka","Marly Rampont","David Luvualu",
    "Jérémy Lauratet","Samed Kilic","Jalil Moustaid","Clément Couturier",
    "Bryan Labissière","Alexis Gouletquer","Karim Bouhmidi","Chafik Gourichy"
]

@st.cache_data(ttl=300)
def load_data(path):
    def sheet(name):
        raw = pd.read_excel(path, sheet_name=name)
        df  = raw.iloc[2:].copy().reset_index(drop=True)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return sheet("Stats gen"),sheet("Stats off"),sheet("Stats def"),sheet("Stats pass"),sheet("Stats index")

@st.cache_data(ttl=300)
def load_players(path):
    p = {}
    for name in ALL_PLAYERS:
        df = pd.read_excel(path, sheet_name=name)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        p[name] = df
    return p

gen_all,off_all,defe_all,passe_all,idx_all = load_data(FICHIER)
players_all = load_players(FICHIER)

DARK="#000000";CARD="#111111";BORD="#2a2a2a";TEXT="#ffffff";MUTED="#8b949e"
GREY="#9e9e9e";RED="#ff2d55";GREEN="#00ff88";GOLD="#ffd60a";GOLD2="#C9A84C"

st.markdown(f"""<style>
  .stApp,.main,[data-testid="stAppViewContainer"],[data-testid="stHeader"],
  section[data-testid="stSidebar"],[data-testid="stSidebarContent"]
  {{background-color:{DARK} !important;}}
  .block-container {{padding-top:1rem;background-color:{DARK} !important;}}
  h1,h2,h3,p,label,span {{color:{TEXT} !important;}}
  .kpi {{background:{CARD};border:1px solid {BORD};border-radius:10px;padding:12px 10px;text-align:center;margin-bottom:6px;}}
  .kpi-label {{color:{MUTED};font-size:11px;margin-bottom:3px;}}
  .kpi-value {{color:{TEXT};font-size:22px;font-weight:700;}}
  .kpi-pos {{color:{GREEN};font-size:10px;margin-top:2px;}}
  .kpi-neg {{color:{RED};font-size:10px;margin-top:2px;}}
  .kpi-neu {{color:{MUTED};font-size:10px;margin-top:2px;}}
  .section {{color:{TEXT};font-size:15px;font-weight:600;margin:14px 0 6px 0;}}
  .sc {{background:#1E2733;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:14px;margin-bottom:10px;}}
  .sct {{font-size:11px;font-weight:600;color:#C9A84C;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;}}
  .bt {{height:3px;background:rgba(255,255,255,0.08);border-radius:2px;margin-top:3px;}}
  [data-testid="stDataFrame"] {{background:{CARD};}}
  [data-testid="collapsedControl"] {{display:none !important;}}
  /* Décale le contenu principal sous le header Streamlit */
  .block-container {{padding-top:3.5rem !important;}}
  /* NAV HORIZONTALE */
  .nav-bar {{display:flex;align-items:center;gap:6px;padding:10px 0 14px 0;flex-wrap:wrap;}}
  .nav-logo {{height:36px;width:auto;margin-right:10px;}}
  .nav-btn {{background:#111;border:1px solid #2a2a2a;border-radius:8px;padding:7px 14px;
             font-size:13px;font-weight:500;color:#9e9e9e;cursor:pointer;white-space:nowrap;
             transition:all 0.15s;}}
  .nav-btn:hover {{background:#1a1a1a;color:#fff;border-color:#444;}}
  .nav-btn.active {{background:#1a1a1a;color:#ffd60a;border-color:#ffd60a;}}
  .nav-divider {{width:1px;height:28px;background:#2a2a2a;margin:0 4px;}}
  div[data-testid="stHorizontalBlock"] > div {{padding:0 2px !important;}}
</style>""", unsafe_allow_html=True)

def lyt():
    return dict(paper_bgcolor=DARK,plot_bgcolor=DARK,font_color=TEXT,
        margin=dict(t=30,b=20,l=10,r=10),
        legend=dict(bgcolor=CARD,bordercolor=BORD,borderwidth=1,font=dict(color=TEXT)))

def kpi(col,label,value,delta=None,inverse=False,fmt=".2f",suffix=""):
    vs=f"{value:{fmt}}{suffix}"; dh=""
    if delta is not None:
        diff=value-delta
        if diff==0: cls,sign="kpi-neu","="
        elif (diff>0 and not inverse) or (diff<0 and inverse): cls,sign="kpi-pos","+"
        else: cls,sign="kpi-neg","+"
        dh=f'<div class="{cls}">{sign}{diff:{fmt}}{suffix} vs adv.</div>'
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{vs}</div>{dh}</div>',unsafe_allow_html=True)

def section(t): st.markdown(f'<div class="section">{t}</div>',unsafe_allow_html=True)

def pct_bar_overlay(fig,x,yt,yr,nt,nr,ct,cr):
    pct=(yr/yt.replace(0,float("nan"))*100).round(1)
    fig.add_trace(go.Bar(x=x,y=yt,name=nt,marker_color=ct))
    fig.add_trace(go.Bar(x=x,y=yr,name=nr,marker_color=cr,
        text=[f"{v}%" for v in pct],textposition="inside",insidetextanchor="middle",
        textfont=dict(color=DARK,size=11,family="Arial Black")))
    return fig

def mirror_row(label,tv,av,tm,am,pct=False):
    wt=round(tv/tm*100,1) if tm>0 else 0; wa=round(av/am*100,1) if am>0 else 0
    ts=f"{tv:.0f}%" if pct else str(round(tv,1)); as_=f"{av:.0f}%" if pct else str(round(av,1))
    r='<div style="display:grid;grid-template-columns:55px 1fr 160px 1fr 55px;align-items:center;gap:4px;padding:6px 0;border-bottom:0.5px solid #2a2a2a;">'
    r+=f'<div style="text-align:right;font-size:13px;color:#fff;">{ts}</div>'
    r+=f'<div style="background:#2a2a2a;border-radius:3px;height:16px;overflow:hidden;"><div style="width:{wt}%;height:100%;background:#9e9e9e;margin-left:auto;border-radius:3px;"></div></div>'
    r+=f'<div style="text-align:center;font-size:12px;color:#8b949e;padding:0 4px;">{label}</div>'
    r+=f'<div style="background:#2a2a2a;border-radius:3px;height:16px;overflow:hidden;"><div style="width:{wa}%;height:100%;background:#ff2d55;border-radius:3px;"></div></div>'
    r+=f'<div style="text-align:left;font-size:13px;color:#fff;">{as_}</div></div>'
    return r

def build_mirror(rows,tl,adv):
    h=f'<div style="display:grid;grid-template-columns:55px 1fr 160px 1fr 55px;gap:4px;padding-bottom:8px;border-bottom:1px solid #2a2a2a;margin-bottom:4px;">'
    h+=f'<div style="text-align:right;font-size:12px;color:#9e9e9e;font-weight:700;">{tl}</div><div></div><div></div><div></div>'
    h+=f'<div style="text-align:left;font-size:12px;color:#ff2d55;font-weight:700;">{adv}</div></div>'
    return '<div style="background:#111111;border:1px solid #2a2a2a;border-radius:10px;padding:14px;">'+h+rows+'</div>'

def make_mirror_section(data,tl,adv):
    rows=""
    for item in data:
        lb,tv,av,mode=item[0],item[1],item[2],item[3]
        if mode=="pct": rows+=mirror_row(lb,tv,av,100,100,pct=True)
        elif mode=="vs":
            tot=tv+av if (tv+av)>0 else 1; rows+=mirror_row(lb,tv,av,tot,tot)
        elif mode=="self":
            tr,ar=item[4],item[5]; rows+=mirror_row(lb,tv,av,tr if tr>0 else 1,ar if ar>0 else 1)
    return build_mirror(rows,tl,adv)

def get_player_cols(df):
    cols=list(df.columns)
    def nc(c):
        if c not in cols: return None
        return cols[cols.index(c)+1]
    def safe_nc(c, fallback=None):
        result = nc(c)
        return result if result is not None else fallback
    yc = "Yellow cards" if "Yellow cards" in cols else "Yellow card"
    rc = "Red cards"    if "Red cards"    in cols else "Red card"
    def_acc = nc("Defensive duels / won") if "Defensive duels / won" in cols else nc("Duels / won")
    slides_acc = nc("Sliding tackles / successful") if "Sliding tackles / successful" in cols else None
    return {
        "ta_acc":      nc("Total actions / successful"),
        "pass_acc":    nc("Passes / accurate"),
        "long_acc":    nc("Long passes / accurate"),
        "aer_acc":     nc("Aerial duels / won"),
        "def_acc":     def_acc,
        "loss_acc":    nc("Losses / own half"),
        "rec_acc":     nc("Recoveries / opp. half"),
        "through_acc": nc("Through passes / accurate"),
        "ptf_acc":     nc("Passes to final third / accurate"),
        "ppa_acc":     nc("Passes to penalty area / accurate"),
        "fp_acc":      nc("Forward passes / accurate"),
        "bp_acc":      nc("Back passes / accurate"),
        "slides_acc":  slides_acc,
        "crosses_acc": nc("Crosses / accurate"),
        "shots_acc":   nc("Shots / on target"),
        "off_acc":     nc("Offensive duels / won"),
        "drib_acc":    nc("Dribbles / successful"),
        "yc": yc, "rc": rc,
    }

def make_pitch_svg(ph,pm,pl,color,journee="",adversaire="",width=190,height=300):
    def op(p): return round(0.10+(p/100)*0.65,2)
    H,W=height,width; zh=H//3
    gw=int(W*0.62);gh=int(H*0.15);gx=(W-gw)//2
    sw=int(W*0.37);sh=int(H*0.06);sx=(W-sw)//2
    bw=int(W*0.19);bh=int(H*0.025);bx=(W-bw)//2
    cx=W//2;cy=H//2;cr=int(min(W,H)*0.14);pp=int(gh*0.55)
    s=f'<svg width="{W+30}" height="{H+50}" viewBox="0 0 {W+30} {H+50}" xmlns="http://www.w3.org/2000/svg">'
    s+=f'<rect x="0" y="25" width="{W}" height="{H}" fill="#6a9e4a"/>'
    for i in range(5):
        if i%2==0: s+=f'<rect x="0" y="{25+i*H//5}" width="{W}" height="{H//5}" fill="#5e8f40"/>'
    s+=f'<rect x="0" y="25" width="{W}" height="{zh}" fill="{color}" opacity="{op(ph)}"/>'
    s+=f'<rect x="0" y="{25+zh}" width="{W}" height="{zh}" fill="{color}" opacity="{op(pm)}"/>'
    s+=f'<rect x="0" y="{25+2*zh}" width="{W}" height="{zh}" fill="{color}" opacity="{op(pl)}"/>'
    s+=f'<line x1="0" y1="{25+zh}" x2="{W}" y2="{25+zh}" stroke="white" stroke-width="1" stroke-dasharray="5,4" opacity="0.7"/>'
    s+=f'<line x1="0" y1="{25+2*zh}" x2="{W}" y2="{25+2*zh}" stroke="white" stroke-width="1" stroke-dasharray="5,4" opacity="0.7"/>'
    s+=f'<rect x="0" y="25" width="{W}" height="{H}" fill="none" stroke="white" stroke-width="2"/>'
    s+=f'<line x1="0" y1="{25+cy}" x2="{W}" y2="{25+cy}" stroke="white" stroke-width="1.5"/>'
    s+=f'<circle cx="{cx}" cy="{25+cy}" r="{cr}" fill="none" stroke="white" stroke-width="1.5"/>'
    s+=f'<circle cx="{cx}" cy="{25+cy}" r="2" fill="white"/>'
    s+=f'<rect x="{gx}" y="25" width="{gw}" height="{gh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s+=f'<rect x="{sx}" y="25" width="{sw}" height="{sh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s+=f'<rect x="{bx}" y="{25-bh}" width="{bw}" height="{bh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s+=f'<circle cx="{cx}" cy="{25+pp}" r="2" fill="white"/>'
    s+=f'<rect x="{gx}" y="{25+H-gh}" width="{gw}" height="{gh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s+=f'<rect x="{sx}" y="{25+H-sh}" width="{sw}" height="{sh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s+=f'<rect x="{bx}" y="{25+H}" width="{bw}" height="{bh}" fill="none" stroke="white" stroke-width="1.5"/>'
    s+=f'<circle cx="{cx}" cy="{25+H-pp}" r="2" fill="white"/>'
    for i,p in enumerate([ph,pm,pl]):
        yb=25+i*zh+zh//2-11
        s+=f'<rect x="3" y="{yb}" width="42" height="21" fill="rgba(0,0,0,0.65)" rx="3"/>'
        s+=f'<text x="24" y="{yb+15}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="white">{p:.0f}%</text>'
    ax=W+4
    s+=f'<line x1="{ax}" y1="{25+H-10}" x2="{ax}" y2="35" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>'
    s+=f'<polygon points="{ax},35 {ax-4},45 {ax+4},45" fill="rgba(255,255,255,0.5)"/>'
    if journee: s+=f'<text x="{cx}" y="16" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="white">{journee}</text>'
    if adversaire: s+=f'<text x="{cx}" y="{25+H+bh+14}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" fill="rgba(255,255,255,0.7)">{adversaire[:16]}</text>'
    s+='</svg>'
    return s

def make_pass_svg(fp_r,bp_r,long_r,tp_r,ptf_r,ppa_r,total_w,width=320,height=430,poste="DC"):
    import math
    W,H=width,height
    cx=W//2; cy=H//2
    gw=int(W*0.55); gh=int(H*0.14); gx=(W-gw)//2
    sw=int(W*0.34); sh=int(H*0.055); sx=(W-sw)//2
    bw=int(W*0.18); bh=int(H*0.022); bx=(W-bw)//2
    cr=int(min(W,H)*0.11)
    tiers_h=int(H*0.32)
    poste_y={"DC":0.68,"DL":0.64,"DR":0.64,"MC":0.50,"MDF":0.50,"MO":0.44,"ATT":0.33,"GK":0.82}
    px=cx; py=int(10+H*poste_y.get(poste,0.68))
    L_short=int(H*0.22); L_long=int(H*0.30)
    svg=[]
    svg.append(f'<svg width="{W}" height="{H+20}" viewBox="0 0 {W} {H+20}" xmlns="http://www.w3.org/2000/svg">')
    svg.append(f'<rect x="0" y="10" width="{W}" height="{H}" fill="#1e4d14"/>')
    for i in range(9):
        if i%2==0: svg.append(f'<rect x="0" y="{10+i*H//9}" width="{W}" height="{H//9}" fill="#1a4511"/>')
    svg.append(f'<rect x="0" y="10" width="{W}" height="{tiers_h}" fill="rgba(40,90,200,0.18)"/>')
    svg.append(f'<rect x="{gx}" y="10" width="{gw}" height="{gh}" fill="rgba(140,30,200,0.25)"/>')
    svg.append(f'<rect x="0" y="10" width="{W}" height="{H}" fill="none" stroke="white" stroke-width="2" stroke-opacity="0.5"/>')
    svg.append(f'<line x1="0" y1="{10+cy}" x2="{W}" y2="{10+cy}" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{10+cy}" r="{cr}" fill="none" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{10+cy}" r="2.5" fill="white" opacity="0.4"/>')
    svg.append(f'<rect x="{gx}" y="10" width="{gw}" height="{gh}" fill="none" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<rect x="{sx}" y="10" width="{sw}" height="{sh}" fill="none" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<rect x="{bx}" y="{10-bh}" width="{bw}" height="{bh}" fill="none" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{10+int(gh*0.55)}" r="2" fill="white" opacity="0.4"/>')
    svg.append(f'<rect x="{gx}" y="{10+H-gh}" width="{gw}" height="{gh}" fill="none" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<rect x="{sx}" y="{10+H-sh}" width="{sw}" height="{sh}" fill="none" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<rect x="{bx}" y="{10+H}" width="{bw}" height="{bh}" fill="none" stroke="white" stroke-width="1.5" stroke-opacity="0.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{10+int(H-gh*0.55)}" r="2" fill="white" opacity="0.4"/>')
    def arrow(x1,y1,x2,y2,color,dash=False,width=2.5,label="",label_x=None,label_y=None):
        dx=x2-x1; dy=y2-y1; length=math.sqrt(dx*dx+dy*dy)
        if length==0: return ""
        ux=dx/length; uy=dy/length
        ax=x2-ux*10; ay=y2-uy*10
        px2=-uy*5; py2=ux*5
        d=f"M {x1} {y1} L {x2} {y2}"
        da='stroke-dasharray="8,4"' if dash else ""
        s=f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" {da} stroke-opacity="0.85"/>'
        s+=f'<polygon points="{x2},{y2} {ax+px2},{ay+py2} {ax-px2},{ay-py2}" fill="{color}" opacity="0.85"/>'
        if label:
            lx=label_x if label_x else (x1+x2)//2+8
            ly=label_y if label_y else (y1+y2)//2
            s+=f'<rect x="{lx-14}" y="{ly-9}" width="28" height="14" rx="3" fill="rgba(0,0,0,0.7)"/>'
            s+=f'<text x="{lx}" y="{ly+1}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" font-weight="700" fill="{color}">{label}%</text>'
        return s
    fwd_x=px-30; bwd_x=px+30
    # Long: décalé à gauche du centre (px-12)
    # Surface (ppa): décalé à droite (px+18) pour ne pas chevaucher Long
    long_x = px - 12
    ppa_x  = px + 18
    svg.append(arrow(fwd_x,py,fwd_x,py-L_short,"#4488ff",label=f"{fp_r:.0f}",label_x=fwd_x-22,label_y=py-L_short//2))
    svg.append(arrow(bwd_x,py,bwd_x,py+int(L_short*0.7),"#ff3355",label=f"{bp_r:.0f}",label_x=bwd_x+22,label_y=py+int(L_short*0.4)))
    svg.append(arrow(long_x,py,long_x,py-L_long,"#ff8800",dash=True,label=f"{long_r:.0f}",label_x=long_x-22,label_y=py-L_long//2))
    svg.append(arrow(px-10,py-10,px-10,py-int(L_long*1.1),"#ffdd00",dash=True,label=f"{tp_r:.0f}",label_x=px-32,label_y=py-int(L_long*0.55)))
    if ptf_r>0:
        # Pour DC/DL/DR: la flèche va jusqu'au bord de la zone tiers final (10+tiers_h)
        if poste in ("DC","DL","DR","GK"):
            ty = 10 + tiers_h
        else:
            ty = max(10+tiers_h-10, py-int(L_short*1.2))
        svg.append(arrow(px+15,py,px+15,ty,"#22ddaa",label=f"{ptf_r:.0f}",label_x=px+37,label_y=(py+ty)//2))
    if ppa_r>0:
        gy=10+gh+5
        svg.append(arrow(ppa_x,py,ppa_x,gy,"#cc44ff",label=f"{ppa_r:.0f}",label_x=ppa_x+22,label_y=py-int((py-gy)*0.5)))
    svg.append(f'<circle cx="{px}" cy="{py}" r="7" fill="#ffffff" stroke="#000" stroke-width="1.5"/>')
    svg.append(f'<text x="{px}" y="{py+4}" text-anchor="middle" font-family="Arial,sans-serif" font-size="8" font-weight="700" fill="#000">{poste}</text>')
    legend_y=H+20-6
    items=[("#4488ff","→ Avant"),("#ff3355","← Arrière"),("#ff8800","Long"),("#ffdd00","Profond"),("#22ddaa","T.Final"),("#cc44ff","Surface")]
    lx=4
    for color,lbl in items:
        svg.append(f'<circle cx="{lx+5}" cy="{legend_y}" r="4" fill="{color}"/>')
        svg.append(f'<text x="{lx+12}" y="{legend_y+4}" font-family="Arial,sans-serif" font-size="8" fill="#ccc">{lbl}</text>')
        lx+=W//6
    svg.append('</svg>')
    return "".join(svg)

def get_pitch_data(df_gen,adv_names_list,journees_list,col_low,col_med,col_high,col_total):
    rows=[]
    for i,row in df_gen.iterrows():
        total=row[col_total] if row[col_total]>0 else 1
        rows.append({"journee":journees_list[i],"adversaire":adv_names_list[i],
            "high":row[col_high]/total*100,"med":row[col_med]/total*100,"low":row[col_low]/total*100})
    return rows

def render_pitches(rows,color,per_row=4):
    for i in range(0,len(rows),per_row):
        chunk=rows[i:i+per_row]
        cols=st.columns(len(chunk))
        for j,r in enumerate(chunk):
            cols[j].markdown(make_pitch_svg(r["high"],r["med"],r["low"],color,r["journee"],r["adversaire"]),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
logo_path = Path(__file__).parent / "logo.png"

NAV_COLLECTIF = ["🏠 Vue d'ensemble","🎯 Finition","🛡️ Pressing","🔁 En possession","📅 Analyse par match"]

if "nav_mode" not in st.session_state:
    st.session_state.nav_mode = "⚽ Collectif"
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Vue d'ensemble"
if "nav_joueur" not in st.session_state:
    st.session_state.nav_joueur = ALL_PLAYERS[0]
if "nav_saison" not in st.session_state:
    comps_init = sorted(gen_all["Competition"].dropna().unique().tolist())
    comp_opts_init = {COMP_LABELS.get(c,c):c for c in comps_init}
    st.session_state.nav_saison = list(comp_opts_init.keys())[0]

# ── SIDEBAR ──
with st.sidebar:
    logo_path_sb = Path(__file__).parent / "logo.png"
    if logo_path_sb.exists():
        col_l,col_c,col_r=st.columns([1,2,1])
        col_c.image(str(logo_path_sb),width=120)
    st.markdown("<div style='font-size:19px;font-weight:800;color:#ffffff;margin:4px 0 6px 0;text-align:center;'>US Thionville Lusitanos</div>", unsafe_allow_html=True)
    st.divider()
    # Switcher mode dans la sidebar
    mode_sb = st.radio("", ["⚽ Collectif", "👤 Joueur", "📊 KPI'S LIGUE 3"], index=["⚽ Collectif","👤 Joueur","📊 KPI'S LIGUE 3"].index(st.session_state.nav_mode), horizontal=False, label_visibility="collapsed")
    if mode_sb != st.session_state.nav_mode:
        st.session_state.nav_mode = mode_sb
        st.rerun()
    mode = st.session_state.nav_mode
    st.divider()

if mode in ("⚽ Collectif", "👤 Joueur"):
    with st.sidebar:

        comps = sorted(gen_all["Competition"].dropna().unique().tolist())
        comp_opts = {COMP_LABELS.get(c,c):c for c in comps}

        if mode == "⚽ Collectif":
            saison_label = st.selectbox("🏆 Saison", list(comp_opts.keys()))
            saison_comp  = comp_opts[saison_label]
            n_m = len(gen_all[(gen_all["Competition"]==saison_comp)&(gen_all["Team"]==TEAM)])
            st.markdown(f"<span style='color:{MUTED};font-size:12px;'>📊 {n_m} matchs analysés</span>", unsafe_allow_html=True)
            st.divider()
            page = st.radio("Menu", NAV_COLLECTIF)

        elif mode == "👤 Joueur":
            saison_label_j = st.selectbox("🏆 Saison", list(comp_opts.keys()))
            st.divider()
            st.markdown(f"<div style='font-size:11px;color:{MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Joueur</div>", unsafe_allow_html=True)
            joueur_sel = st.radio("", ALL_PLAYERS, label_visibility="collapsed")
            st.divider()
            df_j = players_all[joueur_sel].copy()
            df_played_all = df_j[df_j["Minutes played"]>20].sort_values("Journée").reset_index(drop=True)
            match_labels_j = [str(r["Journée"]) for _,r in df_played_all.iterrows()]
            selected_j = st.multiselect("Filtrer les matchs", match_labels_j, default=[])
            if selected_j:
                df_joueur = df_played_all[df_played_all["Journée"].isin(selected_j)].reset_index(drop=True)
            else:
                df_joueur = df_played_all.copy()

# ── Filtrage collectif ──
if mode == "⚽ Collectif":
    def fc(df): return df[df["Competition"]==saison_comp].copy()
    gen=fc(gen_all);off=fc(off_all);defe=fc(defe_all);passe=fc(passe_all);idx=fc(idx_all)
    thi_gen=gen[gen["Team"]==TEAM].sort_values("Journée").reset_index(drop=True)
    adv_gen=gen[gen["Team"]!=TEAM].sort_values("Journée").reset_index(drop=True)
    thi_off=off[off["Team"]==TEAM].sort_values("Journée").reset_index(drop=True)
    adv_off=off[off["Team"]!=TEAM].sort_values("Journée").reset_index(drop=True)
    thi_def=defe[defe["Team"]==TEAM].sort_values("Journée").reset_index(drop=True)
    adv_def=defe[defe["Team"]!=TEAM].sort_values("Journée").reset_index(drop=True)
    thi_pass=passe[passe["Team"]==TEAM].sort_values("Journée").reset_index(drop=True)
    adv_pass=passe[passe["Team"]!=TEAM].sort_values("Journée").reset_index(drop=True)
    thi_idx=idx[idx["Team"]==TEAM].sort_values("Journée").reset_index(drop=True)
    adv_idx=idx[idx["Team"]!=TEAM].sort_values("Journée").reset_index(drop=True)
    if len(thi_gen)==0: st.warning("Aucune donnée."); st.stop()
    adv_names=[gen[gen["Match"]==thi_gen.iloc[i]["Match"]][gen["Team"]!=TEAM]["Team"].values[0] for i in range(len(thi_gen))]
    journees=[str(j) for j in thi_gen["Journée"]]
    journees_adv=[f"{journees[i]}\n{adv_names[i]}" for i in range(len(thi_gen))]
    adv_gen  = pd.concat([gen[(gen["Match"]==thi_gen.iloc[i]["Match"])&(gen["Team"]!=TEAM)] for i in range(len(thi_gen))]).reset_index(drop=True)
    adv_off  = pd.concat([off[(off["Match"]==thi_gen.iloc[i]["Match"])&(off["Team"]!=TEAM)] for i in range(len(thi_gen))]).reset_index(drop=True)
    adv_def  = pd.concat([defe[(defe["Match"]==thi_gen.iloc[i]["Match"])&(defe["Team"]!=TEAM)] for i in range(len(thi_gen))]).reset_index(drop=True)
    adv_pass = pd.concat([passe[(passe["Match"]==thi_gen.iloc[i]["Match"])&(passe["Team"]!=TEAM)] for i in range(len(thi_gen))]).reset_index(drop=True)
    adv_idx  = pd.concat([idx[(idx["Match"]==thi_gen.iloc[i]["Match"])&(idx["Team"]!=TEAM)] for i in range(len(thi_gen))]).reset_index(drop=True)
    def get_result(rt,ra):
        if rt["Goals"]>ra["Goals"]: return "V"
        if rt["Goals"]==ra["Goals"]: return "N"
        return "D"
    resultats=[get_result(thi_gen.iloc[i],adv_gen[adv_gen["Match"]==thi_gen.iloc[i]["Match"]].iloc[0]) for i in range(len(thi_gen))]
    bar_colors=[{"V":GREEN,"N":GOLD,"D":RED}[r] for r in resultats]
    buts_adv_list=[adv_gen[adv_gen["Match"]==row["Match"]]["Goals"].values[0] for _,row in thi_gen.iterrows()]
    thi_gen["pct_recup_high"]=thi_gen["Recoveries High"]/thi_gen["Recoveries"].replace(0,float("nan"))*100
    thi_gen["pct_losses_low"]=thi_gen["Losses Low "]/thi_gen["Losses"].replace(0,float("nan"))*100
    thi_gen["ratio_pression"]=(thi_gen["pct_recup_high"]/thi_gen["pct_losses_low"].replace(0,float("nan"))).round(2)
    thi_off["CPA_with_shots"]=thi_off["Corners with shots"]+thi_off["Free kicks with shots"]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE KPI'S LIGUE 3
# ══════════════════════════════════════════════════════════════════════════════
if mode == "📊 KPI'S LIGUE 3":
    st.markdown("""
    <div style="margin-bottom:20px;">
      <div style="font-size:11px;font-weight:600;color:#C9A84C;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Référentiel</div>
      <div style="font-size:26px;font-weight:900;color:#fff;letter-spacing:1px;">KPI'S LIGUE 3</div>
      <div style="font-size:13px;color:#8b949e;margin-top:2px;">7 indicateurs différenciants — Championnat National 1 · Saison 2025-26</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Cartes KPI seuils ──
    kpi_defs = [
        ("K1","PPDA","≤ 10.5","#4A90D9"),
        ("K2","Récup. off./90","≥ 9.0","#4A90D9"),
        ("K3","Deep comp./90","≥ 5.0","#4A90D9"),
        ("K4","Pass. prog/90","≥ 65","#4A90D9"),
        ("K5","% pertes déf.","≤ 16%","#4A90D9"),
        ("K6","Tirs subis/90","≤ 10.0","#4A90D9"),
        ("K7","Ratio %R/%P","≥ 0.80","#4A90D9"),
    ]
    kcols = st.columns(7)
    for i,(num,name,seuil,_) in enumerate(kpi_defs):
        kcols[i].markdown(f"""
        <div style="background:#0d1117;border:1px solid #2a3a4a;border-radius:10px;padding:12px 8px;text-align:center;">
          <div style="font-size:13px;font-weight:700;color:#4A90D9;margin-bottom:4px;">{num}</div>
          <div style="font-size:11px;color:#ccc;margin-bottom:6px;">{name}</div>
          <div style="font-size:16px;font-weight:800;color:#4A90D9;">{seuil}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Données ──
    teams = [
        (1,  "Dijon",            8.23, 11.60, 6.06, 74.6, 13, 7.27, 1.15, 7, "top"),
        (2,  "Sochaux",          8.95, 10.27, 5.52, 61.9, 15, 8.37, 0.93, 6, "top"),
        (3,  "Rouen",            9.09, 11.04, 5.66, 69.7, 13, 8.77, 1.08, 7, "top"),
        (4,  "Fleury 91 FC",     9.42,  9.73, 6.66, 71.4, 16, 9.90, 0.81, 6, "top"),
        (5,  "Versailles",       8.80,  9.47, 6.02, 65.8, 15, 9.67, 0.80, 7, "top"),
        (6,  "Orléans",         10.34, 10.95, 7.25, 69.5, 15, 9.45, 0.93, 7, "top"),
        (7,  "Le Puy F.43",     11.38,  8.20, 6.21, 72.6, 17,10.05, 0.65, 3, "mid"),
        (8,  "Caen",             8.91,  9.46, 5.68, 68.7, 13, 8.92, 1.00, 7, "top"),
        (9,  "Concarneau",      12.38,  7.99, 4.20, 65.9, 15, 8.13, 0.73, 3, "mid"),
        (10, "Valenciennes",    10.45, 11.61, 4.99, 69.7, 13, 9.68, 1.15, 6, "top"),
        (11, "Aubagne",         10.34,  8.42, 4.25, 62.5, 19,10.74, 0.58, 2, "bot"),
        (12, "Villefranche",     9.86,  7.91, 3.57, 57.3, 19,12.05, 0.58, 1, "bot"),
        (13, "Quevilly Rouen",  13.31,  7.44, 3.29, 64.2, 17, 9.90, 0.59, 2, "bot"),
        (14, "Paris 13 Atl.",   12.17,  8.96, 4.21, 62.4, 19,11.51, 0.63, 1, "bot"),
        (15, "Bourg-en-Bresse", 12.59,  9.14, 3.33, 64.0, 18, 8.97, 0.72, 3, "mid"),
        (16, "Châteauroux",      9.42,  8.47, 4.28, 67.5, 16,10.80, 0.75, 3, "mid"),
        (17, "Stade Briochin",  13.14,  8.86, 3.73, 67.2, 17,12.10, 0.71, 2, "bot"),
    ]
    avg = (0, "Moy. ligue", 10.52, 9.38, 5.00, 66.8, 16, 9.78, 0.76, None, "avg")

    # Seuils: (min_ok, max_ok) — None = pas de borne de ce côté
    thresholds = {
        "k1": (None, 10.5),   # ≤ 10.5
        "k2": (9.0,  None),   # ≥ 9.0
        "k3": (5.0,  None),   # ≥ 5.0
        "k4": (65.0, None),   # ≥ 65
        "k5": (None, 16.0),   # ≤ 16%
        "k6": (None, 10.0),   # ≤ 10.0
        "k7": (0.80, None),   # ≥ 0.80
    }

    def is_ok(val, key):
        lo, hi = thresholds[key]
        if hi is not None: return val <= hi
        return val >= lo

    def cell_color(val, key, is_avg=False):
        if is_avg: return "#1a1a1a"
        return "#0e2d1a" if is_ok(val, key) else "#2d0e0e"

    def text_color(val, key, is_avg=False):
        if is_avg: return "#9e9e9e"
        return "#00e676" if is_ok(val, key) else "#ff5252"

    # Score pill colors
    def score_style(score):
        if score is None: return "#1a1a1a","#9e9e9e"
        if score >= 6: return "#0d3b22","#00e676"
        if score >= 5: return "#1a2d0d","#76d600"
        if score >= 3: return "#2d2200","#ffd600"
        return "#2d0a0a","#ff5252"

    # Rank badge colors
    def rank_style(tier):
        if tier == "top": return "#0d3b22","#00e676"
        if tier == "mid": return "#2d2200","#ffd600"
        if tier == "bot": return "#2d0a0a","#ff5252"
        return "#1a1a1a","#9e9e9e"

    # Header
    th = """
    <style>
      .kpi-tbl { width:100%; border-collapse:separate; border-spacing:0 3px;
                 font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:13px; }
      .kpi-tbl th { background:#0d1117; color:#4A90D9; padding:10px 8px;
                    text-align:center; font-size:10px; font-weight:700;
                    text-transform:uppercase; letter-spacing:0.5px;
                    border-bottom:2px solid #4A90D9; white-space:nowrap; }
      .kpi-tbl th.left { text-align:left; padding-left:12px; }
      .kpi-tbl td { padding:7px 8px; vertical-align:middle; }
      .kpi-tbl tr { background:#0d0d0d; }
      .kpi-tbl tr:hover td { background:#111 !important; filter:brightness(1.1); }
      .rank-badge { display:inline-flex;align-items:center;justify-content:center;
                    width:24px;height:24px;border-radius:50%;font-size:11px;font-weight:700; }
      .val-chip { display:inline-block;padding:3px 10px;border-radius:6px;
                  font-size:13px;font-weight:600;min-width:52px;text-align:center; }
      .score-pill { display:inline-block;padding:4px 12px;border-radius:20px;
                    font-size:13px;font-weight:800;min-width:46px;text-align:center; }
      .avg-row td { border-top:1px solid #2a2a2a !important; }
    </style>
    <table class="kpi-tbl">
      <thead><tr>
        <th style="width:32px;">Cl.</th>
        <th class="left" style="min-width:120px;">Équipe</th>
        <th>K1<br>PPDA<br>≤10.5</th>
        <th>K2<br>Récup OFF<br>≥9.0/90</th>
        <th>K3<br>Deep Comp<br>≥5.0/90</th>
        <th>K4<br>Pass Prog<br>≥65/90</th>
        <th>K5<br>%Pertes Déf<br>≤16%</th>
        <th>K6<br>Tirs Subis<br>≤10.0/90</th>
        <th>K7<br>Ratio %R/%P<br>≥0.80</th>
        <th>Score /7</th>
      </tr></thead>
      <tbody>
    """

    def make_row(row, is_avg=False):
        cl, name, k1, k2, k3, k4, k5, k6, k7, score, tier = row

        if is_avg:
            rank_cell = '<td style="text-align:center;color:#9e9e9e;">—</td>'
            name_cell = f'<td style="padding-left:12px;font-style:italic;color:#9e9e9e;">{name}</td>'
            score_cell = '<td style="text-align:center;"><span style="color:#9e9e9e;">—</span></td>'
            row_class = ' class="avg-row"'
        else:
            rb_bg, rb_fg = rank_style(tier)
            rank_cell = f'<td style="text-align:center;"><span class="rank-badge" style="background:{rb_bg};color:{rb_fg};">{cl}</span></td>'
            name_cell = f'<td style="padding-left:12px;font-weight:600;color:#fff;">{name}</td>'
            sc_bg, sc_fg = score_style(score)
            score_cell = f'<td style="text-align:center;"><span class="score-pill" style="background:{sc_bg};color:{sc_fg};">{score}/7</span></td>'
            row_class = ""

        def td(val, key, pct=False):
            bg = cell_color(val, key, is_avg)
            fg = text_color(val, key, is_avg)
            display = f"{val}%" if pct else str(val)
            return f'<td style="text-align:center;"><span class="val-chip" style="background:{bg};color:{fg};">{display}</span></td>'

        return f'<tr{row_class}>{rank_cell}{name_cell}{td(k1,"k1")}{td(k2,"k2")}{td(k3,"k3")}{td(k4,"k4")}{td(k5,"k5",pct=True)}{td(k6,"k6")}{td(k7,"k7")}{score_cell}</tr>'

    body = ""
    for row in teams:
        body += make_row(row)
    body += make_row(avg, is_avg=True)

    st.markdown(th + body + "</tbody></table>", unsafe_allow_html=True)

    # ── Légende groupes ──
    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)

    def group_card(col, title, score_range, teams_list, bg, border, fg):
        col.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:10px;padding:14px 12px;text-align:center;">
          <div style="font-size:11px;font-weight:700;color:{fg};text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">{title}</div>
          <div style="font-size:24px;font-weight:900;color:{fg};">{score_range}</div>
          <div style="font-size:11px;color:#aaa;margin-top:6px;line-height:1.5;">{teams_list}</div>
        </div>""", unsafe_allow_html=True)

    _gc1,_gc2=st.columns(2)
    group_card(_gc1,"Top 6 Garanti","6–7 / 7","Dijon, Sochaux, Rouen, Fleury, Versailles, Orléans","#071a0e","#00e676","#00e676")
    group_card(_gc2,"Bas de Tableau","≤ 2 / 7","Aubagne, Quevilly, Paris 13, Villefranche, Briochin","#1a0707","#ff5252","#ff5252")

    # ── Comparaison Thionville N2 ──────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:14px;">
      <div style="font-size:11px;font-weight:600;color:#C9A84C;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Projection</div>
      <div style="font-size:20px;font-weight:800;color:#fff;">US Thionville Lusitanos — N2 25/26 vs référentiel N1 25/26</div>
    </div>
    """, unsafe_allow_html=True)

    # Données Thionville N2 extraites du rapport Wyscout National 2 Group B
    thl_n2 = {
        "K1": 9.82,   # PPDA (page défense)
        "K2": 9.95,   # Récupérations dernier tiers /90
        "K3": 4.97,   # Réalisations en profondeur /90 (proxy deep comp)
        "K4": 68.31,  # Passes progressives /90
        "K5": 14,     # % pertes zone défensive (16.98/121.70 = 14%)
        "K6": 10.28,  # Tirs subis /90 — source : rapport PDF N2 (15 matchs, hors matchs non représentatifs)
        "K7": 0.59,   # Ratio récup. off. / pertes déf. (9.95/16.98)
    }

    def delta_label(val, key):
        lo, hi = thresholds[key]
        if hi is not None:
            diff = hi - val
            ok = val <= hi
            sign = "↑" if ok else "↓"
            color = "#00e676" if ok else "#ff5252"
            return f'<span style="color:{color};font-size:11px;">{sign} {abs(diff):.2f} vs seuil N1</span>'
        else:
            diff = val - lo
            ok = val >= lo
            sign = "↑" if ok else "↓"
            color = "#00e676" if ok else "#ff5252"
            return f'<span style="color:{color};font-size:11px;">{sign} {abs(diff):.2f} vs seuil N1</span>'

    # Score N2
    n2_score = sum([
        thl_n2["K1"] <= 10.5,
        thl_n2["K2"] >= 9.0,
        thl_n2["K3"] >= 5.0,
        thl_n2["K4"] >= 65.0,
        thl_n2["K5"] <= 16,
        thl_n2["K6"] <= 10.0,
        thl_n2["K7"] >= 0.80,
    ])
    sc_bg_n2, sc_fg_n2 = score_style(n2_score)

    # Tableau de comparaison
    kpi_labels = [
        ("K1", "PPDA", "k1", False),
        ("K2", "Récup off /90", "k2", False),
        ("K3", "Deep comp /90", "k3", False),
        ("K4", "Pass prog /90", "k4", False),
        ("K5", "% Pertes déf", "k5", True),
        ("K6", "Tirs subis /90", "k6", False),
        ("K7", "Ratio %R/%P", "k7", False),
    ]

    # Ligne Thionville N2 dans le même style que le tableau N1
    def td_n2(val, key, pct=False):
        bg = cell_color(val, key)
        fg = text_color(val, key)
        display = f"{val}%" if pct else str(val)
        return f'<td style="text-align:center;"><span class="val-chip" style="background:{bg};color:{fg};">{display}</span></td>'

    thl_row_html = f"""
    <table class="kpi-tbl" style="margin-top:16px;">
      <thead><tr>
        <th style="width:32px;"></th>
        <th class="left" style="min-width:120px;"></th>
        <th>K1<br>PPDA<br>≤10.5</th>
        <th>K2<br>Récup OFF<br>≥9.0/90</th>
        <th>K3<br>Deep Comp<br>≥5.0/90</th>
        <th>K4<br>Pass Prog<br>≥65/90</th>
        <th>K5<br>%Pertes Déf<br>≤16%</th>
        <th>K6<br>Tirs Subis<br>≤10.0/90</th>
        <th>K7<br>Ratio %R/%P<br>≥0.80</th>
        <th>Score /7</th>
      </tr></thead>
      <tbody>
        <tr>
          <td style="text-align:center;">
            <span class="rank-badge" style="background:#0d1e3b;color:#4A90D9;">TL</span>
          </td>
          <td style="padding-left:12px;font-weight:700;color:#C9A84C;">
            US Thionville Lusitanos <span style="font-size:10px;color:#8b949e;font-weight:400;">N2 25/26</span>
          </td>
          {td_n2(thl_n2["K1"],"k1")}
          {td_n2(thl_n2["K2"],"k2")}
          {td_n2(thl_n2["K3"],"k3")}
          {td_n2(thl_n2["K4"],"k4")}
          {td_n2(thl_n2["K5"],"k5",pct=True)}
          {td_n2(thl_n2["K6"],"k6")}
          {td_n2(thl_n2["K7"],"k7")}
          <td style="text-align:center;">
            <span class="score-pill" style="background:{sc_bg_n2};color:{sc_fg_n2};">{n2_score}/7</span>
          </td>
        </tr>
      </tbody>
    </table>
    """
    st.markdown(thl_row_html, unsafe_allow_html=True)

    # Radar comparatif
    st.markdown("<br>", unsafe_allow_html=True)

    def norm_kpi(k1,k2,k3,k4,k5,k6,k7):
        v1 = max(0, min(10, (10.5 - k1) / (10.5 - 8.0) * 10))
        v2 = max(0, min(10, (k2 - 7.0) / (12.0 - 7.0) * 10))
        v3 = max(0, min(10, (k3 - 3.0) / (7.5 - 3.0) * 10))
        v4 = max(0, min(10, (k4 - 57.0) / (75.0 - 57.0) * 10))
        v5 = max(0, min(10, (16 - k5) / (16 - 13) * 10))
        v6 = max(0, min(10, (12.1 - k6) / (12.1 - 7.27) * 10))
        v7 = max(0, min(10, (k7 - 0.58) / (1.15 - 0.58) * 10))
        return [v1,v2,v3,v4,v5,v6,v7]

    # Moy. Top 6 N1 : Dijon, Sochaux, Rouen, Fleury, Versailles, Orléans
    top6 = [
        [8.23,11.60,6.06,74.6,13,7.27,1.15],
        [8.95,10.27,5.52,61.9,15,8.37,0.93],
        [9.09,11.04,5.66,69.7,13,8.77,1.08],
        [9.42, 9.73,6.66,71.4,16,9.90,0.81],
        [8.80, 9.47,6.02,65.8,15,9.67,0.80],
        [10.34,10.95,7.25,69.5,15,9.45,0.93],
    ]
    bot3 = [
        [9.86, 7.91,3.57,57.3,19,12.05,0.58],
        [12.17,8.96,4.21,62.4,19,11.51,0.63],
        [13.14,8.86,3.73,67.2,17,12.10,0.71],
    ]
    avg_top6 = [sum(x[i] for x in top6)/len(top6) for i in range(7)]
    avg_bot3 = [sum(x[i] for x in bot3)/len(bot3) for i in range(7)]

    v_thl  = norm_kpi(*[thl_n2[f"K{i+1}"] for i in range(7)])
    v_top6 = norm_kpi(*avg_top6)
    v_bot3 = norm_kpi(*avg_bot3)

    cats_r = ["PPDA (inv.)","Récup off","Deep comp","Pass prog","% Pertes (inv.)","Tirs subis (inv.)","Ratio %R/%P"]
    fig_r = go.Figure()
    for vals, name, color, fill_color, dash in [
        (v_top6, "Moy. Top 6 N1", "#00e676", "rgba(0,230,118,0.12)",  "solid"),
        (v_bot3, "Moy. Bas N1",   "#ff5252", "rgba(255,82,82,0.12)",   "dot"),
        (v_thl,  "Thionville N2", "#C9A84C", "rgba(201,168,76,0.18)",  "solid"),
    ]:
        fig_r.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=cats_r+[cats_r[0]],
            fill="toself", name=name,
            line=dict(color=color, width=2, dash=dash),
            fillcolor=fill_color, opacity=0.9
        ))
    fig_r.update_layout(
        polar=dict(
            bgcolor=CARD, radialaxis=dict(visible=True,range=[0,10],gridcolor="#333"),
            angularaxis=dict(gridcolor="#333",tickcolor="#f0f0f0"),
        ),
        paper_bgcolor=DARK, plot_bgcolor=DARK, font_color=TEXT,
        legend=dict(bgcolor=DARK), height=460,
        margin=dict(l=60,r=60,t=40,b=40),
    )
    st.plotly_chart(fig_r, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MODE JOUEUR
# ══════════════════════════════════════════════════════════════════════════════
elif mode=="👤 Joueur":
    df=df_joueur; C=get_player_cols(df)
    def sp(w,t): return round(w/t*100,1) if t>0 else 0
    def pc(pct):
        if pct>=60: return "#00ff88"
        elif pct>=30: return "#ff8800"
        return "#ff2d55"
    def pc_inv(pct):
        if pct>=60: return "#ff2d55"
        elif pct>=30: return "#ff8800"
        return "#00ff88"

    n_m_j=len(df); minutes_j=int(df["Minutes played"].sum())
    buts_j=int(df["Goals"].sum()); assists_j=int(df["Assists"].sum())
    yc_j=int(df[C["yc"]].sum()); rc_j=int(df[C["rc"]].sum())
    min_per_match=round(minutes_j/n_m_j,1) if n_m_j>0 else 0

    ta_t=df["Total actions / successful"].sum(); ta_w=df[C["ta_acc"]].sum(); ta_pct=sp(ta_w,ta_t)
    pass_t=df["Passes / accurate"].sum(); pass_w=df[C["pass_acc"]].sum(); pass_pct=sp(pass_w,pass_t)
    long_t=df["Long passes / accurate"].sum(); long_w=df[C["long_acc"]].sum(); long_pct=sp(long_w,long_t)
    fp_t=df["Forward passes / accurate"].sum(); fp_w=df[C["fp_acc"]].sum(); fp_pct=sp(fp_w,fp_t)
    bp_t=df["Back passes / accurate"].sum(); bp_w=df[C["bp_acc"]].sum(); bp_pct=sp(bp_w,bp_t)
    ptf_t=df["Passes to final third / accurate"].sum(); ptf_w=df[C["ptf_acc"]].sum(); ptf_pct=sp(ptf_w,ptf_t)
    ppa_t=df["Passes to penalty area / accurate"].sum(); ppa_w=df[C["ppa_acc"]].sum(); ppa_pct=sp(ppa_w,ppa_t)
    tp_t=df["Through passes / accurate"].sum(); tp_w=df[C["through_acc"]].sum(); tp_pct=sp(tp_w,tp_t)
    crosses_t=df["Crosses / accurate"].sum(); crosses_w=df[C["crosses_acc"]].sum(); crosses_pct=sp(crosses_w,crosses_t)
    rec_passes=int(df["Received passes"].sum())
    pass_pm=round(pass_t/n_m_j,1) if n_m_j>0 else 0
    _pw=max(int(pass_w),1)
    fp_r=round(fp_w/_pw*100,1); bp_r=round(bp_w/_pw*100,1)
    long_r=round(long_w/_pw*100,1); tp_r=round(tp_w/_pw*100,1)
    ptf_r=round(ptf_w/_pw*100,1); ppa_r=round(ppa_w/_pw*100,1)
    aer_t=df["Aerial duels / won"].sum(); aer_w=df[C["aer_acc"]].sum(); aer_pct=sp(aer_w,aer_t)
    def_col = "Defensive duels / won" if "Defensive duels / won" in df.columns else "Duels / won"
    def_t=df[def_col].sum(); def_w=df[C["def_acc"]].sum() if C["def_acc"] else 0; def_pct=sp(def_w,def_t)
    rec_j=int(df["Recoveries / opp. half"].sum()); rec_j_w=int(df[C["rec_acc"]].sum())
    loss_j=int(df["Losses / own half"].sum()); loss_j_w=int(df[C["loss_acc"]].sum())
    intercept_j=int(df["Interceptions"].sum())
    slides_t=int(df["Sliding tackles / successful"].sum()) if "Sliding tackles / successful" in df.columns else 0
    slides_w_n=int(df[C["slides_acc"]].sum()) if C["slides_acc"] else 0
    fouls_j=int(df["Fouls"].sum())
    rec_zone_pct=sp(rec_j_w,rec_j) if rec_j>0 else 0
    loss_zone_pct=sp(loss_j_w,loss_j) if loss_j>0 else 0
    off_t=df["Offensive duels / won"].sum(); off_w=df[C["off_acc"]].sum(); off_pct=sp(off_w,off_t)
    drib_t=df["Dribbles / successful"].sum(); drib_w=df[C["drib_acc"]].sum(); drib_pct=sp(drib_w,drib_t)
    prog_runs=int(df["Progressive runs"].sum())
    touches_pa=int(df["Touches in penalty area"].sum())
    fouls_suf=int(df["Fouls suffered"].sum())
    offsides=int(df["Offsides"].sum())
    xg_j=round(df["xG"].sum(),2)
    shots_t=df["Shots / on target"].sum(); shots_w=df[C["shots_acc"]].sum(); conv_pct=sp(buts_j,shots_t)
    xA_j=round(df["xA"].sum(),2)
    shot_assists_j=int(df["Shot assists"].sum())
    second_assists=int(df["Second assists"].sum())
    journees_j=[str(r["Journée"]) for _,r in df.iterrows()]
    aer_pm=[round(r[C["aer_acc"]]/r["Aerial duels / won"]*100,1) if r["Aerial duels / won"]>0 else 0 for _,r in df.iterrows()]
    _def_col = "Defensive duels / won" if "Defensive duels / won" in df.columns else "Duels / won"
    def_pm=[round(r[C["def_acc"]]/r[_def_col]*100,1) if C["def_acc"] and r[_def_col]>0 else 0 for _,r in df.iterrows()]

    note=f" — {n_m_j} matchs sélectionnés" if selected_j else f" — {n_m_j} matchs"
    import base64 as _b64, unicodedata
    photo_html = ""
    _base = Path(__file__).parent / "photos"
    _found = None
    _names = [joueur_sel, unicodedata.normalize("NFC", joueur_sel), unicodedata.normalize("NFD", joueur_sel)]
    for _name in _names:
        for _ext in ["png","jpg","jpeg","PNG","JPG"]:
            _p = _base / f"{_name}.{_ext}"
            if _p.exists(): _found = _p; break
        if _found: break
    if _found:
        with open(_found,"rb") as _f: _b = _b64.b64encode(_f.read()).decode()
        _mime = "image/jpeg" if str(_found).lower().endswith(("jpg","jpeg")) else "image/png"
        photo_html = f'<img src="data:{_mime};base64,{_b}" style="height:200px;width:auto;object-fit:contain;border-radius:12px;border:3px solid rgba(201,168,76,0.5);margin-right:28px;flex-shrink:0;box-shadow:0 4px 20px rgba(0,0,0,0.5);"/>'

    st.markdown(f"""
    <div style="margin-top:10px;background:linear-gradient(135deg,#161D27 0%,#0D1117 100%);border-radius:12px;padding:20px 24px;border:1px solid rgba(201,168,76,0.25);margin-bottom:10px;display:flex;align-items:center;min-height:120px;">
      {photo_html}
      <div>
        <div style="font-size:10px;font-weight:600;color:{GOLD2};letter-spacing:2px;text-transform:uppercase;">US Thionville Lusitanos</div>
        <div style="font-size:28px;font-weight:900;letter-spacing:2px;color:#F0EDE6;line-height:1.1;margin:3px 0;">{joueur_sel.upper()}</div>
        <div style="background:rgba(201,168,76,0.15);border:1px solid rgba(201,168,76,0.35);border-radius:6px;padding:2px 10px;font-size:10px;color:#C9A84C;display:inline-block;">{saison_label_j}{note}</div>
      </div>
    </div>""",unsafe_allow_html=True)

    st.markdown(f"""<div style="background:#1E2733;border:1px solid rgba(201,168,76,0.3);border-radius:10px;padding:10px 16px;margin-bottom:10px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
      <div style="text-align:center;"><div style="font-size:9px;color:{MUTED};text-transform:uppercase;">Total actions</div><div style="font-size:24px;font-weight:900;">{int(ta_t)}</div></div>
      <div style="width:1px;height:30px;background:{BORD};"></div>
      <div style="text-align:center;"><div style="font-size:9px;color:{MUTED};text-transform:uppercase;">Réussies</div><div style="font-size:24px;font-weight:900;color:{GREEN};">{int(ta_w)}</div></div>
      <div style="width:1px;height:30px;background:{BORD};"></div>
      <div style="text-align:center;"><div style="font-size:9px;color:{MUTED};text-transform:uppercase;">% Réussite</div><div style="font-size:24px;font-weight:900;color:{GOLD};">{ta_pct}%</div></div>
      <div style="flex:1;min-width:80px;"><div style="height:7px;background:{BORD};border-radius:4px;overflow:hidden;"><div style="width:{ta_pct}%;height:100%;background:linear-gradient(90deg,{GREEN},{GOLD});border-radius:4px;"></div></div></div>
    </div>""",unsafe_allow_html=True)

    c1,c2,c3,c4,c5,c6=st.columns(6)
    def pk(col,label,val,color=TEXT):
        col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value" style="color:{color};">{val}</div></div>',unsafe_allow_html=True)
    pk(c1,"Matchs",n_m_j); pk(c2,"Minutes",minutes_j); pk(c3,"Min / Match",min_per_match)
    pk(c4,"Buts",buts_j); pk(c5,"Passes déc.",assists_j); pk(c6,"🟨 Jaunes",yc_j,GOLD)
    st.markdown("")

    def qty_bar(label,val,max_val,color="#4499ff"):
        w=round(val/max_val*100,1) if max_val>0 else 0
        return f'<div style="margin-bottom:7px;"><div style="display:flex;justify-content:space-between;"><span style="font-size:11px;color:#8B99AC;">{label}</span><span style="font-size:12px;font-weight:600;color:{color};">{int(val)}</span></div><div class="bt"><div style="width:{w}%;height:100%;background:{color};border-radius:2px;"></div></div></div>'
    def pct_bar(label,pct):
        c="#00ff88" if pct>=70 else ("#E87B2A" if pct>=55 else "#E24B4A")
        return f'<div style="margin-bottom:7px;"><div style="display:flex;justify-content:space-between;"><span style="font-size:11px;color:#8B99AC;">{label}</span><span style="font-size:11px;color:{c};font-weight:600;">{pct}%</span></div><div class="bt"><div style="width:{min(pct,100)}%;height:100%;background:{c};border-radius:2px;"></div></div></div>'
    def zone_bar(label,pct,disp="",inverse=False):
        c=pc_inv(pct) if inverse else pc(pct); d=disp if disp else f"{pct}%"
        return f'<div style="margin-bottom:8px;"><div style="display:flex;justify-content:space-between;margin-bottom:2px;"><span style="font-size:11px;color:#8B99AC;">{label}</span><span style="font-size:11px;color:{c};font-weight:600;">{d}</span></div><div style="height:5px;background:#2a2a2a;border-radius:3px;overflow:hidden;"><div style="width:{min(pct,100)}%;height:100%;background:{c};border-radius:3px;"></div></div></div>'
    def sr(label,val,color=TEXT):
        return f'<div style="display:flex;justify-content:space-between;margin-bottom:7px;"><span style="font-size:11px;color:#8B99AC;">{label}</span><span style="font-size:12px;font-weight:600;color:{color};">{val}</span></div>'

    col1,col2,col3=st.columns(3)
    with col1:
        pw=max(int(pass_w),1)
        h='<div class="sc"><div class="sct">🏗️ Construction</div>'
        h+=sr("Passes / match",pass_pm)+sr("Passes reçues",rec_passes)+sr("Passes réussies",int(pass_w),GREEN)
        h+=qty_bar("Passes vers l'avant",fp_w,pw,"#4499ff")
        h+=qty_bar("Passes vers l'arrière",bp_w,pw,"#ff2d55")
        h+=qty_bar("Passes vers le dernier tiers",ptf_w,pw,"#4499ff")
        h+=qty_bar("Passes longues",long_w,pw,"#ff8800")
        h+='</div>'
        st.markdown(h,unsafe_allow_html=True)
    with col2:
        h='<div class="sc"><div class="sct">🎯 Précision</div>'
        h+=pct_bar("Précision des passes (%)",pass_pct)
        h+=pct_bar("Précision passes vers l'avant (%)",fp_pct)
        h+=pct_bar("Précision passes vers l'arrière (%)",bp_pct)
        h+=pct_bar("Précision passes vers le dernier tiers (%)",ptf_pct)
        h+=pct_bar("Précision passes vers la surface adverse (%)",ppa_pct)
        h+=pct_bar("Précision passes longues (%)",long_pct)
        h+=pct_bar("Précision passes en profondeur (%)",tp_pct)
        h+=pct_bar("Précision des centres (%)",crosses_pct)
        h+='</div>'
        st.markdown(h,unsafe_allow_html=True)
    with col3:
        h='<div class="sc"><div class="sct">🛡️ Défense</div>'
        h+=sr("Duels aériens disputés",int(aer_t))
        h+=sr("Duels aériens gagnés",int(aer_w))
        h+=zone_bar("Duels aériens gagnés (%)",aer_pct,f"{aer_pct}%")
        h+=sr("Duels défensifs disputés",int(def_t))
        h+=sr("Duels défensifs gagnés",int(def_w))
        h+=zone_bar("Duels défensifs gagnés (%)",def_pct,f"{def_pct}%")
        h+=zone_bar("Récup. zone offensive",rec_zone_pct,f"{rec_j_w} / {rec_j}")
        h+=zone_bar("Pertes zone défensive",loss_zone_pct,f"{loss_j_w} / {loss_j}",inverse=True)
        h+=sr("Interceptions",intercept_j)
        h+=sr("Tacles glissés réussis",f"{slides_w_n} / {slides_t}")
        h+=sr("Fautes commises",fouls_j)
        h+=sr("Cartons jaunes",yc_j,GOLD)
        h+=sr("Cartons rouges",rc_j,RED)
        h+='</div>'
        st.markdown(h,unsafe_allow_html=True)

    st.markdown("")
    col4,col5,col6=st.columns(3)
    with col4:
        h='<div class="sc"><div class="sct">⚽ Finition</div>'
        h+=sr("Buts",buts_j,GREEN)+sr("xG",xg_j)
        h+=sr("Tirs / cadrés",f"{int(shots_t)} / {int(shots_w)}")
        h+=zone_bar("Taux de conversion but/tir (%)",conv_pct,f"{conv_pct}%")
        h+='</div>'
        st.markdown(h,unsafe_allow_html=True)
    with col5:
        h='<div class="sc"><div class="sct">🎨 Création</div>'
        xA_per_rp = round(xA_j/rec_passes*100,2) if rec_passes>0 else 0
        h+=sr("Passes décisives",assists_j,GREEN)+sr("xA",xA_j)
        h+=sr("xA par 100 passes reçues",xA_per_rp)
        h+=sr("Passes clés",shot_assists_j)
        h+=sr("Avant-dernière passe",second_assists)
        h+=sr("Passes en profondeur réussies",int(tp_w))
        h+=sr("Passes vers la surface adverse réussies",int(ppa_w))
        h+=sr("Centres réussis",int(crosses_w))
        h+='</div>'
        st.markdown(h,unsafe_allow_html=True)
    with col6:
        h='<div class="sc"><div class="sct">🚀 Offensif</div>'
        h+=sr("Duels offensifs disputés",int(off_t))
        h+=sr("Duels offensifs gagnés",int(off_w))
        h+=zone_bar("Duels offensifs gagnés (%)",off_pct,f"{off_pct}%")
        h+=sr("Dribbles tentés",int(drib_t))+sr("Dribbles réussis",int(drib_w))
        h+=zone_bar("Dribbles réussis (%)",drib_pct,f"{drib_pct}%")
        h+=sr("Courses progressives",prog_runs)
        h+=sr("Touches surface adverse",touches_pa)
        h+=sr("Fautes subies",fouls_suf)+sr("Hors-jeu",offsides)
        h+='</div>'
        st.markdown(h,unsafe_allow_html=True)

    st.markdown("")
    col_p,col_s=st.columns([1,1])
    with col_p:
        section("Direction des passes")
        POSTE_MAP = {
            "Muamer Aljic":"DC","Samir Bouzar":"DC","Cachito Wanduka":"DC",
            "Marly Rampont":"DC","David Luvualu":"DC",
            "Jalil Moustaid":"MC","Clément Couturier":"MC","Samed Kilic":"MC","Jérémy Lauratet":"MC",
            "Bryan Labissière":"ATT","Karim Bouhmidi":"ATT","Chafik Gourichy":"ATT","Alexis Gouletquer":"ATT",
        }
        _poste = POSTE_MAP.get(joueur_sel, "DC")
        svg_p=make_pass_svg(fp_r,bp_r,long_r,tp_r,ptf_r,ppa_r,int(pass_w),width=320,height=430,poste=_poste)
        st.markdown(f'<div style="background:#1E2733;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:12px;display:flex;justify-content:center;">{svg_p}</div>',unsafe_allow_html=True)
    with col_s:
        section("Répartition des passes réussies")
        cats=["→ Avant","← Arrière","Longues","Profondeur","Tiers final","Surface"]
        vals=[fp_r,bp_r,long_r,tp_r,ptf_r,ppa_r]
        colors_p=["#4488ff","#ff3355","#ff8800","#ffdd00","#22ddaa","#cc44ff"]
        rh='<div class="sc"><div class="sct">% sur passes réussies</div>'
        for cat,val,col_c in zip(cats,vals,colors_p):
            w=min(val,100)
            rh+=f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="font-size:12px;color:#8B99AC;">{cat}</span><span style="font-size:13px;font-weight:700;color:{col_c};">{val}%</span></div><div style="height:6px;background:#2a2a2a;border-radius:3px;overflow:hidden;"><div style="width:{w}%;height:100%;background:{col_c};border-radius:3px;"></div></div></div>'
        rh+='</div>'
        st.markdown(f'<div style="margin-top:22px;">{rh}</div>',unsafe_allow_html=True)
        total_r=round(fp_r+bp_r+ptf_r+ppa_r+long_r+tp_r,1)
        if total_r < 100:
            st.caption(f"% calculés sur {int(pass_w)} passes réussies. Total = {total_r}% (< 100%) car certaines passes longues ou en profondeur sont aussi comptées dans d'autres catégories selon leur direction.")
        else:
            st.caption(f"% calculés sur {int(pass_w)} passes réussies. Total = {total_r}% (> 100%) car certaines passes appartiennent à plusieurs catégories.")

    st.markdown("")
    section("Duels aériens gagnés (%) par journée")
    fa=go.Figure()
    fa.add_trace(go.Scatter(x=journees_j,y=aer_pm,mode="lines+markers+text",
        line=dict(color=GREEN,width=2),
        marker=dict(size=10,color=[GREEN if v>=75 else GOLD if v>=55 else RED for v in aer_pm],line=dict(color=CARD,width=2)),
        text=[f"{v}%" for v in aer_pm],textposition="top center",textfont=dict(size=9,color=TEXT),
        fill="tozeroy",fillcolor="rgba(0,255,136,0.08)"))
    fa.add_hline(y=aer_pct,line_dash="dot",line_color=GREY,annotation_text=f"Moy. {aer_pct:.0f}%",annotation_font_color=TEXT)
    fa.update_layout(**lyt(),height=300); fa.update_yaxes(range=[0,115],gridcolor=BORD)
    st.plotly_chart(fa,use_container_width=True)

    section("Duels défensifs gagnés (%) par journée")
    fd=go.Figure()
    fd.add_trace(go.Scatter(x=journees_j,y=def_pm,mode="lines+markers+text",
        line=dict(color=GOLD,width=2),
        marker=dict(size=10,color=[GREEN if v>=65 else GOLD if v>=50 else RED for v in def_pm],line=dict(color=CARD,width=2)),
        text=[f"{v}%" for v in def_pm],textposition="top center",textfont=dict(size=9,color=TEXT),
        fill="tozeroy",fillcolor="rgba(255,208,10,0.08)"))
    fd.add_hline(y=def_pct,line_dash="dot",line_color=GREY,annotation_text=f"Moy. {def_pct:.0f}%",annotation_font_color=TEXT)
    fd.update_layout(**lyt(),height=280); fd.update_yaxes(range=[0,115],gridcolor=BORD)
    st.plotly_chart(fd,use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MODE COLLECTIF
# ══════════════════════════════════════════════════════════════════════════════
elif mode=="⚽ Collectif":

    if page=="🏠 Vue d'ensemble":
        st.markdown(f"# 🏠 Vue d'ensemble — {saison_label}")
        section("Résultats")
        cols_res=st.columns(len(thi_gen))
        for i,row in thi_gen.iterrows():
            ar=adv_gen[adv_gen["Match"]==row["Match"]].iloc[0]; res=resultats[i]
            cl={"V":GREEN,"N":GOLD,"D":RED}[res]; em={"V":"🟢","N":"🟠","D":"🔴"}[res]
            cols_res[i].markdown(f'<div style="background:{CARD};border:1px solid {cl};border-radius:10px;padding:10px 8px;text-align:center;"><div style="font-size:11px;color:{MUTED};">{journees[i]}</div><div style="font-size:11px;color:{TEXT};margin:2px 0;">{adv_names[i][:12]}</div><div style="font-size:20px;font-weight:700;color:{cl};">{int(row["Goals"])}–{int(ar["Goals"])}</div><div style="font-size:11px;">{em}</div></div>',unsafe_allow_html=True)
        st.markdown("")
        c1,c2,c3,c4,c5,c6=st.columns(6)
        kpi(c1,"⚽ Buts / m",thi_gen["Goals"].mean(),adv_gen["Goals"].mean(),fmt=".2f")
        kpi(c2,"🚫 Concédés / m",thi_def["Conceded goals"].mean(),None,fmt=".2f",inverse=True)
        kpi(c3,"🎯 xG / m",thi_gen["xG"].mean(),adv_gen["xG"].mean(),fmt=".2f")
        kpi(c4,"🔵 Possession",thi_gen["% Possession"].mean(),adv_gen["% Possession"].mean(),fmt=".1f",suffix="%")
        kpi(c5,"💨 Tirs / m",thi_gen["Shots"].mean(),adv_gen["Shots"].mean(),fmt=".1f")
        kpi(c6,"🤼 Duels gag. %",thi_gen["% Duels won"].mean(),adv_gen["% Duels won"].mean(),fmt=".1f",suffix="%")
        st.markdown("")
        section("Comparaison des moyennes")
        ov=[("Buts / match",thi_gen["Goals"].mean(),adv_gen["Goals"].mean(),"vs"),
            ("xG / match",thi_gen["xG"].mean(),adv_gen["xG"].mean(),"vs"),
            ("Tirs / match",thi_gen["Shots"].mean(),adv_gen["Shots"].mean(),"vs"),
            ("Tirs cadrés / m",thi_gen["Shots on target"].mean(),adv_gen["Shots on target"].mean(),"vs"),
            ("Possession %",thi_gen["% Possession"].mean(),adv_gen["% Possession"].mean(),"pct"),
            ("Passes / match",thi_gen["Passes"].mean(),adv_gen["Passes"].mean(),"vs"),
            ("Passes réuss. %",thi_gen["% Passes accurate"].mean(),adv_gen["% Passes accurate"].mean(),"pct"),
            ("Récupérations / m",thi_gen["Recoveries"].mean(),adv_gen["Recoveries"].mean(),"vs"),
            ("Pertes / match",thi_gen["Losses"].mean(),adv_gen["Losses"].mean(),"vs"),
            ("Duels gagnés %",thi_gen["% Duels won"].mean(),adv_gen["% Duels won"].mean(),"pct")]
        st.markdown(make_mirror_section(ov,"TL","Adversaires"),unsafe_allow_html=True)
        st.markdown("")
        section("Pertes & Récupérations par zone")
        mls=[f"{journees[i]} — {adv_names[i]}" for i in range(len(thi_gen))]
        sel=st.multiselect("Filtrer par match(s)",options=mls,default=[])
        if sel:
            si=[mls.index(s) for s in sel]; dfs=thi_gen.iloc[si].reset_index(drop=True)
            tl=dfs["Losses"].mean() or 1; tr=dfs["Recoveries"].mean() or 1
            lh=dfs["Losses High"].mean()/tl*100; lm=dfs["Losses Medium"].mean()/tl*100; ll=dfs["Losses Low "].mean()/tl*100
            rh=dfs["Recoveries High"].mean()/tr*100; rm=dfs["Recoveries Medium"].mean()/tr*100; rl=dfs["Recoveries Low"].mean()/tr*100
        else:
            tl=thi_gen["Losses"].mean() or 1; tr=thi_gen["Recoveries"].mean() or 1
            lh=thi_gen["Losses High"].mean()/tl*100; lm=thi_gen["Losses Medium"].mean()/tl*100; ll=thi_gen["Losses Low "].mean()/tl*100
            rh=thi_gen["Recoveries High"].mean()/tr*100; rm=thi_gen["Recoveries Medium"].mean()/tr*100; rl=thi_gen["Recoveries Low"].mean()/tr*100
        cl2,cr2=st.columns(2)
        with cl2:
            st.markdown("**Pertes**")
            st.markdown(f'<div style="display:flex;justify-content:center;">{make_pitch_svg(lh,lm,ll,"#ff5500",width=280,height=440)}</div>',unsafe_allow_html=True)
        with cr2:
            st.markdown("**Récupérations**")
            st.markdown(f'<div style="display:flex;justify-content:center;">{make_pitch_svg(rh,rm,rl,"#00dd55",width=280,height=440)}</div>',unsafe_allow_html=True)
        st.markdown("")
        section("xG par journée")
        f2=go.Figure()
        f2.add_trace(go.Bar(x=journees_adv,y=thi_gen["xG"],name="xG TL",marker_color=GREY,text=thi_gen["xG"].round(2),textposition="outside"))
        f2.add_trace(go.Bar(x=journees_adv,y=adv_gen["xG"],name="xG Adversaires",marker_color=RED,text=adv_gen["xG"].round(2),textposition="outside"))
        f2.update_layout(**lyt(),barmode="group",height=300); f2.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f2,use_container_width=True)

    elif page=="🎯 Finition":
        st.markdown(f"# 🎯 Finition — {saison_label}")
        c1,c2,c3,c4=st.columns(4)
        kpi(c1,"⚽ Buts / m",thi_gen["Goals"].mean(),adv_gen["Goals"].mean(),fmt=".2f")
        kpi(c2,"🎯 xG / m",thi_off["xG"].mean(),adv_off["xG"].mean(),fmt=".2f")
        kpi(c3,"💨 Tirs / m",thi_off["Shots"].mean(),adv_off["Shots"].mean(),fmt=".1f")
        kpi(c4,"🎯 Tirs cadrés %",thi_off["% Shots on target"].mean(),adv_off["% Shots on target"].mean(),fmt=".1f",suffix="%")
        st.markdown("")
        section("Buts marqués vs xG  (🟢V · 🟠N · 🔴D)")
        f5=go.Figure()
        f5.add_trace(go.Bar(x=journees_adv,y=thi_gen["Goals"],name="Buts",marker_color=bar_colors,text=thi_gen["Goals"].astype(int),textposition="outside"))
        f5.add_trace(go.Scatter(x=journees_adv,y=thi_gen["xG"],name="xG",mode="lines+markers",line=dict(color=GREY,width=2)))
        f5.update_layout(**lyt(),height=300); f5.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f5,use_container_width=True)
        section("Tirs totaux vs cadrés")
        f7=go.Figure(); f7=pct_bar_overlay(f7,journees_adv,thi_gen["Shots"],thi_gen["Shots on target"],"Total","Cadrés","rgba(158,158,158,.35)",GREY)
        f7.update_layout(**lyt(),barmode="overlay",height=260); f7.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f7,use_container_width=True)
        section("Distance moyenne des tirs (m)")
        f29=go.Figure()
        f29.add_trace(go.Bar(x=journees_adv,y=thi_idx["Average shot distance"],name="US Thionville",marker_color=GREY,text=thi_idx["Average shot distance"].round(1),textposition="outside"))
        f29.add_trace(go.Bar(x=journees_adv,y=adv_idx["Average shot distance"],name="Adversaires",marker_color=RED,text=adv_idx["Average shot distance"].round(1),textposition="outside"))
        f29.update_layout(**lyt(),barmode="group",height=290); f29.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f29,use_container_width=True)
        section("Tirs par phase de jeu")
        fp=go.Figure()
        fp.add_trace(go.Bar(x=journees_adv,y=thi_off["Positional attacks with shots"],name="Att. positionnelle",marker_color=GREY))
        fp.add_trace(go.Bar(x=journees_adv,y=thi_off["Counterattacks with shots"],name="Contre-attaque",marker_color=RED))
        fp.add_trace(go.Bar(x=journees_adv,y=thi_off["CPA_with_shots"],name="CPA",marker_color=GOLD))
        fp.update_layout(**lyt(),barmode="group",height=300); fp.update_yaxes(gridcolor=BORD)
        st.plotly_chart(fp,use_container_width=True)
        section("% attaques avec tir")
        et=["Positionnelles","Contres","Corners","Coups francs"]
        ett=[thi_off["% Positional attacks with shots"].mean(),thi_off["% Counterattacks with shots"].mean(),thi_off["% Corners with shots"].mean(),thi_off["% Free kicks with shots"].mean()]
        eta=[adv_off["% Positional attacks with shots"].mean(),adv_off["% Counterattacks with shots"].mean(),adv_off["% Corners with shots"].mean(),adv_off["% Free kicks with shots"].mean()]
        f11=go.Figure()
        f11.add_trace(go.Bar(x=et,y=ett,name="US Thionville",marker_color=GREY,text=[f"{v:.1f}%" for v in ett],textposition="outside"))
        f11.add_trace(go.Bar(x=et,y=eta,name="Adversaires",marker_color=RED,text=[f"{v:.1f}%" for v in eta],textposition="outside"))
        f11.update_layout(**lyt(),barmode="group",height=310); f11.update_yaxes(range=[0,100],gridcolor=BORD)
        st.plotly_chart(f11,use_container_width=True)
        section("Attaques positionnelles — total vs avec tir")
        f12=go.Figure(); f12=pct_bar_overlay(f12,journees_adv,thi_off["Positional attacks"],thi_off["Positional attacks with shots"],"Total","Avec tir","rgba(158,158,158,.35)",GREY)
        f12.update_layout(**lyt(),barmode="overlay",height=260); f12.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f12,use_container_width=True)
        section("Centres — total vs réussis")
        f13=go.Figure(); f13=pct_bar_overlay(f13,journees_adv,thi_off["Crosses"],thi_off["Crosses accurate"],"Total","Réussis","rgba(158,158,158,.35)",GREY)
        f13.update_layout(**lyt(),barmode="overlay",height=260); f13.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f13,use_container_width=True)

    elif page=="🛡️ Pressing":
        st.markdown(f"# 🛡️ Pressing — {saison_label}")
        c1,c2,c3,c4,c5=st.columns(5)
        kpi(c1,"🚫 Concédés / m",thi_def["Conceded goals"].mean(),None,fmt=".2f",inverse=True)
        kpi(c2,"📉 Tirs subis / m",thi_def["Shots against"].mean(),adv_def["Shots against"].mean(),fmt=".1f",inverse=True)
        kpi(c3,"🛡️ Tacles %",thi_def["% Sliding tackles successful"].mean(),adv_def["% Sliding tackles successful"].mean(),fmt=".1f",suffix="%")
        kpi(c4,"✋ Intercept. / m",thi_def["Interceptions"].mean(),adv_def["Interceptions"].mean(),fmt=".1f")
        kpi(c5,"🤼 Duels gag. / m",thi_gen["Duels won"].mean(),adv_gen["Duels won"].mean(),fmt=".1f")
        st.markdown("")
        section("Récupérations par zone — par journée")
        rd=get_pitch_data(thi_gen,adv_names,journees,"Recoveries Low","Recoveries Medium","Recoveries High","Recoveries")
        render_pitches(rd,"#00dd55",4)
        st.markdown("")
        section("PPDA par journée")
        pm=thi_idx["PPDA"].mean()
        fpp=go.Figure()
        fpp.add_trace(go.Bar(x=journees_adv,y=thi_idx["PPDA"],name="PPDA TL",marker_color=GREY,text=thi_idx["PPDA"].round(2),textposition="outside"))
        fpp.add_hline(y=pm,line_dash="dash",line_color=GOLD,annotation_text=f"Moy : {pm:.2f}",annotation_font_color=GOLD)
        fpp.update_layout(**lyt(),height=300); fpp.update_yaxes(gridcolor=BORD)
        st.plotly_chart(fpp,use_container_width=True)
        section("Ratio % récup zone off. ÷ % pertes zone déf.")
        rm=thi_gen["ratio_pression"].mean()
        fr=go.Figure()
        fr.add_trace(go.Bar(x=journees_adv,y=thi_gen["ratio_pression"],marker_color=[GREEN if v>=1.0 else GOLD if v>=0.7 else RED for v in thi_gen["ratio_pression"]],text=thi_gen["ratio_pression"].astype(str),textposition="outside"))
        fr.add_hline(y=1.0,line_dash="dash",line_color=GOLD,annotation_text="Équilibre : 1.0",annotation_font_color=GOLD)
        fr.add_hline(y=rm,line_dash="dot",line_color=GREY,annotation_text=f"Moy. : {rm:.2f}",annotation_font_color=TEXT)
        fr.update_layout(**lyt(),height=300); fr.update_yaxes(gridcolor=BORD)
        st.plotly_chart(fr,use_container_width=True)
        section("% récupérations zone offensive (seuil : 13%)")
        pro=thi_gen["pct_recup_high"].round(1); S=13.0
        fro=go.Figure()
        fro.add_trace(go.Bar(x=journees_adv,y=pro,marker_color=[GREEN if v>=S else RED for v in pro],text=[f"{v}%" for v in pro],textposition="outside",textfont=dict(color=TEXT)))
        fro.add_hline(y=S,line_dash="dash",line_color=RED,annotation_text=f"Seuil : {S}%",annotation_font_color=RED)
        fro.add_hline(y=pro.mean(),line_dash="dot",line_color=GREY,annotation_text=f"Moy. : {pro.mean():.1f}%",annotation_font_color=TEXT)
        fro.update_layout(**lyt(),height=300); fro.update_yaxes(gridcolor=BORD,range=[0,max(pro)*1.3])
        st.plotly_chart(fro,use_container_width=True)
        section("Pertes vs Récupérations")
        f9=go.Figure()
        f9.add_trace(go.Bar(x=journees_adv,y=thi_gen["Losses"],name="Pertes",marker_color=RED))
        f9.add_trace(go.Bar(x=journees_adv,y=thi_gen["Recoveries"],name="Récupérations",marker_color=GREY))
        f9.update_layout(**lyt(),barmode="group",height=260); f9.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f9,use_container_width=True)
        ca,cb=st.columns(2)
        with ca:
            section("Duels défensifs gagnés (%)")
            f16=go.Figure(); f16.add_trace(go.Scatter(x=journees_adv,y=thi_def["% Defensive duels won"],mode="lines+markers",line=dict(color=GREY,width=2),fill="tozeroy",fillcolor="rgba(158,158,158,.1)"))
            mv=thi_def["% Defensive duels won"].mean(); f16.add_hline(y=mv,line_dash="dash",line_color=GOLD,annotation_text=f"moy. {mv:.1f}%",annotation_font_color=GOLD)
            f16.update_layout(**lyt(),height=260); f16.update_yaxes(range=[40,90],gridcolor=BORD); st.plotly_chart(f16,use_container_width=True)
        with cb:
            section("Duels aériens gagnés (%)")
            f17=go.Figure(); f17.add_trace(go.Scatter(x=journees_adv,y=thi_def["% Aerial duels won"],mode="lines+markers",line=dict(color=GREY,width=2),fill="tozeroy",fillcolor="rgba(158,158,158,.1)"))
            mv2=thi_def["% Aerial duels won"].mean(); f17.add_hline(y=mv2,line_dash="dash",line_color=GOLD,annotation_text=f"moy. {mv2:.1f}%",annotation_font_color=GOLD)
            f17.update_layout(**lyt(),height=260); f17.update_yaxes(range=[20,90],gridcolor=BORD); st.plotly_chart(f17,use_container_width=True)
        section("Buts marqués vs concédés")
        f8=go.Figure()
        f8.add_trace(go.Scatter(x=journees_adv,y=thi_gen["Goals"],name="Marqués",mode="lines+markers",line=dict(color=GREY,width=2)))
        f8.add_trace(go.Scatter(x=journees_adv,y=buts_adv_list,name="Concédés",mode="lines+markers",line=dict(color=RED,width=2)))
        f8.update_layout(**lyt(),height=260); f8.update_yaxes(gridcolor=BORD); st.plotly_chart(f8,use_container_width=True)
        section("Buts concédés & tirs subis")
        f18=go.Figure()
        f18.add_trace(go.Bar(x=journees_adv,y=thi_def["Conceded goals"],name="Buts concédés",marker_color=RED,text=thi_def["Conceded goals"].astype(int),textposition="outside"))
        f18.add_trace(go.Scatter(x=journees_adv,y=thi_def["Shots against"],name="Tirs subis",mode="lines+markers",line=dict(color=GREY,width=2),yaxis="y2"))
        f18.update_layout(**lyt(),barmode="group",height=290,yaxis2=dict(overlaying="y",side="right",showgrid=False,color=TEXT)); f18.update_yaxes(gridcolor=BORD)
        st.plotly_chart(f18,use_container_width=True)

    elif page=="🔁 En possession":
        st.markdown(f"# 🔁 En possession — {saison_label}")
        section("Pertes de balle par zone — par journée")
        loss_rows=get_pitch_data(thi_gen,adv_names,journees,"Losses Low ","Losses Medium","Losses High","Losses")
        render_pitches(loss_rows,"#ff5500",4)
        st.markdown("")
        pa,pb=st.columns(2)
        with pa:
            section("Passes progressives — total vs réussies")
            f19=go.Figure(); f19=pct_bar_overlay(f19,journees_adv,thi_pass["Progressive passes"],thi_pass["Progressive passes accurate"],"Total","Réussies","rgba(158,158,158,.35)",GREY)
            f19.update_layout(**lyt(),barmode="overlay",height=250); f19.update_yaxes(gridcolor=BORD); st.plotly_chart(f19,use_container_width=True,key="poss_f19")
        with pb:
            section("Passes longues — total vs réussies")
            f20=go.Figure(); f20=pct_bar_overlay(f20,journees_adv,thi_pass["Long passes"],thi_pass["Long passes accurate"],"Total","Réussies","rgba(158,158,158,.35)",GREY)
            f20.update_layout(**lyt(),barmode="overlay",height=250); f20.update_yaxes(gridcolor=BORD); st.plotly_chart(f20,use_container_width=True,key="poss_f20")
        section("Passes / possession")
        f21=go.Figure()
        f21.add_trace(go.Bar(x=journees_adv,y=thi_idx["Average passes per possession"],name="US Thionville",marker_color=GREY,text=thi_idx["Average passes per possession"].round(1),textposition="outside"))
        f21.add_trace(go.Bar(x=journees_adv,y=adv_idx["Average passes per possession"],name="Adversaires",marker_color=RED,text=adv_idx["Average passes per possession"].round(1),textposition="outside"))
        mv21=thi_idx["Average passes per possession"].mean()
        f21.add_hline(y=mv21,line_dash="dash",line_color=GOLD,annotation_text=f"Moy TL : {mv21:.2f}",annotation_font_color=GOLD)
        f21.update_layout(**lyt(),barmode="group",height=290); f21.update_yaxes(gridcolor=BORD); st.plotly_chart(f21,use_container_width=True,key="poss_f21")
        pa,pb=st.columns(2)
        with pa:
            section("% longues balles")
            f22=go.Figure()
            f22.add_trace(go.Bar(x=journees_adv,y=thi_idx["Long pass %"],name="US Thionville",marker_color=GREY,text=thi_idx["Long pass %"].round(1),textposition="outside"))
            f22.add_trace(go.Bar(x=journees_adv,y=adv_idx["Long pass %"],name="Adversaires",marker_color=RED,text=adv_idx["Long pass %"].round(1),textposition="outside"))
            f22.update_layout(**lyt(),barmode="group",height=290); f22.update_yaxes(range=[0,115],gridcolor=BORD); st.plotly_chart(f22,use_container_width=True,key="poss_f22")
        with pb:
            section("Hors-jeu par journée")
            f14b=go.Figure(go.Bar(x=journees_adv,y=thi_off["Offsides"],marker_color=GOLD,text=thi_off["Offsides"].astype(int),textposition="outside"))
            f14b.update_layout(**lyt(),height=290); f14b.update_yaxes(gridcolor=BORD); st.plotly_chart(f14b,use_container_width=True,key="poss_f14b")
        section("Passes vers le tiers final")
        f23=go.Figure(); f23=pct_bar_overlay(f23,journees_adv,thi_pass["Passes to final third"],thi_pass["Passes to final third accurate"],"Total","Réussies","rgba(158,158,158,.35)",GREY)
        f23.update_layout(**lyt(),barmode="overlay",height=250); f23.update_yaxes(gridcolor=BORD); st.plotly_chart(f23,use_container_width=True,key="poss_f23")
        section("Passes progressives (détail)")
        f24=go.Figure(); f24=pct_bar_overlay(f24,journees_adv,thi_pass["Progressive passes"],thi_pass["Progressive passes accurate"],"Total","Réussies","rgba(158,158,158,.35)",GREY)
        f24.update_layout(**lyt(),barmode="overlay",height=250); f24.update_yaxes(gridcolor=BORD); st.plotly_chart(f24,use_container_width=True,key="poss_f24")

    elif page=="📅 Analyse par match":
        st.markdown("# 📅 Analyse par match")
        mo={journees[i]:thi_gen.iloc[i]["Match"] for i in range(len(thi_gen))}
        js=st.selectbox("Sélectionner une journée",list(mo.keys()),format_func=lambda j:f"{j} — vs {adv_names[journees.index(j)]}")
        ms=mo[js]
        im=thi_gen[thi_gen["Match"]==ms].index[0]
        rtg=thi_gen.loc[im]; rag=adv_gen[adv_gen["Match"]==ms].iloc[0]
        rto=thi_off[thi_off["Match"]==ms].iloc[0]; rao=adv_off[adv_off["Match"]==ms].iloc[0]
        rtd=thi_def[thi_def["Match"]==ms].iloc[0]; rad=adv_def[adv_def["Match"]==ms].iloc[0]
        rtp=thi_pass[thi_pass["Match"]==ms].iloc[0]
        rap_df=passe[passe["Team"]!=TEAM]; rap=rap_df[rap_df["Match"]==ms].iloc[0] if len(rap_df[rap_df["Match"]==ms])>0 else rtp
        rti=thi_idx[thi_idx["Match"]==ms].iloc[0]; rai=adv_idx[adv_idx["Match"]==ms].iloc[0]
        an=rag["Team"]; res=get_result(rtg,rag); er={"V":"🟢 Victoire","N":"🟠 Nul","D":"🔴 Défaite"}[res]
        st.markdown(f"### {js} — US Thionville **{int(rtg['Goals'])} – {int(rag['Goals'])}** {an} — {er}")
        st.caption(f"{rtg['Date'].strftime('%d/%m/%Y')} · {int(rtg['Duration'])} min · Schéma : {rtg['Scheme']}")
        section("Comparaison des métriques clés")
        ptl=int(rtg["Passes"]) if int(rtg["Passes"])>0 else 1; padv=int(rag["Passes"]) if int(rag["Passes"])>0 else 1
        mm=[("Buts",int(rtg["Goals"]),int(rag["Goals"]),"vs"),
            ("xG",round(rtg["xG"],2),round(rag["xG"],2),"vs"),
            ("Tirs",int(rtg["Shots"]),int(rag["Shots"]),"vs"),
            ("Tirs cadrés",int(rtg["Shots on target"]),int(rag["Shots on target"]),"self",int(rtg["Shots"]),int(rag["Shots"])),
            ("Possession %",round(rtg["% Possession"],1),round(rag["% Possession"],1),"pct"),
            ("Passes",int(rtg["Passes"]),int(rag["Passes"]),"vs"),
            ("Passes réussies %",round(rtg["% Passes accurate"],1),round(rag["% Passes accurate"],1),"pct"),
            ("Passes réussies",int(rtg["Passes accurate"]),int(rag["Passes accurate"]),"self",ptl,padv),
            ("Pertes",int(rtg["Losses"]),int(rag["Losses"]),"vs"),
            ("Récupérations",int(rtg["Recoveries"]),int(rag["Recoveries"]),"vs"),
            ("Duels gagnés %",round(rtg["% Duels won"],1),round(rag["% Duels won"],1),"pct"),
            ("Att. posit.",int(rto["Positional attacks"]),int(rao["Positional attacks"]),"vs"),
            ("Centres",int(rto["Crosses"]),int(rao["Crosses"]),"vs"),
            ("Interceptions",int(rtd["Interceptions"]),int(rad["Interceptions"]),"vs"),
            ("Fautes",int(rtd["Fouls"]),int(rad["Fouls"]),"vs")]
        rh=""
        for it in mm:
            lb,tl2,av,md=it[0],it[1],it[2],it[3]
            if md=="pct": pt2,pa3=tl2,av
            elif md=="vs":
                tot=tl2+av if (tl2+av)>0 else 1; pt2=tl2/tot*100; pa3=av/tot*100
            elif md=="self":
                tr2,ar2=it[4],it[5]; pt2=tl2/(tr2 if tr2>0 else 1)*100; pa3=av/(ar2 if ar2>0 else 1)*100
            rw='<div style="display:grid;grid-template-columns:80px 1fr 160px 1fr 80px;align-items:center;gap:6px;padding:5px 0;border-bottom:0.5px solid #2a2a2a;">'
            rw+=f'<div style="text-align:right;font-size:14px;font-weight:500;color:#fff;">{tl2}</div>'
            rw+=f'<div style="background:#2a2a2a;border-radius:3px;height:18px;overflow:hidden;"><div style="width:{pt2:.1f}%;height:100%;background:#9e9e9e;margin-left:auto;border-radius:3px;"></div></div>'
            rw+=f'<div style="text-align:center;font-size:12px;color:#8b949e;font-weight:500;">{lb}</div>'
            rw+=f'<div style="background:#2a2a2a;border-radius:3px;height:18px;overflow:hidden;"><div style="width:{pa3:.1f}%;height:100%;background:#ff2d55;border-radius:3px;"></div></div>'
            rw+=f'<div style="text-align:left;font-size:14px;font-weight:500;color:#fff;">{av}</div></div>'
            rh+=rw
        hh='<div style="background:#111111;border:1px solid #2a2a2a;border-radius:10px;padding:16px;">'
        hh+=f'<div style="display:grid;grid-template-columns:80px 1fr 160px 1fr 80px;gap:6px;padding-bottom:8px;border-bottom:1px solid #2a2a2a;margin-bottom:4px;"><div style="text-align:right;font-size:12px;color:#9e9e9e;font-weight:600;">TL</div><div></div><div></div><div></div><div style="text-align:left;font-size:12px;color:#ff2d55;font-weight:600;">{an}</div></div>'+rh+'</div>'
        st.markdown(hh,unsafe_allow_html=True)
        st.markdown("")
        section("Phases de jeu")
        od=[("xG",rto["xG"],rao["xG"],"vs"),("Tirs",rto["Shots"],rao["Shots"],"vs"),
            ("Tirs cadrés",rto["Shots on target"],rao["Shots on target"],"self",int(rtg["Shots"]),int(rag["Shots"])),
            ("Dist.moy.tir(m)",rti["Average shot distance"],rai["Average shot distance"],"vs"),
            ("Att. posit.",rto["Positional attacks"],rao["Positional attacks"],"vs"),
            ("Att.posit.+tir",rto["Positional attacks with shots"],rao["Positional attacks with shots"],"vs"),
            ("% att.posit.tir",rto["% Positional attacks with shots"],rao["% Positional attacks with shots"],"pct"),
            ("Contres",rto["Counterattacks"],rao["Counterattacks"],"vs"),
            ("Corners",rto["Corners"],rao["Corners"],"vs"),("Corners+tir",rto["Corners with shots"],rao["Corners with shots"],"vs"),
            ("Coups francs",rto["Free kicks"],rao["Free kicks"],"vs"),("CF+tir",rto["Free kicks with shots"],rao["Free kicks with shots"],"vs"),
            ("Centres",rto["Crosses"],rao["Crosses"],"vs"),("Centres réussis",rto["Crosses accurate"],rao["Crosses accurate"],"vs"),
            ("% centres",rto["% Crosses accurate"],rao["% Crosses accurate"],"pct")]
        st.markdown(make_mirror_section(od,"TL",an[:20]),unsafe_allow_html=True)
        st.markdown("")
        section("Actions défensives")
        tlr=max(rtg["Recoveries Low"]+rtg["Recoveries Medium"]+rtg["Recoveries High"],1)
        ar2=max(rag["Recoveries Low"]+rag["Recoveries Medium"]+rag["Recoveries High"],1)
        dd=[("PPDA",rti["PPDA"],rai["PPDA"],"vs"),
            ("Tacles réussis %",rtd["% Sliding tackles successful"],rad["% Sliding tackles successful"],"pct"),
            ("Duels déf.gag.%",rtd["% Defensive duels won"],rad["% Defensive duels won"],"pct"),
            ("Duels aér.gag.%",rtd["% Aerial duels won"],rad["% Aerial duels won"],"pct"),
            ("Cartons jaunes",float(rtd["Yellow cards"]),float(rad["Yellow cards"]),"vs"),
            ("Récupérations",rtg["Recoveries"],rag["Recoveries"],"vs"),
            ("Récup.hautes %",rtg["Recoveries High"]/tlr*100,rag["Recoveries High"]/ar2*100,"pct"),
            ("Récup.méd.%",rtg["Recoveries Medium"]/tlr*100,rag["Recoveries Medium"]/ar2*100,"pct"),
            ("Récup.basses%",rtg["Recoveries Low"]/tlr*100,rag["Recoveries Low"]/ar2*100,"pct"),
            ("Duels gagnés",rtg["Duels won"],rag["Duels won"],"vs"),
            ("% Duels gagnés",rtg["% Duels won"],rag["% Duels won"],"pct")]
        st.markdown(make_mirror_section(dd,"TL",an[:20]),unsafe_allow_html=True)
        st.markdown("")
        section("Passing")
        p1=float(rtp["Passes"]) if float(rtp["Passes"])>0 else 1
        p2=float(rap["Passes"]) if float(rap["Passes"])>0 else 1
        pd_=[("Tempo",rti["Match tempo"],rai["Match tempo"],"vs"),
            ("% longues balles",rti["Long pass %"],rai["Long pass %"],"pct"),
            ("Passes/possession",rti["Average passes per possession"],rai["Average passes per possession"],"vs"),
            ("Passes",rtp["Passes"],rap["Passes"],"vs"),
            ("Passes réussies",rtp["Passes accurate"],rap["Passes accurate"],"self",p1,p2),
            ("% passes réuss.",rtp["% Passes accurate"],rap["% Passes accurate"],"pct"),
            ("Passes avant",rtp["Forward passes"],rap["Forward passes"],"vs"),
            ("% passes av.",rtp["% Forward passes accurate"],rap["% Forward passes accurate"],"pct"),
            ("Passes longues",rtp["Long passes"],rap["Long passes"],"vs"),
            ("% passes long.",rtp["% Long passes accurate"],rap["% Long passes accurate"],"pct"),
            ("Passes tiers fin.",rtp["Passes to final third"],rap["Passes to final third"],"vs"),
            ("% TF réussies",rtp["% Passes to final third accurate"],rap["% Passes to final third accurate"],"pct"),
            ("Passes prog.",rtp["Progressive passes"],rap["Progressive passes"],"vs"),
            ("% passes prog.",rtp["% Progressive passes accurate"],rap["% Progressive passes accurate"],"pct")]
        st.markdown(make_mirror_section(pd_,"TL",an[:20]),unsafe_allow_html=True)
