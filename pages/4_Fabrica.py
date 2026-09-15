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


try:
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

    st.title("Painel de Vendas de Fábrica")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total no ano", fmt_money(grand_total))
    c2.metric("PMW", fmt_money(store_totals["PMW"]))
    c3.metric("SLZ", fmt_money(store_totals["SLZ"]))
    c4.metric("ITZ", fmt_money(store_totals["ITZ"]))

    chart_df = pd.DataFrame({"Mês": MONTH_SHORT, "Total": month_totals})
    chart = (
        alt.Chart(chart_df)
        .mark_bar(color="#1B2A4A")
        .encode(x=alt.X("Mês:N", sort=MONTH_SHORT), y="Total:Q")
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

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
    st.dataframe(detail_df, use_container_width=True, hide_index=True)
    st.write("✅ Checkpoint A: tabela por assessora ok")

    total_fat = sum(split_value(v)[0] for v in totals.values())
    total_dig = sum(split_value(v)[1] for v in totals.values())
    total_geral = sum(split_value(v)[2] for v in totals.values())

    def esc_money(v: float) -> str:
        return fmt_money(v).replace("$", "\\$")

    st.markdown(
        f"**Total do mês:** {esc_money(total_geral)}  ·  "
        f"Faturadas: {esc_money(total_fat)}  ·  Digitais: {esc_money(total_dig)}"
    )
    st.write("✅ Checkpoint B: linha de totais ok")

    details = entry.get("details", [])
    st.write(f"✅ Checkpoint C: {len(details)} lançamentos detalhados encontrados")

    if details:
        det_df = pd.DataFrame(details)
        st.write("✅ Checkpoint D: DataFrame de detalhes criado")
        st.write("Colunas encontradas:", list(det_df.columns))

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
        st.write("✅ Checkpoint E: colunas renomeadas ok")

        assessoras_no_mes = sorted(det_df["Assessora"].dropna().unique().tolist())
        escolha = st.selectbox("Assessora", ["Todas"] + assessoras_no_mes)
        if escolha != "Todas":
            det_df = det_df[det_df["Assessora"] == escolha]
        st.write("✅ Checkpoint F: filtro de assessora ok")

        det_df["Valor"] = det_df["Valor"].apply(fmt_money)
        det_df = det_df[["Tipo", "Assessora", "Cliente", "Data", "Instituição", "Rastreio", "Valor"]]
        st.dataframe(det_df, use_container_width=True, hide_index=True)
        st.write("✅ Checkpoint G: chegou até o fim!")
    else:
        st.info("Sem lançamentos detalhados para este mês.")

except Exception as e:
    st.error("Erro encontrado:")
    st.exception(e)
