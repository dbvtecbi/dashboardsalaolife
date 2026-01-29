import streamlit as st
import pandas as pd
import random
import textwrap

# ==============================================================================
# 0. CONFIG (AJUSTE FINO)
# ==============================================================================
NOME_DA_CAMPANHA = "Campanha 2026"
META_CAMPANHA = 1_000_000.0

UI_SCALE = 1.00
TOP_N_RAIAS = 8

random.seed(42)

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="DBV Race - Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 2. DADOS
# ==============================================================================
def gerar_dados_campanha(meta: float) -> pd.DataFrame:
    nomes = [
        "Arthur Linhares", "Bruno Silva", "Carla Dias", "Daniel Morone",
        "Eduardo Parente", "Fabiane Souza", "Gustavo Levy", "Henrique Vieira",
        "Isabela Martins", "João Goldenberg", "Lucas Mendes", "Mariana Costa"
    ]

    dados = []
    for nome in nomes:
        captado = random.uniform(200_000, 1_100_000)
        foto_url = (
            "https://ui-avatars.com/api/"
            f"?name={nome.replace(' ', '+')}"
            "&background=0D1117&color=2ecc71&bold=true&size=256"
        )

        pct = (captado / meta) * 100
        pct = max(3, min(pct, 96))

        dados.append(
            {
                "nome": nome,
                "captado": float(captado),
                "meta": float(meta),
                "foto": foto_url,
                "pct": float(pct),
            }
        )

    df = pd.DataFrame(dados).sort_values("captado", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


df_campanha = gerar_dados_campanha(META_CAMPANHA)
df_top = df_campanha.head(TOP_N_RAIAS).copy()
df_podium = df_campanha.head(3).copy()

total_arrecadado = float(df_campanha["captado"].sum())
media_por_assessor = float(df_campanha["captado"].mean())
lider_nome = df_top.iloc[0]["nome"].split()[0]

META_ANUAL = META_CAMPANHA * 12
pct_anual = max(0.0, min((total_arrecadado / META_ANUAL) * 100, 100.0))

# ==============================================================================
# 3. HELPERS
# ==============================================================================
def html_clean(s: str) -> str:
    s = textwrap.dedent(s)
    return "\n".join(line.lstrip() for line in s.splitlines()).strip()


def format_brl(valor: float) -> str:
    s = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def format_k(valor: float) -> str:
    if valor >= 1_000_000:
        return f"{(valor / 1_000_000):.1f}M"
    return f"{valor / 1000:.0f}k"


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(v, hi))


# ==============================================================================
# 4. CSS
# ==============================================================================
st.markdown(
    html_clean(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');

:root {{
  --bg0: #0b1110;
  --border: rgba(255,255,255,0.12);
  --border2: rgba(255,255,255,0.08);
  --txt: rgba(255,255,255,0.92);
  --muted: rgba(255,255,255,0.58);

  --green: #00ff88;
  --green2: #2ecc71;

  --gold: #FFD700;
  --silver: #D9D9D9;
  --bronze: #CD7F32;

  --shadow: 0 18px 55px rgba(0,0,0,0.45);
  --shadow-in: inset 0 0 28px rgba(0,0,0,0.55);

  --r: 18px;
}}

html, body {{
  height: 100%;
  overflow: hidden !important;
}}

#MainMenu, header, footer {{
  display: none !important;
}}

.stApp {{
  font-family: 'Montserrat', sans-serif;
  color: var(--txt);
  background:
    radial-gradient(1200px 520px at 50% 5%, rgba(0,255,136,0.14), transparent 60%),
    radial-gradient(900px 420px at 10% 40%, rgba(46,204,113,0.10), transparent 60%),
    linear-gradient(180deg, #0c1412 0%, #0a0f0e 100%) !important;
  overflow: hidden !important;
}}

.block-container {{
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
}}

section.main > div {{
  padding-top: 0 !important;
}}

[data-testid="stSidebar"] {{
  display: none !important;
}}

:root {{
  --scale: {UI_SCALE};
}}

.dashboard {{
  height: calc(100vh - 8px);
  width: 100vw;
  box-sizing: border-box;
  padding: calc(10px * var(--scale)) calc(18px * var(--scale));
  display: grid;
  grid-template-rows: calc(10vh * var(--scale)) 1fr calc(18vh * var(--scale));
  gap: calc(10px * var(--scale));
  overflow: hidden;
}}

/* ========================= HEADER ========================= */
.header {{
  display: grid;
  grid-template-columns: 1.1fr 2fr 1.1fr;
  align-items: center;
  padding: 0 calc(18px * var(--scale));
  border-radius: var(--r);
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}}

.brand {{
  display: flex;
  align-items: center;
  gap: calc(10px * var(--scale));
}}

.brand-badge {{
  width: calc(44px * var(--scale));
  height: calc(44px * var(--scale));
  border-radius: 14px;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 30% 30%, rgba(0,255,136,0.35), transparent 60%),
    rgba(0,0,0,0.35);
  border: 1px solid var(--border2);
  box-shadow: 0 0 18px rgba(0,255,136,0.18);
}}

