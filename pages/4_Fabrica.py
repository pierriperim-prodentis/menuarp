import copy
import json
import unicodedata
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


def norm(s: str) -> str:
    """Tira acentos e deixa minúsculo (Madê -> made) para casar nomes."""
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def is_a_faturar(det: dict) -> bool:
    return str(det.get("rastreio", "")).strip().lower().startswith("não faturado")


def ajustar_a_faturar(data: dict) -> dict:
    """Tira do faturado (Faturadas e Total) os lançamentos 'Não Faturado'.
    Eles continuam nos detalhes e aparecem só na coluna 'A Faturar'."""
    data = copy.deepcopy(data)
    for entry_ in data.values():
        totals_ = entry_.get("totals_by_assessora", {})
        for d_ in entry_.get("details", []):
            if is_a_faturar(d_):
                k_ = norm(d_.get("assessora", ""))
                v_ = float(d_.get("valor", 0) or 0)
                t_ = totals_.get(k_)
                if isinstance(t_, dict):
                    t_["faturadas"] = round(t_.get("faturadas", 0) - v_, 2)
                    t_["total"] = round(t_.get("total", 0) - v_, 2)
    return data


@st.cache_data(ttl=60)
def load_data():
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
        # Linha inteira em vermelho quando o rastreio indica "Não Faturado"
        is_red = str(row.get("Rastreio", "")).strip().lower().startswith("não faturado")
        row_class = ' class="fab-row-red"' if is_red else ""
        rows_html += f"<tr{row_class}>{cells}</tr>"
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
        .fab-table tr.fab-row-red td {{
            color: #d32f2f !important;
            font-weight: 600;
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

DATA = ajustar_a_faturar(load_data())

month_totals = []
month_store_totals = []  # um dict {PMW, SLZ, ITZ} por mês, na ordem de MONTH_LABELS
store_totals = {"PMW": 0.0, "SLZ": 0.0, "ITZ": 0.0}
grand_total = 0.0

for label in MONTH_LABELS:
    entry = DATA.get(label, {})
    totals = entry.get("totals_by_assessora", {})
    m_total = sum(split_value(v)[2] for v in totals.values())
    month_totals.append(m_total)
    m_store = {"PMW": 0.0, "SLZ": 0.0, "ITZ": 0.0}
    for a, v in totals.items():
        loja = ASSESSOR_LOJA.get(a)
        subtotal = split_value(v)[2]
        if loja:
            store_totals[loja] += subtotal
            m_store[loja] += subtotal
        grand_total += subtotal
    month_store_totals.append(m_store)

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

st.markdown('<div class="fab-section-title">Total por mês, por loja</div>', unsafe_allow_html=True)
STORE_COLORS = {"PMW": PURPLE_DARK, "SLZ": PURPLE, "ITZ": "#c9a8e8"}
stacked_rows = []
for i, label in enumerate(MONTH_SHORT):
    for loja, cor in STORE_COLORS.items():
        stacked_rows.append({"Mês": label, "Loja": loja, "Valor": month_store_totals[i][loja]})
stacked_df = pd.DataFrame(stacked_rows)
chart = (
    alt.Chart(stacked_df)
    .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
    .encode(
        x=alt.X("Mês:N", sort=MONTH_SHORT, title=None),
        y=alt.Y("Valor:Q", title=None, stack="zero"),
        color=alt.Color(
            "Loja:N",
            scale=alt.Scale(domain=list(STORE_COLORS.keys()), range=list(STORE_COLORS.values())),
            legend=alt.Legend(title=None, orient="top"),
        ),
        order=alt.Order("Loja:N"),
        tooltip=[alt.Tooltip("Mês:N"), alt.Tooltip("Loja:N"), alt.Tooltip("Valor:Q", format=",.2f")],
    )
    .properties(height=320, background=BG)
    .configure_axis(labelColor="#2c2440", gridColor="#e8def2")
    .configure_view(strokeWidth=0)
    .configure_legend(labelColor="#2c2440", titleColor="#2c2440")
)
st.altair_chart(chart, use_container_width=True)

st.markdown('<div class="fab-section-title">Detalhamento por loja</div>', unsafe_allow_html=True)
table_rows = []
for i, label in enumerate(MONTH_SHORT):
    m_total = month_totals[i]
    row = {"Mês": label}
    for loja in ("PMW", "SLZ", "ITZ"):
        v = month_store_totals[i][loja]
        pct = f" ({v / m_total * 100:.0f}%)" if m_total else ""
        row[loja] = fmt_money(v) + pct
    row["Total"] = fmt_money(m_total)
    table_rows.append(row)
table_df = pd.DataFrame(table_rows)
st.markdown(render_table(table_df), unsafe_allow_html=True)

st.markdown('<div class="fab-section-title">Detalhe por assessora</div>', unsafe_allow_html=True)
months_with_data = [
    label for label in MONTH_LABELS
    if DATA.get(label, {}).get("details") or DATA.get(label, {}).get("totals_by_assessora")
] or [MONTH_LABELS[0]]
sel_label = st.selectbox("Mês", months_with_data, index=len(months_with_data) - 1)

entry = DATA.get(sel_label, {})
totals = entry.get("totals_by_assessora", {})
a_faturar = {}
for d_ in entry.get("details", []):
    if is_a_faturar(d_):
        k_ = norm(d_.get("assessora", ""))
        a_faturar[k_] = a_faturar.get(k_, 0.0) + float(d_.get("valor", 0) or 0)

rows = []
for a, v in sorted(totals.items(), key=lambda kv: -split_value(kv[1])[2]):
    fat, dig, tot = split_value(v)
    af = a_faturar.get(norm(a), 0.0)
    af_txt = fmt_money(af)
    if af > 0:
        af_txt = f'<span style="color:#d32f2f;font-weight:600">{af_txt}</span>'
    rows.append({
        "Assessora": title_case(a),
        "Loja": ASSESSOR_LOJA.get(a, "—"),
        "Faturadas": fmt_money(fat),
        "Digitais": fmt_money(dig),
        "Total": fmt_money(tot),
        "A Faturar": af_txt,
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
    f"Faturadas: {esc_money(total_fat)}  ·  Digitais: {esc_money(total_dig)}  ·  "
    f"A faturar: {esc_money(sum(a_faturar.values()))}"
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
    det_df["Tipo"] = det_df["Tipo"].map({"faturada": "Direta", "digital": "Digital"}).fillna(det_df["Tipo"])

    # Ordena por data (lançamentos sem data vão para o final)
    det_df["_data_ord"] = det_df["Data"].replace("", "9999-99-99")
    det_df = det_df.sort_values("_data_ord").drop(columns="_data_ord")

    assessoras_no_mes = sorted(det_df["Assessora"].dropna().unique().tolist())
    escolha = st.selectbox("Assessora", ["Todas"] + assessoras_no_mes)
    if escolha != "Todas":
        det_df = det_df[det_df["Assessora"] == escolha]

    det_df["Valor"] = det_df["Valor"].apply(fmt_money)
    det_df = det_df[["Tipo", "Assessora", "Cliente", "Data", "Instituição", "Rastreio", "Valor"]]
    st.markdown(render_table(det_df), unsafe_allow_html=True)
else:
    st.info("Sem lançamentos detalhados para este mês.")
