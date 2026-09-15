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

# fabrica_data.json fica na raiz do repo, não dentro de pages/
DATA_PATH = Path(__file__).parent.parent / "fabrica_data.json"


def split_value(v):
    """Aceita tanto o formato antigo (número único) quanto o novo
    (dict com faturadas/digitais/total) e sempre devolve os três."""
    if isinstance(v, dict):
        fat = v.get("faturadas", 0)
        dig = v.get("digitais", 0)
        tot = v.get("total", fat + dig)
        return fat, dig, tot
    v = v or 0
    return v, 0, v


def norm(s: str) -> str:
    s = str(s or "")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


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


DATA = load_data()

# ------------------------------------------------------------------
# Aggregate
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# Header
# --------------------------------------------