.brand-badge span {{
  font-weight: 900;
  letter-spacing: 1px;
  background: linear-gradient(135deg, var(--green2), var(--green), #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: calc(18px * var(--scale));
}}

.brand-text {{
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}}

.brand-text .small {{
  font-size: calc(11px * var(--scale));
  color: var(--muted);
  font-weight: 700;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}}

.brand-text .big {{
  font-size: calc(18px * var(--scale));
  font-weight: 900;
  letter-spacing: 0.6px;
}}

.title {{
  text-align: center;
  font-weight: 900;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: calc(22px * var(--scale));
  background: linear-gradient(90deg, #fff, var(--green));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.goal {{
  text-align: right;
}}

.goal .label {{
  font-size: calc(10px * var(--scale));
  color: var(--muted);
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}}

.goal .value {{
  font-size: calc(18px * var(--scale));
  font-weight: 900;
  color: var(--green);
  text-shadow: 0 0 14px rgba(0,255,136,0.25);
}}

/* ========================= MIDDLE ========================= */
.middle {{
  display: grid;
  grid-template-columns: 3fr 1.05fr;
  gap: calc(10px * var(--scale));
  min-height: 0;
}}

.panel {{
  border-radius: var(--r);
  border: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
  overflow: hidden;
}}

.track {{
  position: relative;
  padding: calc(10px * var(--scale)) 0;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  height: 100%;
  min-height: 0;
  box-shadow: var(--shadow-in);
}}

.track:before {{
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(700px 260px at 20% 30%, rgba(0,255,136,0.10), transparent 60%),
    repeating-linear-gradient(90deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 28px);
  opacity: 0.35;
  pointer-events: none;
}}

.finish {{
  position: absolute;
  right: calc(34px * var(--scale));
  top: calc(12px * var(--scale));
  bottom: calc(12px * var(--scale));
  width: calc(18px * var(--scale));
  border-radius: 6px;
  background-image:
    linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000),
    linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000);
  background-color: #fff;
  background-position: 0 0, 9px 9px;
  background-size: 18px 18px;
  border: 2px solid #fff;
  box-shadow: 0 0 18px rgba(0,255,136,0.35);
  z-index: 2;
}}

.finish-label {{
  position: absolute;
  right: calc(6px * var(--scale));
  top: 50%;
  transform: translateY(-50%);
  writing-mode: vertical-rl;
  text-orientation: mixed;
  letter-spacing: 3px;
  font-weight: 900;
  font-size: calc(10px * var(--scale));
  color: rgba(0,255,136,0.95);
  text-shadow: 0 0 10px rgba(0,0,0,0.8);
  z-index: 3;
  pointer-events: none;
}}

.lane {{
  position: relative;
  width: 100%;
  flex: 1;
  display: flex;
  align-items: center;
}}

.lane-line {{
  position: absolute;
  left: calc(12px * var(--scale));
  right: calc(46px * var(--scale));
  top: 50%;
  transform: translateY(-50%);
  height: calc(18px * var(--scale));
  border-radius: 6px;
  background: linear-gradient(180deg, rgba(255,255,255,0.09), rgba(255,255,255,0.02));
  border-top: 1px solid rgba(255,255,255,0.14);
  border-bottom: 1px solid rgba(0,0,0,0.35);
  box-shadow: inset 0 0 10px rgba(0,0,0,0.45);
  z-index: 0;
}}

.lane-dash {{
  position: absolute;
  left: calc(14px * var(--scale));
  right: calc(50px * var(--scale));
  top: 50%;
  transform: translateY(-50%);
  height: 2px;
  background: repeating-linear-gradient(90deg, rgba(255,255,255,0.20) 0px, rgba(255,255,255,0.20) 8px, transparent 8px, transparent 18px);
  opacity: 0.35;
  z-index: 1;
}}

/* =========================
   PERSONAGEM (MENOR PARA NÃO ENCOSTAR NA RAIA DE CIMA/BAIXO)
   - continua colado (gap 0), sem sobrepor
========================= */
.racer {{
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  z-index: 10;
  transition: left 1.5s cubic-bezier(0.25, 1, 0.5, 1);
}}

.racer.near {{
  transform: translate(-78%, -50%);
}}

