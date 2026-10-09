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

from datetime import date, datetime
from zoneinfo import ZoneInfo

# ------------------------------------------------------------------
# Estilos da navegação (chips de período, botões de visão, alerta)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
        .fab-ctl-label {
            font-size: 11px; font-weight: 700; letter-spacing: .08em;
            color: #8b7a9e; text-transform: uppercase; margin: 6px 0 4px 0;
        }
        .fab-card .sub { font-size: 12px; color: #8b7a9e; margin-top: 2px; }
        .fab-badge {
            background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35);
            border-radius: 999px; padding: 5px 14px; font-size: 12px; font-weight: 600;
            color: white; white-space: nowrap;
        }
        .fab-alert {
            background: #fdecea; border: 1px solid #f4c7c3; border-radius: 12px;
            padding: 14px 18px; display: flex; flex-wrap: wrap; gap: 8px 28px;
            align-items: center; margin: 14px 0 6px 0;
        }
        .fab-alert .l { font-size: 11px; font-weight: 700; letter-spacing: .05em; color: #b3261e; }
        .fab-alert .v { font-size: 24px; font-weight: 700; color: #b3261e; }
        .fab-alert .t { font-size: 13px; color: #5c2a27 !important; line-height: 1.5; flex: 1 1 300px; }
        .fab-bar {
            display: inline-block; width: 90px; height: 8px; background: #f1eaf8;
            border-radius: 99px; vertical-align: middle; overflow: hidden;
        }
        .fab-bar > span { display: block; height: 100%; background: #7c4dbd; border-radius: 99px; }

        /* Botão "Ver pedidos pendentes" */
        .st-key-ir_pendentes button {
            background: #b3261e; border: 0; border-radius: 8px; min-height: 40px;
        }
        .st-key-ir_pendentes button * { color: #fff !important; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Radios horizontais viram chips / botões (funciona no Streamlit novo e no antigo)
def _css_pills(key: str, radius: str, pad: str, size: str, weight: str) -> str:
    k = f".st-key-{key}"
    opt = f'{k} label[data-testid="stRadioOption"], {k} label[data-baseweb="radio"]'
    sel = f'{k} label[data-testid="stRadioOption"]:has(input:checked), {k} label[data-baseweb="radio"]:has(input:checked)'
    txt = f'{k} label[data-testid="stRadioOption"] *, {k} label[data-baseweb="radio"] *'
    txt_sel = f'{k} label[data-testid="stRadioOption"]:has(input:checked) *, {k} label[data-baseweb="radio"]:has(input:checked) *'
    circ = f'{k} label[data-testid="stRadioOption"] > div > div:first-child, {k} label[data-baseweb="radio"] > div:first-child'
    grp = f'{k} [data-testid="stRadioGroup"], {k} [role="radiogroup"]'
    return (
        f"{grp} {{ gap: 8px; flex-wrap: wrap; }}"
        f"{opt} {{ background: #fff; border: 1px solid #d9c9ee; border-radius: {radius}; padding: {pad};"
        f" margin: 0; cursor: pointer; min-height: 40px; align-items: center; }}"
        f"{circ} {{ display: none !important; }}"
        f"{txt} {{ color: #5b2f92 !important; font-weight: {weight}; font-size: {size}; margin: 0; }}"
        f"{sel} {{ background: #5b2f92; border-color: #5b2f92; }}"
        f"{txt_sel} {{ color: #fff !important; }}"
    )


st.markdown(
    "<style>"
    + _css_pills("periodo", "999px", "8px 16px", "13px", "600")
    + _css_pills("lanc_status", "999px", "8px 16px", "13px", "600")
    + _css_pills("visao", "10px", "9px 22px", "14px", "700")
    + "</style>",
    unsafe_allow_html=True,
)

DATA = ajustar_a_faturar(load_data())
HOJE = datetime.now(ZoneInfo("America/Sao_Paulo")).date()


NOME_EXIBICAO = {"made": "Madê"}


def nome_ass(a: str) -> str:
    return NOME_EXIBICAO.get(a, title_case(a))


def esc_money(v: float) -> str:
    return fmt_money(v).replace("$", "\\$")


def fmt_data(iso: str) -> str:
    s = str(iso or "")
    return f"{s[8:10]}/{s[5:7]}/{s[0:4]}" if len(s) >= 10 and s[4] == "-" else s


def month_has_data(label: str) -> bool:
    e = DATA.get(label, {})
    return bool(e.get("details")) or any(
        split_value(v)[2] for v in e.get("totals_by_assessora", {}).values()
    )


LAST_IDX = max([i for i, l in enumerate(MONTH_LABELS) if month_has_data(l)] or [0])
MONTH_NAME = [l.split()[0].capitalize() for l in MONTH_LABELS]

# Totais por mês (assessora e loja) — já sem os pedidos "a faturar"
month_totals = []
month_store_totals = []
for label in MONTH_LABELS:
    totals = DATA.get(label, {}).get("totals_by_assessora", {})
    month_totals.append(sum(split_value(v)[2] for v in totals.values()))
    m_store = {"PMW": 0.0, "SLZ": 0.0, "ITZ": 0.0}
    for a, v in totals.items():
        loja = ASSESSOR_LOJA.get(a)
        if loja:
            m_store[loja] += split_value(v)[2]
    month_store_totals.append(m_store)

# Pendências (todas, de qualquer mês)
pendentes = [
    d_ for label in MONTH_LABELS for d_ in DATA.get(label, {}).get("details", []) if is_a_faturar(d_)
]
pend_total = sum(float(d_.get("valor", 0) or 0) for d_ in pendentes)
pend_oldest = None
for d_ in pendentes:
    if d_.get("data") and (pend_oldest is None or d_["data"] < pend_oldest["data"]):
        pend_oldest = d_

# Selo "Dados até"
ult_datas = [d_["data"] for d_ in DATA.get(MONTH_LABELS[LAST_IDX], {}).get("details", []) if d_.get("data")]
badge = ""
if ult_datas:
    mx = max(ult_datas)
    badge = f"Dados até {mx[8:10]}/{mx[5:7]}/{mx[2:4]}"
    if HOJE.year == 2026 and HOJE.month - 1 == LAST_IDX:
        badge += f" · {MONTH_NAME[LAST_IDX]} parcial"

# ------------------------------------------------------------------
# Cabeçalho
# ------------------------------------------------------------------
st.markdown(
    f"""
    <div class="fab-header" style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px">
        <div>
            <h1>🏭 Painel de Vendas de Fábrica</h1>
            <p>Pródentis / ARP — Fábrica</p>
        </div>
        <span class="fab-badge">{badge}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Período (chips) + mês específico
# ------------------------------------------------------------------
PERIODOS = ["Último mês", "Trimestre", "Semestre", "Acumulado do ano"]
MESES_COM_DADOS = [MONTH_LABELS[i] for i in range(len(MONTH_LABELS)) if month_has_data(MONTH_LABELS[i])]
MES_OPCOES = ["Todos"] + [l.title() for l in MESES_COM_DADOS]

st.session_state.setdefault("periodo", "Acumulado do ano")
st.session_state.setdefault("mes_sel", "Todos")
st.session_state.setdefault("visao", "Visão geral")
st.session_state.setdefault("lanc_status", "Todas")

c_per, c_mes = st.columns([3, 1])
with c_per:
    st.markdown('<div class="fab-ctl-label">Período</div>', unsafe_allow_html=True)
    st.radio("Período", PERIODOS, horizontal=True, key="periodo", label_visibility="collapsed")
with c_mes:
    st.markdown('<div class="fab-ctl-label">Mês específico</div>', unsafe_allow_html=True)
    st.selectbox("Mês específico", MES_OPCOES, key="mes_sel", label_visibility="collapsed")

if st.session_state["mes_sel"] != "Todos":
    idx_sel = [l.title() for l in MONTH_LABELS].index(st.session_state["mes_sel"])
    ini = fim = idx_sel
    periodo_txt = f"{MONTH_NAME[idx_sel]} 2026"
else:
    fim = LAST_IDX
    ini = {
        "Último mês": LAST_IDX,
        "Trimestre": max(0, LAST_IDX - 2),
        "Semestre": max(0, LAST_IDX - 5),
        "Acumulado do ano": 0,
    }[st.session_state["periodo"]]
    periodo_txt = MONTH_NAME[ini] if ini == fim else f"{MONTH_NAME[ini]} a {MONTH_NAME[fim]}"
RANGE = range(ini, fim + 1)

# ------------------------------------------------------------------
# Alerta fixo: A Faturar
# ------------------------------------------------------------------
if pendentes:
    if pend_oldest:
        dias = (HOJE - date.fromisoformat(pend_oldest["data"])).days
        quando = "hoje" if dias <= 0 else (f"há {dias} dia" + ("s" if dias > 1 else ""))
        mais_antigo = (
            f"Mais antigo: <strong>{pend_oldest.get('cliente', '')}</strong> · "
            f"{fmt_money(float(pend_oldest.get('valor', 0) or 0))} · "
            f"pedido de {fmt_data(pend_oldest['data'])[:5]} ({quando})"
        )
    else:
        mais_antigo = ""
    st.markdown(
        f"""
        <div class="fab-alert">
            <div><div class="l">A FATURAR</div><div class="v">{fmt_money(pend_total)}</div></div>
            <div class="t">{len(pendentes)} pedido(s) sem NF e sem rastreio, fora dos totais do painel até o faturamento.<br>{mais_antigo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def _ir_pendentes():
        st.session_state["visao"] = "Lançamentos"
        st.session_state["lanc_status"] = "A faturar"
        st.session_state["mes_sel"] = "Todos"
        st.session_state["periodo"] = "Acumulado do ano"

    st.button("Ver pedidos pendentes", key="ir_pendentes", on_click=_ir_pendentes)

# ------------------------------------------------------------------
# Visões
# ------------------------------------------------------------------
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
st.radio(
    "Visão", ["Visão geral", "Assessoras", "Lançamentos"],
    horizontal=True, key="visao", label_visibility="collapsed",
)
visao = st.session_state["visao"]

# Agregados do período
sums = {}
af_by_ass = {}
for i in RANGE:
    entry_i = DATA.get(MONTH_LABELS[i], {})
    for a, v in entry_i.get("totals_by_assessora", {}).items():
        f_, d_, t_ = split_value(v)
        s_ = sums.setdefault(a, [0.0, 0.0, 0.0])
        s_[0] += f_
        s_[1] += d_
        s_[2] += t_
    for det in entry_i.get("details", []):
        if is_a_faturar(det):
            k_ = norm(det.get("assessora", ""))
            af_by_ass[k_] = af_by_ass.get(k_, 0.0) + float(det.get("valor", 0) or 0)

total_p = sum(s_[2] for s_ in sums.values())
store_p = {"PMW": 0.0, "SLZ": 0.0, "ITZ": 0.0}
for a, s_ in sums.items():
    if ASSESSOR_LOJA.get(a):
        store_p[ASSESSOR_LOJA[a]] += s_[2]


def pct_txt(v: float) -> str:
    return f"{v / total_p * 100:.0f}% do total" if total_p else ""


# ---------------------------- VISÃO GERAL -------------------------
if visao == "Visão geral":
    st.markdown(
        f"""
        <div class="fab-cards" style="margin-top:14px">
            <div class="fab-card"><div class="label">Total no período</div><div class="value">{fmt_money(total_p)}</div><div class="sub">{periodo_txt}</div></div>
            <div class="fab-card"><div class="label">PMW · Palmas</div><div class="value">{fmt_money(store_p['PMW'])}</div><div class="sub">{pct_txt(store_p['PMW'])}</div></div>
            <div class="fab-card"><div class="label">SLZ · São Luís</div><div class="value">{fmt_money(store_p['SLZ'])}</div><div class="sub">{pct_txt(store_p['SLZ'])}</div></div>
            <div class="fab-card"><div class="label">ITZ · Imperatriz</div><div class="value">{fmt_money(store_p['ITZ'])}</div><div class="sub">{pct_txt(store_p['ITZ'])}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="fab-section-title">Total por mês, por loja</div>', unsafe_allow_html=True)
    STORE_COLORS = {"PMW": PURPLE_DARK, "SLZ": PURPLE, "ITZ": "#c9a8e8"}
    stacked_rows = []
    for i in range(LAST_IDX + 1):
        for loja in STORE_COLORS:
            stacked_rows.append({
                "Mês": MONTH_SHORT[i], "Loja": loja,
                "Valor": month_store_totals[i][loja], "Ativo": i in RANGE,
            })
    stacked_df = pd.DataFrame(stacked_rows)
    chart = (
        alt.Chart(stacked_df)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("Mês:N", sort=MONTH_SHORT[: LAST_IDX + 1], title=None),
            y=alt.Y("Valor:Q", title=None, stack="zero"),
            color=alt.Color(
                "Loja:N",
                scale=alt.Scale(domain=list(STORE_COLORS.keys()), range=list(STORE_COLORS.values())),
                legend=alt.Legend(title=None, orient="top"),
            ),
            opacity=alt.condition(alt.datum.Ativo, alt.value(1), alt.value(0.3)),
            order=alt.Order("Loja:N"),
            tooltip=[alt.Tooltip("Mês:N"), alt.Tooltip("Loja:N"), alt.Tooltip("Valor:Q", format=",.2f")],
        )
        .properties(height=320, background=BG)
        .configure_axis(labelColor="#2c2440", gridColor="#e8def2")
        .configure_view(strokeWidth=0)
        .configure_legend(labelColor="#2c2440", titleColor="#2c2440")
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption("Meses fora do período escolhido ficam esmaecidos. Os pedidos \"a faturar\" não entram nos totais.")

    with st.expander("Detalhamento por loja (tabela)"):
        table_rows = []
        for i in range(LAST_IDX + 1):
            m_total = month_totals[i]
            row = {"Mês": MONTH_SHORT[i]}
            for loja in ("PMW", "SLZ", "ITZ"):
                v = month_store_totals[i][loja]
                pct = f" ({v / m_total * 100:.0f}%)" if m_total else ""
                row[loja] = fmt_money(v) + pct
            row["Total"] = fmt_money(m_total)
            table_rows.append(row)
        st.markdown(render_table(pd.DataFrame(table_rows)), unsafe_allow_html=True)

# ---------------------------- ASSESSORAS --------------------------
elif visao == "Assessoras":
    st.markdown(
        f'<div class="fab-section-title">Ranking de assessoras · {periodo_txt}</div>',
        unsafe_allow_html=True,
    )
    ranking = sorted(
        [(a, s_) for a, s_ in sums.items() if s_[2] > 0 or af_by_ass.get(norm(a), 0) > 0],
        key=lambda kv: -kv[1][2],
    )
    max_v = ranking[0][1][2] if ranking and ranking[0][1][2] > 0 else 1
    rows = []
    for pos, (a, (fat, dig, tot)) in enumerate(ranking, start=1):
        af = af_by_ass.get(norm(a), 0.0)
        af_txt = fmt_money(af)
        if af > 0:
            af_txt = f'<span style="color:#d32f2f;font-weight:600">{af_txt}</span>'
        barra = (
            f'<span class="fab-bar"><span style="width:{max(2, round(tot / max_v * 100))}%"></span></span>'
        )
        rows.append({
            "#": pos,
            "Assessora": nome_ass(a),
            "Loja": ASSESSOR_LOJA.get(a, "—"),
            "Participação": barra,
            "Faturadas": fmt_money(fat),
            "Digitais": fmt_money(dig),
            "Total": fmt_money(tot),
            "% do período": f"{tot / total_p * 100:.0f}%" if total_p else "—",
            "A Faturar": af_txt,
        })
    if rows:
        st.markdown(render_table(pd.DataFrame(rows)), unsafe_allow_html=True)
    else:
        st.info("Sem vendas no período escolhido.")

    total_fat = sum(s_[0] for s_ in sums.values())
    total_dig = sum(s_[1] for s_ in sums.values())
    st.markdown(
        f"**Total do período:** {esc_money(total_p)}  ·  "
        f"Faturadas: {esc_money(total_fat)}  ·  Digitais: {esc_money(total_dig)}  ·  "
        f"A faturar: {esc_money(sum(af_by_ass.values()))}"
    )

# ---------------------------- LANÇAMENTOS -------------------------
else:
    st.markdown(
        f'<div class="fab-section-title">Lançamentos · {periodo_txt}</div>',
        unsafe_allow_html=True,
    )
    details = [d_ for i in RANGE for d_ in DATA.get(MONTH_LABELS[i], {}).get("details", [])]

    if details:
        det_df = pd.DataFrame(details)
        for col in ("tipo", "rastreio", "data", "instituicao"):
            if col not in det_df.columns:
                det_df[col] = ""
        det_df["rastreio"] = det_df["rastreio"].fillna("")
        det_df["data"] = det_df["data"].fillna("")
        det_df["tipo"] = det_df["tipo"].map({"faturada": "Direta", "digital": "Digital"}).fillna(det_df["tipo"])
        det_df["_pend"] = det_df["rastreio"].str.strip().str.lower().str.startswith("não faturado")
        det_df["_ord"] = det_df["data"].replace("", "9999-99-99")
        det_df = det_df.sort_values("_ord", kind="stable")

        f1, f2 = st.columns([2, 1])
        with f1:
            st.radio(
                "Situação", ["Todas", "A faturar", "Faturadas"],
                horizontal=True, key="lanc_status", label_visibility="collapsed",
            )
        with f2:
            assessoras_no_periodo = sorted(det_df["assessora"].dropna().unique().tolist())
            escolha = st.selectbox(
                "Assessora", ["Todas"] + assessoras_no_periodo, label_visibility="collapsed"
            )

        status = st.session_state["lanc_status"]
        if status == "A faturar":
            det_df = det_df[det_df["_pend"]]
        elif status == "Faturadas":
            det_df = det_df[~det_df["_pend"]]
        if escolha != "Todas":
            det_df = det_df[det_df["assessora"] == escolha]

        if det_df.empty:
            st.info("Nenhum lançamento com esses filtros.")
        else:
            det_df = det_df.rename(columns={
                "assessora": "Assessora", "cliente": "Cliente", "data": "Data",
                "valor": "Valor", "instituicao": "Instituição", "tipo": "Tipo",
                "rastreio": "Rastreio",
            })
            det_df["Data"] = det_df["Data"].apply(fmt_data)
            det_df["Valor"] = det_df["Valor"].apply(fmt_money)
            det_df = det_df[["Tipo", "Assessora", "Cliente", "Data", "Instituição", "Rastreio", "Valor"]]
            st.markdown(render_table(det_df), unsafe_allow_html=True)
            st.caption("Linhas em vermelho: ainda sem NF e sem rastreio.")
    else:
        st.info("Sem lançamentos detalhados para este período.")
