<p align="center"><img src="https://dodysalim.github.io/assets/project-covers/kriometrics.webp" alt="KrioMetrics" width="100%"></p>

<h1 align="center">KrioMetrics</h1>

<p align="center"><b>A catalog of 55 refrigerants turned into analysis, comparison and interactive visualization.</b></p>

<p align="center"><a href="https://refrigerant-explorer.streamlit.app/"><b>Live demo ↗</b></a></p>

<p align="center"><img src="https://img.shields.io/badge/Personal_project-75E6CE?style=for-the-badge&labelColor=0b1222" alt="Personal project"></p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite"> <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white" alt="Plotly"> <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"> <img src="https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logoColor=black" alt="Power BI">
</p>

<p align="center"><a href="https://dodysalim.github.io/"><b>🌐 Portfolio</b></a> · <a href="README.md"><b>🇪🇸 Versión en español</b></a></p>

---

## 📌 At a glance

| | |
| --- | --- |
| **🎯 Problem** | Compare properties, safety and environmental impact of refrigerant gases with explicit assumptions. |
| **🛠️ Solution** | ETL into a SQLite star schema with a layered architecture (domain, application, infrastructure, presentation). |
| **📈 Deliverables** | 5 Streamlit views (P-T calculator, comparator, refrigeration cycle, SQL console) and Power BI. |
| **🧪 Quality** | 59 automated tests; catalog stored as JSON, thermodynamic engine isolated from readers. |

## 🏗️ Architecture

```mermaid
flowchart LR
    subgraph INF[Infraestructura]
        CAT[(catalog/refrigerants.json<br/>55 gases)] --> RD[JsonCatalogReader]
        TH[ThermodynamicEngine<br/>Clausius-Clapeyron] --> RD
    end
    subgraph APP[Aplicación]
        RD --> ETL[Pipeline ETL] --> DB[(SQLite<br/>modelo estrella)]
        ETL --> REP[Reportes de calidad<br/>y sostenibilidad]
    end
    subgraph DOM[Dominio]
        ENT[Entidades y validadores]
    end
    ENT -. reglas .-> ETL
    DB --> ST[Streamlit · 5 vistas]
    DB --> PBI[Power BI]
    DB --> WEB[SPA web]
```

## 🚀 How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run dashboard.py
python -m pytest tests -q
```

## ⚖️ Scope

P-T curves are model estimates (calibrated Clausius-Clapeyron), not certified engineering tables.

---

<p align="center">
<b>Dody Dueñas Remache</b> · Data Analyst / Data Scientist · Guayaquil, Ecuador (remote LATAM)<br>
<a href="https://dodysalim.github.io/">Portfolio</a> · <a href="https://github.com/dodysalim">GitHub</a> · <a href="https://www.linkedin.com/in/dody-duenas/">LinkedIn</a> · <a href="mailto:dodydurema67@gmail.com">dodydurema67@gmail.com</a>
</p>
