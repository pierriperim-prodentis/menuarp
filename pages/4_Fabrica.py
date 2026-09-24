import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

MONTH_LABELS = [
    "JANEIRO 2026", "FEVEREIRO 2026", "MARÇO 2026", "ABRIL 2026", "MAIO 2026",
    "JUNHO 2026", "JULHO 2026", "AGOSTO 2026", "SETEMBRO 2026", "OUTUBRO 2026",
    "NOVEMBRO 2026", "DEZEMBRO 2026",
]
MONTH_SHORT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

ASSESSOR_LOJA = {
    "bruna": "PMW", "made": "PMW", "luana": "PMW",
    "diego": "SLZ", "francely": "SLZ", "lizia": "SLZ",
    "jarlene": "ITZ",
}

DATA_PATH = Path(__file__).parent.parent / "fabrica_data.json"

PURPLE = "#7c4dbd"
PURPLE_DARK = "#5b2f92"
BG = "#f8f4fc"


def split_value(v):
    if isinstance(v, dict):
        fat = v.get("faturadas", 0)
        dig = v.get("digitais", 0)
        tot = v.get("total", fat + dig)
        return fat, dig, tot
    v = v or 0
    return v, 0, v


def title_case(s: str) -> str:
    return " ".join(w.capitalize() for w in s.split())


JSONBIN_BIN_ID = "6a91c5cff5f4af5e294ebcf0"
JSONBIN_MASTER_KEY = "$2a$10$kDShjgaHn/S8k124l8ehU.lw9To/Dt0VHer/KXhF6XMT2CvljlxKm"