.avatar {{
  width: calc(30px * var(--scale));     /* ↓ 34 -> 30 */
  height: calc(30px * var(--scale));    /* ↓ 34 -> 30 */
  border-radius: 999px;
  border: 1.5px solid rgba(255,255,255,0.92); /* ↓ 2 -> 1.5 */
  box-shadow: 0 0 12px rgba(0,255,136,0.20);
  background: #000;
  object-fit: cover;
  margin: 0;
  display: block;
}}

.tag {{
  min-width: calc(64px * var(--scale));  /* ↓ 72 -> 64 */
  padding: calc(6px * var(--scale)) calc(8px * var(--scale)) calc(5px * var(--scale)); /* ↓ */
  border-radius: 12px;
  border: 2px solid rgba(0,255,136,0.22);
  background: rgba(0,0,0,0.78);
  box-shadow: 0 10px 20px rgba(0,0,0,0.35);
  text-align: center;
  margin: 0;
  display: block;
}}

.tag .v {{
  font-weight: 900;
  font-size: calc(11px * var(--scale));  /* ↓ 12 -> 11 */
  color: var(--green);
  line-height: 1.05;
}}

.tag .n {{
  margin-top: 1px;                       /* ↓ 2 -> 1 */
  font-weight: 800;
  font-size: calc(9px * var(--scale));   /* ↓ 10 -> 9 */
  color: rgba(255,255,255,0.82);
  white-space: nowrap;
}}

/* ========================= RIGHT CARDS ========================= */
.right {{
  display: flex;
  flex-direction: column;
  gap: calc(10px * var(--scale));
  min-height: 0;
}}

.card {{
  flex: 1;
  padding: calc(14px * var(--scale)) calc(14px * var(--scale));
  border-radius: var(--r);
  border: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: calc(6px * var(--scale));
  overflow: hidden;
}}

.card .t {{
  font-size: calc(11px * var(--scale));
  color: var(--muted);
  font-weight: 900;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}}

.card .big {{
  font-size: calc(22px * var(--scale));
  font-weight: 900;
  line-height: 1.05;
}}

.card .sub {{
  font-size: calc(12px * var(--scale));
  color: rgba(46,204,113,0.95);
  font-weight: 800;
}}

.progress {{
  width: 100%;
  height: calc(8px * var(--scale));
  border-radius: 999px;
  background: rgba(255,255,255,0.10);
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.10);
}}

.progress > div {{
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--green2), var(--green));
  box-shadow: 0 0 18px rgba(46,204,113,0.25);
}}

/* ========================= PODIUM ========================= */
.podium {{
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: calc(18px * var(--scale));
  padding: calc(12px * var(--scale)) calc(14px * var(--scale)) 0;
  border-radius: var(--r);
  border: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  box-shadow: var(--shadow);
  overflow: hidden;
}}

.podium:after {{
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: calc(10px * var(--scale));
  background: linear-gradient(90deg, rgba(0,255,136,0.10), rgba(255,255,255,0.04), rgba(0,255,136,0.10));
  opacity: 0.55;
}}

.p-col {{
  width: calc(190px * var(--scale));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  padding-bottom: calc(8px * var(--scale));
  z-index: 2;
}}

.p-ava {{
  width: calc(44px * var(--scale));
  height: calc(44px * var(--scale));
  border-radius: 999px;
  border: 3px solid rgba(255,255,255,0.92);
  object-fit: cover;
  margin-bottom: calc(10px * var(--scale));
  box-shadow: 0 10px 22px rgba(0,0,0,0.45);
}}

.p-block {{
  width: 100%;
  border-radius: 14px 14px 0 0;
  padding: calc(10px * var(--scale)) calc(10px * var(--scale));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: calc(6px * var(--scale));
  border-top: 1px solid rgba(255,255,255,0.18);
  box-shadow: inset 0 12px 20px rgba(0,0,0,0.18);
}}

.p-r {{
  font-size: calc(22px * var(--scale));
  font-weight: 900;
  line-height: 1;
}}

.p-v {{
  font-size: calc(12px * var(--scale));
  font-weight: 800;
  color: rgba(255,255,255,0.80);
}}

.gold .p-block {{
  height: calc(92px * var(--scale));
  background: linear-gradient(180deg, rgba(255,215,0,0.20), rgba(255,215,0,0.05));
  border-bottom: 6px solid var(--gold);
}}
.silver .p-block {{
  height: calc(76px * var(--scale));
  background: linear-gradient(180deg, rgba(217,217,217,0.20), rgba(217,217,217,0.05));
  border-bottom: 6px solid var(--silver);
}}
.bronze .p-block {{
  height: calc(66px * var(--scale));
  background: linear-gradient(180deg, rgba(205,127,50,0.20), rgba(205,127,50,0.05));
  border-bottom: 6px solid var(--bronze);
}}

