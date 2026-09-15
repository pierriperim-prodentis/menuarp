# ARP — Central de Painéis

App único (multipágina) que reúne ADM, Funil, Cursos, Fábrica e Vendas
num só deploy do Streamlit, com um menu lateral pra trocar de painel.

## Antes de subir

Copie estes arquivos dos repositórios antigos pra raiz deste projeto
(mesmo nome, sem alterar nada dentro deles):

- `Dashboard_ADM.html`       ← do repo do ADM (dashadmarp)
- `Dashboard_Funil.html`     ← do repo do Funil (funilinsta)
- `Dashboard_Cursos_2026.html` ← do repo do Cursos (cursosarp)
- `relatorio.html`           ← do repo de Vendas (arpvendas)
- `fabrica_data.json`        ← do repo da Fábrica (fabricaarp) — usado só
  se a busca no jsonbin.io falhar (fallback local)

Estrutura final esperada:

```
central-paineis/
├── app.py
├── requirements.txt
├── pages/
│   ├── 1_ADM.py
│   ├── 2_Funil.py
│   ├── 3_Cursos.py
│   ├── 4_Fabrica.py
│   └── 5_Vendas.py
├── Dashboard_ADM.html
├── Dashboard_Funil.html
├── Dashboard_Cursos_2026.html
├── relatorio.html
└── fabrica_data.json
```

## Subir no GitHub + Streamlit Cloud

1. Crie um repositório novo (ex: `pierriperim-prodentis/central-paineis`)
   e suba todos os arquivos acima.
2. No Streamlit Cloud, novo app apontando pro `app.py` como main file.
3. Acesse com `https://SEU-APP.streamlit.app/?chave=prodentis2026` —
   o menu lateral leva pra cada painel sem sair da página.
4. Depois de confirmar que está tudo funcionando, pode desativar
   (ou apagar) os 5 apps antigos no Streamlit Cloud
   (dashadmarp, funilinsta, cursosarp, fabricaarp, arpvendas).

## Se algo quebrar

- Se um HTML não carregar: confira se o arquivo `.html` foi mesmo
  copiado pra raiz do repo (não pra dentro de `pages/`).
- Se a Fábrica não carregar dados: confira se as credenciais do
  jsonbin.io (`JSONBIN_BIN_ID` / `JSONBIN_MASTER_KEY`) em
  `pages/4_Fabrica.py` ainda são as mesmas do app original.