@st.cache_data(ttl=60)
def load_data():
    import requests
    try:
        res = requests.get(
            f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest",
            headers={"X-Master-Key": JSONBIN_MASTER_KEY},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()["record"]
    except Exception:
        with open(DATA_PATH, encoding="utf-8") as f:
            return json.load(f)


def fmt_money(v: float) -> str:
    s = f"{v:,.2f}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    return f"R$ {s}"


def render_table(df: pd.DataFrame) -> str:
    """Monta uma tabela HTML clara, no mesmo estilo roxo/branco do painel."""
    header_html = "".join(f"<th>{col}</th>" for col in df.columns)
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{row[col]}</td>" for col in df.columns)
        rows_html += f"<tr>{cells}</tr>"
    return f"""
    <div class="fab-table-wrap">
        <table class="fab-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """


st.markdown(
    f"""
    <style>
        section[data-testid="stMain"] {{
            background-color: {BG} !important;
        }}
        section[data-testid="stMain"] .block-container {{
            padding: 1rem 2rem 3rem 2rem !important;
            max-width: 100% !important;
        }}
        .fab-header {{
            background: linear-gradient(90deg, {PURPLE_DARK}, {PURPLE});
            border-radius: 10px;
            padding: 18px 24px;
            margin-bottom: 20px;
            color: white;
        }}
        section[data-testid="stMain"] .fab-header h1 {{
            font-size: 22px;
            margin: 0;
            color: white !important;
        }}
        section[data-testid="stMain"] .fab-header p {{
            margin: 4px 0 0 0;
            font-size: 13px;
            color: white !important;
            opacity: 0.85;
        }}
        .fab-cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }}
        .fab-card {{
            background: white;
            border-radius: 10px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}
        .fab-card .label {{
            font-size: 11px;
            font-weight: 600;
            color: #8b7a9e;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .fab-card .value {{
            font-size: 24px;
            font-weight: 700;
            color: {PURPLE_DARK};
            margin-top: 4px;
        }}
        .fab-section-title {{
            font-size: 13px;
            font-weight: 700;
            color: {PURPLE_DARK};
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin: 24px 0 10px 0;
        }}
        section[data-testid="stMain"] h1,
        section[data-testid="stMain"] h2,
        section[data-testid="stMain"] h3,
        section[data-testid="stMain"] p,
        section[data-testid="stMain"] label,
        section[data-testid="stMain"] .stMarkdown {{
            color: #2c2440;
        }}

        /* Caixa de seleção (Mês / Assessora) */
        section[data-testid="stMain"] [data-baseweb="select"] {{
            background-color: white !important;
        }}
        section[data-testid="stMain"] [data-baseweb="select"] > div,
        section[data-testid="stMain"] [data-baseweb="select"] div {{
            background-color: white !important;
            color: #2c2440 !important;
        }}
        section[data-testid="stMain"] [data-baseweb="select"] > div {{
            border: 1px solid #e0d6ee !important;
            border-radius: 8px !important;
        }}
        section[data-testid="stMain"] [data-baseweb="select"] svg {{
            fill: {PURPLE} !important;
        }}
        [data-baseweb="popover"] li {{
            background-color: white !important;
            color: #2c2440 !important;
        }}
        [data-baseweb="popover"] li:hover {{
            background-color: #f3ecfa !important;
        }}

        /* Tabelas em HTML puro */
        .fab-table-wrap {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            overflow-x: auto;
            margin-bottom: 16px;
        }}
        .fab-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        .fab-table th {{
            background: {PURPLE};
            color: white;
            text-align: left;
            padding: 10px 14px;
            font-weight: 600;
            white-space: nowrap;
        }}
        .fab-table td {{
            padding: 9px 14px;
            border-bottom: 1px solid #f0e9f8;
            color: #2c2440;
            white-space: nowrap;
        }}
        .fab-table tr:last-child td {{
            border-bottom: none;
        }}
        .fab-table tr:nth-child(even) td {{
            background: #faf7fd;
        }}

        /* ── CELULAR ─────────────────────────────────────── */
        @media (max-width: 640px) {{
            section[data-testid="stMain"] .block-container {{
                padding: 0.75rem 1rem 2rem 1rem !important;
            }}
            .fab-cards {{
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}
            .fab-card {{
                padding: 12px 14px;
            }}
            .fab-card .value {{
                font-size: 18px;
            }}
            .fab-header {{
                padding: 14px 16px;
            }}
            .fab-header h1 {{
                font-size: 17px;
            }}
            .fab-header p {{
                font-size: 11px;
            }}
            .fab-table {{
                font-size: 12px;
            }}
            .fab-table th, .fab-table td {{
                padding: 7px 10px;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

DATA = load_data()

month_totals = []
store_totals = {"PMW": 0.0, "SLZ": 0.0, "ITZ": 0.0}
grand_total = 0.0

for label in MONTH_LABELS:
    entry = DATA.get(label, {})
    totals = entry.get("totals_by_assessora", {})
    m_total = sum(split_value(v)[2] for v in totals.values())
    month_totals.append(m_total)
    for a, v in totals.items():
        loja = ASSESSOR_LOJA.get(a)
        subtotal = split_value(v)[2]
        if loja:
            store_totals[loja] += subtotal
        grand_total += subtotal

st.markdown(
    """
    <div class="fab-header">
        <h1>🏭 Painel de Vendas de Fábrica</h1>
        <p>Pródentis / ARP — Fábrica 2026</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="fab-cards">
        <div class="fab-card"><div class="label">Total no ano</div><div class="value">{fmt_money(grand_total)}</div></div>
        <div class="fab-card"><div class="label">PMW · Palmas</div><div class="value">{fmt_money(store_totals['PMW'])}</div></div>
        <div class="fab-card"><div class="label">SLZ · São Luís</div><div class="value">{fmt_money(store_totals['SLZ'])}</div></div>
        <div class="fab-card"><div class="label">ITZ · Imperatriz</div><div class="value">{fmt_money(store_totals['ITZ'])}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="fab-section-title">Total por mês</div>', unsafe_allow_html=True)
chart_df = pd.DataFrame({"Mês": MONTH_SHORT, "Total": month_totals})
chart = (
    alt.Chart(chart_df)
    .mark_bar(color=PURPLE, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X("Mês:N", sort=MONTH_SHORT, title=None),
        y=alt.Y("Total:Q", title=None),
        tooltip=[alt.Tooltip("Mês:N"), alt.Tooltip("Total:Q", format=",.2f")],
    )
    .properties(height=300, background=BG)
    .configure_axis(labelColor="#2c2440", gridColor="#e8def2")
    .configure_view(strokeWidth=0)
)
st.altair_chart(chart, use_container_width=True)

st.markdown('<div class="fab-section-title">Detalhe por assessora</div>', unsafe_allow_html=True)
months_with_data = [MONTH_LABELS[i] for i, t in enumerate(month_totals) if t > 0] or [MONTH_LABELS[0]]
sel_label = st.selectbox("Mês", months_with_data, index=len(months_with_data) - 1)

entry = DATA.get(sel_label, {})
totals = entry.get("totals_by_assessora", {})
rows = []
for a, v in sorted(totals.items(), key=lambda kv: -split_value(kv[1])[2]):
    fat, dig, tot = split_value(v)
    rows.append({
        "Assessora": title_case(a),
        "Loja": ASSESSOR_LOJA.get(a, "—"),
        "Faturadas": fmt_money(fat),
        "Digitais": fmt_money(dig),
        "Total": fmt_money(tot),
    })
detail_df = pd.DataFrame(rows)
st.markdown(render_table(detail_df), unsafe_allow_html=True)

total_fat = sum(split_value(v)[0] for v in totals.values())
total_dig = sum(split_value(v)[1] for v in totals.values())
total_geral = sum(split_value(v)[2] for v in totals.values())


def esc_money(v: float) -> str:
    return fmt_money(v).replace("$", "\\$")


st.markdown(
    f"**Total do mês:** {esc_money(total_geral)}  ·  "
    f"Faturadas: {esc_money(total_fat)}  ·  Digitais: {esc_money(total_dig)}"
)

st.markdown('<div class="fab-section-title">Detalhamento linha a linha</div>', unsafe_allow_html=True)
details = entry.get("details", [])

if details:
    det_df = pd.DataFrame(details)
    if "tipo" not in det_df.columns:
        det_df["tipo"] = ""
    det_df = det_df.rename(columns={
        "assessora": "Assessora", "cliente": "Cliente", "data": "Data",
        "valor": "Valor", "instituicao": "Instituição", "tipo": "Tipo",
        "rastreio": "Rastreio",
    })
    if "Rastreio" not in det_df.columns:
        det_df["Rastreio"] = ""
    det_df["Rastreio"] = det_df["Rastreio"].fillna("")
    det_df["Tipo"] = det_df["Tipo"].map({"faturada": "Faturada", "digital": "Digital"}).fillna(det_df["Tipo"])

    assessoras_no_mes = sorted(det_df["Assessora"].dropna().unique().tolist())
    escolha = st.selectbox("Assessora", ["Todas"] + assessoras_no_mes)
    if escolha != "Todas":
        det_df = det_df[det_df["Assessora"] == escolha]

    det_df["Valor"] = det_df["Valor"].apply(fmt_money)
    det_df = det_df[["Tipo", "Assessora", "Cliente", "Data", "Instituição", "Rastreio", "Valor"]]
    st.markdown(render_table(det_df), unsafe_allow_html=True)
else:
    st.info("Sem lançamentos detalhados para este mês.")