.gold .p-r {{ color: var(--gold); text-shadow: 0 0 10px rgba(255,215,0,0.35); }}
.silver .p-r {{ color: var(--silver); text-shadow: 0 0 10px rgba(217,217,217,0.25); }}
.bronze .p-r {{ color: var(--bronze); text-shadow: 0 0 10px rgba(205,127,50,0.25); }}

.gold .p-ava {{
  border-color: var(--gold);
  width: calc(44px * var(--scale));
  height: calc(44px * var(--scale));
}}
.silver .p-ava {{ border-color: var(--silver); width: calc(44px * var(--scale)); height: calc(44px * var(--scale)); }}
.bronze .p-ava {{ border-color: var(--bronze); width: calc(44px * var(--scale)); height: calc(44px * var(--scale)); }}

div[data-testid="stVerticalBlock"] {{
  gap: 0 !important;
}}
</style>
"""
    ),
    unsafe_allow_html=True,
)

# ==============================================================================
# 5. HTML (PISTA + PÓDIO)
# ==============================================================================
lanes_html = []
for _, row in df_top.iterrows():
    pct = float(row["pct"])
    val_k = format_k(float(row["captado"]))
    first_name = row["nome"].split()[0]
    rank_num = int(row["rank"])

    z_index = 60 - rank_num
    near = "near" if pct > 88 else ""

    lanes_html.append(
        f"""
        <div class="lane" style="z-index:{z_index};">
          <div class="lane-line"></div>
          <div class="lane-dash"></div>

          <div class="racer {near}" style="left:{pct}%;">
            <img src="{row["foto"]}" class="avatar" alt="{row["nome"]}"/>
            <div class="tag">
              <div class="v">{val_k}</div>
              <div class="n">#{rank_num} {first_name}</div>
            </div>
          </div>
        </div>
        """
    )

lanes_html = "\n".join(lanes_html)


def podium_html(df3: pd.DataFrame) -> str:
    order = []
    if len(df3) >= 2:
        order.append((1, "silver"))
    if len(df3) >= 1:
        order.append((0, "gold"))
    if len(df3) >= 3:
        order.append((2, "bronze"))

    blocks = []
    for idx, cls in order:
        r = df3.iloc[idx]
        blocks.append(
            f"""
            <div class="p-col {cls}">
              <img src="{r["foto"]}" class="p-ava" alt="{r["nome"]}"/>
              <div class="p-block">
                <div class="p-r">{int(r["rank"])}º</div>
                <div class="p-v">{format_brl(float(r["captado"]))}</div>
              </div>
            </div>
            """
        )
    return "\n".join(blocks)


p_html = podium_html(df_podium)

# ==============================================================================
# 6. RENDER
# ==============================================================================
st.markdown(
    html_clean(
        f"""
<div class="dashboard">

  <div class="header">
    <div class="brand">
      <div class="brand-badge"><span>DBV</span></div>
      <div class="brand-text">
        <div class="small">DBV Race</div>
        <div class="big">Dashboard</div>
      </div>
    </div>

    <div class="title">🏁 {NOME_DA_CAMPANHA}</div>

    <div class="goal">
      <div class="label">Objetivo Mensal</div>
      <div class="value">{format_brl(META_CAMPANHA)}</div>
    </div>
  </div>

  <div class="middle">
    <div class="panel track">
      <div class="finish"></div>
      <div class="finish-label">OBJETIVO</div>
      {lanes_html}
    </div>

    <div class="right">
      <div class="card">
        <div class="t">Total Arrecadado</div>
        <div class="big" style="color: var(--green);">{format_k(total_arrecadado)}</div>
      </div>

      <div class="card">
        <div class="t">Performance Global</div>
        <div class="big">{pct_anual:.1f}%</div>
        <div class="progress" aria-label="Progresso">
          <div style="width:{clamp(pct_anual, 0, 100):.1f}%;"></div>
        </div>
      </div>

      <div class="card">
        <div class="t">Líder Atual</div>
        <div class="big" style="font-size: calc(18px * var(--scale));">{lider_nome}</div>
        <div class="sub" style="color: var(--gold);">🏆 Top 1</div>
        <div class="t" style="margin-top: 6px;">Média por assessor</div>
        <div class="big" style="font-size: calc(18px * var(--scale)); color: rgba(255,255,255,0.88);">{format_k(media_por_assessor)}</div>
      </div>
    </div>
  </div>

  <div class="podium">
    {p_html}
  </div>

</div>
"""
    ),
    unsafe_allow_html=True,
)
