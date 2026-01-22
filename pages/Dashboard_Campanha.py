# app.py
# DBV | Dashboard de Gamificação (Bem Visual) — Corrida com “rostos”, checkpoints e linha de chegada quadriculada
# + Pódio bem visual (com SVG de pódio)
#
# Rodar:
#   pip install streamlit pandas numpy plotly pillow
#   streamlit run app.py

import base64
import math
from dataclasses import dataclass
from datetime import date
from io import BytesIO
from textwrap import dedent

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(
    page_title="DBV | Corrida de Campanha",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# THEME / CORES
# =========================
DBV_BG = "#0B0F17"
PANEL_BG = "#101827"
CARD_BG = "#0F1624"
TEXT = "#E8EEF7"
MUTED = "#9AA4B2"
ACCENT = "#2ecc71"

GOLD = "#D4AF37"
SILVER = "#C0C0C0"
BRONZE = "#CD7F32"

LANE_A = "rgba(255,255,255,0.045)"
LANE_B = "rgba(255,255,255,0.025)"


# =========================
# SIDEBAR: CONFIGURAÇÃO
# =========================
st.sidebar.markdown("## ⚙️ Configuração")

modo_tv = st.sidebar.toggle("Modo TV (ocultar barra superior)", value=True)
compactar = st.sidebar.toggle("Compactar layout (1 tela)", value=True)

campanha = st.sidebar.text_input("Nome da campanha", value="Renda Variável")
meta_global_m = st.sidebar.number_input("Meta global (em milhões)", min_value=0.0, value=30.0, step=1.0)

col_d = st.sidebar.columns(2)
inicio = col_d[0].date_input("Início", value=date.today().replace(day=1))
fim = col_d[1].date_input("Fim", value=date.today().replace(day=min(date.today().day, 28)))

st.sidebar.markdown("### 🚩 Checkpoints")
cp_text = st.sidebar.text_input("Percentuais (vírgula)", value="25,50,75,100")

st.sidebar.markdown("### 🧪 Modo Beta")
n_assessores = st.sidebar.slider("Qtd. de assessores", 12, 60, 28, 1)
seed = st.sidebar.number_input("Seed", min_value=0, value=42, step=1)
regen = st.sidebar.button("🔄 Gerar novos dados")


# =========================
# CSS (IMPORTANTE: não cortar topo + pódio não virar codeblock)
# =========================
# Se modo_tv=True, escondemos header e toolbar, e aí podemos reduzir padding-top sem cortar nada.
# Se modo_tv=False, precisamos manter padding-top maior.
top_pad = "0.55rem" if (modo_tv and compactar) else ("1.0rem" if modo_tv else "3.6rem")
bottom_pad = "0.55rem" if compactar else "1.2rem"

hide_chrome_css = ""
if modo_tv:
    hide_chrome_css = """
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    div[data-testid="stToolbar"] { visibility: hidden; height: 0px; }
    div[data-testid="stDecoration"] { visibility: hidden; height: 0px; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    """

metric_value_size = "30px" if compactar else "34px"
metric_label_size = "13px" if compactar else "14px"

race_height = 360 if compactar else 430
podium_height = 250 if compactar else 280

st.markdown(
    f"""
    <style>
      {hide_chrome_css}

      .stApp {{
        background: {DBV_BG};
        color: {TEXT};
      }}

      .block-container {{
        padding-top: {top_pad};
        padding-bottom: {bottom_pad};
      }}

      /* MÉTRICAS (mais compactas) */
      div[data-testid="stMetric"] {{
        background: {CARD_BG};
        border: 1px solid rgba(255,255,255,0.08);
        padding: {"10px 12px 8px 12px" if compactar else "14px 14px 10px 14px"};
        border-radius: 14px;
      }}
      div[data-testid="stMetricLabel"] p {{
        font-size: {metric_label_size} !important;
        color: {MUTED} !important;
      }}
      div[data-testid="stMetricValue"] {{
        font-size: {metric_value_size} !important;
        color: {TEXT} !important;
        line-height: 1.05 !important;
      }}

      .subtle {{
        color: {MUTED};
        font-size: 12px;
      }}

      /* Barra de progresso fina */
      .mini-progress {{
        width: 100%;
        height: 9px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.10);
        overflow: hidden;
        margin-top: 6px;
        margin-bottom: {"10px" if compactar else "16px"};
      }}
      .mini-progress > div {{
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(46,204,113,0.95), rgba(46,204,113,0.65));
      }}

      /* PÓDIO */
      .podium-wrap{{
        background: #101827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        height: {podium_height}px; /* ou 250px */
      }}
      /* SVG do pódio SEM CORTE */
      .podium-bg{{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: contain;             /* mostra inteiro */
        object-position: center bottom;  /* degraus no "chão" */
        opacity: 0.95;
        pointer-events: none;
      }}
      /* Overlay do atleta: agora ANCORADO PELO BOTTOM (topo do degrau) */
      .podium-person{{
        position: absolute;
        z-index: 5;
        left: 50%;
        transform: translateX(-50%) translateY(-8px); /* levanta um tico acima do degrau */
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        text-align: center;
        pointer-events: none;
        width: 320px;
        max-width: 34vw;
      }}
      /* Centros em X (mesmos centros do SVG: 300 / 600 / 900 => 25% / 50% / 75%) */
      /* E bottom = topo exato do degrau (calculado do viewBox 300px de altura) */
      .podium-person.p1{{ left: 50%; bottom: 70%; }}       /* 1º lugar (y=90)  */
      .podium-person.p2{{ left: 25%; bottom: 53.333%; }}   /* 2º lugar (y=140) */
      .podium-person.p3{{ left: 75%; bottom: 45%; }}       /* 3º lugar (y=165) */
      .podium-avatar{{
        width: 74px;
        height: 74px;
        border-radius: 999px;
        border: 3px solid rgba(255,255,255,0.22);
        box-shadow: 0 14px 26px rgba(0,0,0,0.45);
        background: rgba(0,0,0,0.15);
      }}
      .podium-avatar.pill-gold{{ border-color: rgba(212,175,55,0.85); }}
      .podium-avatar.pill-silver{{ border-color: rgba(192,192,192,0.85); }}
      .podium-avatar.pill-bronze{{ border-color: rgba(205,127,50,0.85); }}
      .podium-name-tag{{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(15,22,36,0.78);
        border: 1px solid rgba(255,255,255,0.12);
        font-weight: 900;
        font-size: 14px;
        line-height: 1.1;
        color: #E8EEF7;
        backdrop-filter: blur(6px);
        white-space: nowrap;
      }}

      section[data-testid="stSidebar"] {{
        background: {PANEL_BG};
        border-right: 1px solid rgba(255,255,255,0.07);
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# UTIL
# =========================
def format_brl_m(x: float) -> str:
    return f"R$ {x:,.2f} M".replace(",", "X").replace(".", ",").replace("X", ".")

def pct_str(x: float) -> str:
    return f"{x*100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_checkpoints(text: str, fallback=(0.25, 0.50, 0.75, 1.0)) -> list[float]:
    parts = [p.strip() for p in text.replace(";", ",").split(",") if p.strip()]
    vals = []
    for p in parts:
        try:
            v = float(p)
            if v > 1.0:
                v = v / 100.0
            vals.append(v)
        except ValueError:
            pass
    if not vals:
        vals = list(fallback)
    vals = [min(max(v, 0.0), 1.0) for v in vals if v > 0]
    vals = sorted(set(vals))
    if 1.0 not in vals:
        vals.append(1.0)
    return sorted(set(vals))

checkpoints = parse_checkpoints(cp_text)

# =========================
# AVATAR (rosto) — Pillow
# =========================
def _safe_font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except Exception:
        return ImageFont.load_default()

@st.cache_data(show_spinner=False, max_entries=512)
def make_face_avatar(name: str, seed: int, size: int = 128) -> str:
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    palette = [
        (46, 204, 113), (52, 152, 219), (155, 89, 182),
        (241, 196, 15), (230, 126, 34), (231, 76, 60),
        (26, 188, 156), (149, 165, 166),
    ]
    bg = palette[int(rng.integers(0, len(palette)))]

    pad = int(size * 0.06)
    d.ellipse([pad, pad, size - pad, size - pad], fill=(*bg, 255))
    d.ellipse([pad, pad, size - pad, size - pad], outline=(255, 255, 255, 45), width=3)

    skin_tones = [(238, 205, 180), (224, 189, 165), (198, 134, 66), (141, 85, 36), (255, 219, 172)]
    skin = skin_tones[int(rng.integers(0, len(skin_tones)))]
    face_r = int(size * 0.58)
    cx, cy = size // 2, int(size * 0.54)
    d.ellipse([cx - face_r // 2, cy - face_r // 2, cx + face_r // 2, cy + face_r // 2], fill=(*skin, 255))

    hair_colors = [(30, 30, 35), (60, 45, 35), (90, 70, 50), (20, 15, 10)]
    hair = hair_colors[int(rng.integers(0, len(hair_colors)))]
    hair_h = int(face_r * 0.35)
    d.pieslice(
        [cx - face_r // 2, cy - face_r // 2, cx + face_r // 2, cy + face_r // 2],
        start=180, end=360, fill=(*hair, 255)
    )
    for _ in range(int(rng.integers(2, 5))):
        x = int(cx + rng.normal(0, face_r * 0.12))
        w = int(face_r * rng.uniform(0.08, 0.14))
        h = int(face_r * rng.uniform(0.10, 0.16))
        d.ellipse([x - w, cy - face_r // 2 + hair_h - h, x + w, cy - face_r // 2 + hair_h + h], fill=(*hair, 255))

    eye_y = int(cy - face_r * 0.08)
    eye_dx = int(face_r * 0.18)
    eye_r = max(2, int(size * 0.03))
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        d.ellipse([ex - eye_r, eye_y - eye_r, ex + eye_r, eye_y + eye_r], fill=(25, 25, 30, 255))
        d.ellipse([ex - eye_r // 2, eye_y - eye_r // 2, ex, eye_y], fill=(255, 255, 255, 170))

    mouth_y = int(cy + face_r * 0.18)
    mouth_w = int(face_r * 0.26)
    d.arc([cx - mouth_w, mouth_y - 10, cx + mouth_w, mouth_y + 16], start=10, end=170, fill=(120, 60, 60, 220), width=4)

    initials = "".join([p[0] for p in name.split()[:2]]).upper()
    font = _safe_font(int(size * 0.18))
    bbox = d.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tag_w = int(size * 0.42)
    tag_h = int(size * 0.20)
    tag_x0 = int(size * 0.29)
    tag_y0 = int(size * 0.78)
    d.rounded_rectangle([tag_x0, tag_y0, tag_x0 + tag_w, tag_y0 + tag_h], radius=14, fill=(0, 0, 0, 120))
    d.text((tag_x0 + (tag_w - tw) // 2, tag_y0 + (tag_h - th) // 2 - 2), initials, font=font, fill=(255, 255, 255, 235))

    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


# =========================
# DADOS FICTÍCIOS
# =========================
def generate_fake_data(n_assessores: int, meta_global_m: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    first_names = [
        "Ana", "Bruno", "Carla", "Diego", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Julia",
        "Karla", "Lucas", "Marina", "Nicolas", "Otavio", "Patricia", "Rafael", "Sabrina", "Thiago", "Vanessa",
        "Wagner", "Yasmin", "Felipe", "Camila", "Renato", "Beatriz", "Gustavo", "Aline", "Rodrigo", "Isabela",
        "João", "Marcos", "Paula", "Letícia", "Vitor", "Pedro", "Larissa", "Daniel", "Luiza", "Amanda",
    ]
    last_names = [
        "Silva", "Souza", "Oliveira", "Santos", "Lima", "Pereira", "Carvalho", "Gomes", "Ribeiro", "Almeida",
        "Costa", "Ferreira", "Rocha", "Martins", "Barbosa", "Cardoso", "Moura", "Teixeira", "Correia", "Araujo"
    ]

    names = set()
    while len(names) < n_assessores:
        names.add(f"{rng.choice(first_names)} {rng.choice(last_names)}")
    names = list(names)

    base = rng.lognormal(mean=0.0, sigma=0.80, size=n_assessores)
    base = base / base.max()
    cap_m = base * (meta_global_m * rng.uniform(0.70, 1.35))

    df = pd.DataFrame({"assessor": names, "captacao_m": np.clip(cap_m, 0.0, None)})
    df["pct_meta_global"] = np.where(meta_global_m > 0, df["captacao_m"] / meta_global_m, 0.0)
    return df.sort_values("captacao_m", ascending=False).reset_index(drop=True)

if "df_race" not in st.session_state or regen:
    st.session_state.df_race = generate_fake_data(n_assessores, float(meta_global_m), int(seed))

df = st.session_state.df_race.copy()


# =========================
# CORRIDA (Plotly)
# =========================
@dataclass
class RaceVisualConfig:
    x_pad_ratio: float = 0.12
    avatar_sizey: float = 0.72
    fig_height: int = race_height
    show_names_left: bool = True
    show_values_near_avatar: bool = True

def build_race_figure(df_top: pd.DataFrame, meta_global_m: float, checkpoints: list[float], camp: str, seed: int) -> go.Figure:
    cfg = RaceVisualConfig()

    df_top = df_top.copy().reset_index(drop=True)
    leader = float(df_top["captacao_m"].max()) if len(df_top) else 0.0
    x_ref = max(leader, float(meta_global_m))
    x_max = x_ref * (1.0 + cfg.x_pad_ratio) if x_ref > 0 else 1.0

    fig = go.Figure()

    # Lanes alternadas
    for i in range(len(df_top)):
        fig.add_shape(
            type="rect",
            x0=0, x1=x_max,
            y0=i - 0.5, y1=i + 0.5,
            fillcolor=LANE_A if i % 2 == 0 else LANE_B,
            line=dict(width=0),
            layer="below",
        )

    # Pistas / progresso
    for i, row in df_top.iterrows():
        x = min(float(row["captacao_m"]), x_max * 0.985)
        fig.add_shape(type="line", x0=0, x1=x, y0=i, y1=i,
                      line=dict(color="rgba(46,204,113,0.45)", width=10), layer="below")
        fig.add_shape(type="line", x0=0, x1=x_max, y0=i, y1=i,
                      line=dict(color="rgba(255,255,255,0.10)", width=6), layer="below")

    # Checkpoints
    for cp in checkpoints:
        if meta_global_m <= 0:
            continue
        x_cp = meta_global_m * cp
        is_finish = abs(cp - 1.0) < 1e-9

        fig.add_shape(
            type="line",
            x0=x_cp, x1=x_cp,
            y0=-0.5, y1=len(df_top) - 0.5,
            line=dict(
                color="rgba(255,255,255,0.28)" if not is_finish else "rgba(255,255,255,0.95)",
                width=2 if not is_finish else 3,
                dash="dot" if not is_finish else "dash",
            ),
            layer="above",
        )
        label = "🏁 META" if is_finish else f"🚩 {int(round(cp*100))}%"
        fig.add_annotation(
            x=x_cp, y=-0.85, text=label, showarrow=False,
            font=dict(size=12 if is_finish else 11,
                      color="rgba(255,255,255,0.85)" if is_finish else "rgba(255,255,255,0.55)"),
            yanchor="top",
        )

    # Linha de chegada quadriculada
    if meta_global_m > 0:
        finish_x = meta_global_m
        strip_w = max(meta_global_m * 0.008, x_max * 0.006)
        cell_h = 0.22
        y_start, y_end = -0.5, len(df_top) - 0.5
        rows = int(math.ceil((y_end - y_start) / cell_h))

        for r in range(rows):
            y0 = y_start + r * cell_h
            y1 = min(y0 + cell_h, y_end)
            for c in (0, 1):
                x0 = finish_x - strip_w + c * strip_w
                x1 = finish_x + c * strip_w
                is_light = (r + c) % 2 == 0
                fig.add_shape(
                    type="rect",
                    x0=x0, x1=x1, y0=y0, y1=y1,
                    fillcolor="rgba(245,245,245,0.95)" if is_light else "rgba(25,25,25,0.75)",
                    line=dict(width=0),
                    layer="above",
                )
        fig.add_shape(
            type="rect",
            x0=finish_x - strip_w, x1=finish_x + strip_w,
            y0=-0.5, y1=len(df_top) - 0.5,
            line=dict(color="rgba(255,255,255,0.45)", width=1),
            fillcolor="rgba(0,0,0,0)",
            layer="above",
        )

    fig.add_annotation(
        x=0, y=-0.85, text="🚦 START", showarrow=False,
        font=dict(size=12, color="rgba(255,255,255,0.60)"),
        xanchor="left", yanchor="top",
    )

    # Avatares + labels
    images, hx, hy, ht = [], [], [], []

    # tamanho do avatar em X (clamp p/ ficar bonito em metas pequenas/grandes)
    if meta_global_m > 0:
        avatar_sizex = meta_global_m * 0.045
    else:
        avatar_sizex = x_max * 0.05
    avatar_sizex = max(avatar_sizex, x_max * 0.025)
    avatar_sizex = min(avatar_sizex, x_max * 0.065)

    for i, row in df_top.iterrows():
        name = str(row["assessor"])
        x = min(float(row["captacao_m"]), x_max * 0.985)

        avatar = make_face_avatar(name, seed=seed + i * 17, size=128)
        images.append(dict(
            source=avatar, xref="x", yref="y",
            x=x, y=i, sizex=avatar_sizex, sizey=cfg.avatar_sizey,
            xanchor="center", yanchor="middle", layer="above", opacity=1.0
        ))

        if cfg.show_names_left:
            fig.add_annotation(
                x=0, y=i, text=f"<b>{name}</b>", showarrow=False,
                xanchor="left", yanchor="middle",
                font=dict(size=12, color="rgba(255,255,255,0.86)"),
                xshift=8
            )

        if cfg.show_values_near_avatar:
            fig.add_annotation(
                x=x, y=i, text=f"<b>{format_brl_m(float(row['captacao_m']))}</b>", showarrow=False,
                xanchor="left", yanchor="middle",
                font=dict(size=12, color="rgba(255,255,255,0.92)"),
                xshift=18,
                bgcolor="rgba(15, 22, 36, 0.65)",
                bordercolor="rgba(255,255,255,0.10)",
                borderwidth=1,
                borderpad=3,
            )

        hx.append(x)
        hy.append(i)
        pct = float(row["pct_meta_global"]) if meta_global_m > 0 else 0.0
        ht.append(
            f"<b>{name}</b><br>"
            f"Captação: {format_brl_m(float(row['captacao_m']))}<br>"
            f"Meta global: {format_brl_m(float(meta_global_m))}<br>"
            f"Atingimento: {pct_str(pct)}"
        )

    fig.update_layout(images=images)
    fig.add_trace(go.Scatter(
        x=hx, y=hy, mode="markers",
        marker=dict(size=8, color="rgba(0,0,0,0)"),
        hovertemplate="%{text}<extra></extra>",
        text=ht, showlegend=False,
    ))

    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"🏁 Corrida da Campanha — Top {len(df_top)} | {camp}",
            x=0.01, xanchor="left",
            font=dict(size=16 if compactar else 18, color=TEXT),
        ),
        height=cfg.fig_height,
        margin=dict(l=10, r=10, t=52 if compactar else 60, b=8),
        paper_bgcolor=DBV_BG,
        plot_bgcolor=DBV_BG,
        xaxis=dict(range=[0, x_max], showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        yaxis=dict(range=[len(df_top) - 0.5, -0.5], showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
    )

    return fig


# =========================
# SVG do Pódio (base64)
# =========================
def podium_svg_base64() -> str:
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300">
  <defs>
    <linearGradient id="g" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#1b2640"/>
      <stop offset="1" stop-color="#0f1624"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#000" flood-opacity="0.35"/>
    </filter>
  </defs>

  <rect x="0" y="0" width="1200" height="300" fill="url(#g)"/>

  <rect x="0" y="240" width="1200" height="60" fill="rgba(255,255,255,0.04)"/>

  <g filter="url(#shadow)">
    <rect x="160" y="140" width="280" height="110" rx="18" fill="rgba(255,255,255,0.09)" stroke="rgba(255,255,255,0.12)"/>
    <rect x="460" y="90"  width="280" height="160" rx="18" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.14)"/>
    <rect x="760" y="165" width="280" height="85"  rx="18" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.12)"/>
  </g>

  <text x="300" y="210" font-size="56" font-family="Arial" font-weight="900" fill="{SILVER}" text-anchor="middle">2</text>
  <text x="600" y="205" font-size="64" font-family="Arial" font-weight="900" fill="{GOLD}" text-anchor="middle">1</text>
  <text x="900" y="215" font-size="56" font-family="Arial" font-weight="900" fill="{BRONZE}" text-anchor="middle">3</text>

  <circle cx="1060" cy="70" r="46" fill="rgba(46,204,113,0.14)"/>
  <circle cx="1100" cy="90" r="22" fill="rgba(52,152,219,0.12)"/>
  <circle cx="1130" cy="55" r="14" fill="rgba(212,175,55,0.12)"/>
</svg>
""".strip()
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


# =========================
# KPIs (TOPO) + PROGRESSO FINO
# =========================
total_captado_m = float(df["captacao_m"].sum()) if len(df) else 0.0
atingimento = (total_captado_m / meta_global_m) if meta_global_m > 0 else 0.0

dias_totais = max((fim - inicio).days + 1, 1)
dias_passados = max(min((date.today() - inicio).days + 1, dias_totais), 0)
dias_restantes = max((fim - date.today()).days, 0)
progresso_prazo = dias_passados / dias_totais

k1, k2, k3, k4, k5 = st.columns([1.25, 1.05, 1.0, 1.0, 1.2], gap="small")
k1.metric("Total Captado", format_brl_m(total_captado_m))
k2.metric("Atingimento da Meta", pct_str(atingimento))
k3.metric("Meta Global", format_brl_m(float(meta_global_m)))
k4.metric("Dias Restantes", f"{dias_restantes}")
k5.metric("Progresso do Prazo", pct_str(progresso_prazo))

progress_pct = int(min(max(atingimento, 0.0), 1.0) * 100)
st.markdown("<div class='subtle'>Progresso da meta</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='mini-progress'><div style='width:{progress_pct}%;'></div></div>",
    unsafe_allow_html=True
)


# =========================
# CORRIDA
# =========================
df_top10 = df.sort_values("captacao_m", ascending=False).head(10)
fig = build_race_figure(
    df_top=df_top10,
    meta_global_m=float(meta_global_m),
    checkpoints=checkpoints,
    camp=campanha,
    seed=int(seed) * 1000 + 7,
)
st.plotly_chart(fig, use_container_width=True)


# =========================
# PÓDIO
# =========================
st.markdown("### 🏆 Pódio (Top 3)")

top3 = df.sort_values("captacao_m", ascending=False).head(3).copy()
while len(top3) < 3:
    top3 = pd.concat(
        [top3, pd.DataFrame([{"assessor": "—", "captacao_m": 0.0, "pct_meta_global": 0.0}])],
        ignore_index=True,
    )

a1 = make_face_avatar(str(top3.iloc[0]["assessor"]), seed=int(seed) + 101, size=140)
a2 = make_face_avatar(str(top3.iloc[1]["assessor"]), seed=int(seed) + 202, size=140)
a3 = make_face_avatar(str(top3.iloc[2]["assessor"]), seed=int(seed) + 303, size=140)

podium_bg = podium_svg_base64()

def podium_person_html(pos_class: str, medal: str, pill_class: str, avatar_uri: str, name: str) -> str:
    return (
        f'<div class="podium-person {pos_class}">'
        f'  <img class="podium-avatar {pill_class}" src="{avatar_uri}" />'
        f'  <div class="podium-name-tag">{medal} {name}</div>'
        f'</div>'
    )

# Monta o HTML "flat" (sem linhas indentadas com 4 espaços)
podium_html = (
    f'<div class="podium-wrap">'
    f'  <img class="podium-bg" src="{podium_bg}" />'
    f'  {podium_person_html("p2", "🥈", "pill-silver", a2, str(top3.iloc[1]["assessor"]))}'
    f'  {podium_person_html("p1", "🥇", "pill-gold",   a1, str(top3.iloc[0]["assessor"]))}'
    f'  {podium_person_html("p3", "🥉", "pill-bronze", a3, str(top3.iloc[2]["assessor"]))}'
    f'</div>'
)

st.markdown(podium_html, unsafe_allow_html=True)
