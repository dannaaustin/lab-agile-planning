# Safety Intelligence Hub

**Sistema de analítica H&S multi-site: de datos operacionales a decisiones priorizadas.**

Proyecto de portfolio. Simula el flujo de datos de un departamento de Health & Safety
industrial multi-planta (8 sites, ~1.500 empleados) y responde a una pregunta de negocio
concreta:

> ¿Dónde está aumentando el riesgo realmente, y qué debería priorizar el responsable de H&S esta semana?

No es un clon de ninguna plataforma comercial. La taxonomía de datos (incidentes,
near-miss, safety visits, auditorías, formación, acciones correctivas) sigue la lógica
estándar del sector EHS/ISO 45001 — es el mismo tipo de estructura que usan sistemas
enterprise (p.ej. Wolters Kluwer Enablon, con analítica embebida en Power BI), pero
construida desde cero con datos sintéticos propios.

## Por qué este proyecto (contexto)

Construido pensando en procesos de selección tipo *Schneider Electric — Prácticas
Transformación Digital H&S*, donde piden explícitamente: estructurar y analizar datos
de seguridad (KPIs, safety visits, incidentes), participar en digitalización de procesos
H&S, y nivel medio-alto de Excel/Power BI.

## Qué demuestra

| Área | Cómo se demuestra |
|---|---|
| Modelado de datos | 7 tablas relacionadas con taxonomía real de H&S (`data/generate_data.py`) |
| Cálculo de KPIs de industria | TRIR, LTIFR, near-miss rate, % acciones overdue (`analysis/kpi_engine.py`) |
| Pensamiento leading vs lagging | El near-miss rate se usa como *indicador de cultura de reporte*, no solo de riesgo — ver insight abajo |
| Risk scoring explicable | Fórmula transparente y documentada, no caja negra (justificación en `docs/business_case.md`) |
| Visualización de negocio | Dashboard Power BI (`powerbi/`) |
| Criterio de alcance | Módulo de detección de EPI vía visión artificial marcado explícitamente como **opcional/extensión**, no núcleo del proyecto — ver `ppe_module/` |

## El insight que vende el proyecto en entrevista

Con los datos generados (seed fija, reproducible), **Barcelona Plant (S01)** tiene uno
de los near-miss rates más altos (20 por cada 100 empleados) pero un risk score
*medio*, no crítico — porque ese volumo de reporte es señal de buena cultura preventiva,
no de mal desempeño. En cambio **Porto Plant (S05)** combina TRIR alto, más acciones
correctivas vencidas y menos reporte de near-miss — combinación que la sitúa como
prioridad crítica real.

Esa distinción (reporte alto ≠ sitio peligroso) es exactamente el tipo de lectura que un
H&S Manager necesita y que un dashboard ingenuo de "conteo de incidentes" no da.

## Estructura del repo

```
safety-intelligence-hub/
├── Dockerfile                 # entorno reproducible cross-platform
├── .github/workflows/ci.yml   # CI: valida el pipeline en cada push
├── data/
│   ├── generate_data.py      # genera el dataset sintético (7 CSVs)
│   └── raw/                  # CSVs generados
├── analysis/
│   └── kpi_engine.py         # calcula KPIs + risk score por site
├── orchestration/
│   └── run_pipeline.py       # orquesta el pipeline + manifest de auditoría
├── data/processed/
│   ├── kpi_summary.csv       # output listo para Power BI
│   └── run_manifest.json     # auditoría: cuándo, con qué commit, cuántas filas
├── powerbi/
│   ├── POWERBI_SETUP.md      # cómo montar el dashboard paso a paso
│   └── dax_measures.md       # medidas DAX sugeridas
├── ppe_module/                # EXTENSIÓN OPCIONAL — detección de EPI (no core)
│   └── README.md
└── docs/
    ├── business_case.md         # por qué estos pesos, por qué este scope
    ├── enterprise_workflow.md   # cómo escalaría esto a un entorno multi-usuario
    └── portfolio_writeup.md     # frases listas para CV / LinkedIn
```

## Cómo ejecutarlo

**Opción A — paso a paso:**
```bash
cd data && python3 generate_data.py       # genera data/raw/*.csv
cd ../analysis && python3 kpi_engine.py   # genera data/processed/kpi_summary.csv
```

**Opción B — pipeline orquestado (recomendado, incluye manifest de auditoría):**
```bash
python3 orchestration/run_pipeline.py
```

**Opción C — en contenedor (idéntico en Mac/Windows/Linux, sin instalar Python):**
```bash
docker build -t safety-hub .
docker run --rm -v $(pwd)/data:/app/data safety-hub
```

Luego sigue `powerbi/POWERBI_SETUP.md` para montar el dashboard.

## Orquestación, CI y auditoría

Este repo incluye, además del pipeline base:

- `orchestration/run_pipeline.py` — encadena generación de datos + cálculo de KPIs
  y escribe un manifest de auditoría (`data/processed/run_manifest.json`) con
  timestamp, commit de git y recuento de filas por tabla.
- `Dockerfile` — permite que cualquiera (Mac, Windows, Linux) ejecute el pipeline
  con resultados idénticos, sin drift de entorno.
- `.github/workflows/ci.yml` — valida automáticamente en cada push/PR que el
  pipeline sigue funcionando y que el output tiene la forma esperada.
- `docs/enterprise_workflow.md` — explica cómo escalaría esto a un entorno real
  multi-usuario (capa de datos compartida, orquestación tipo Airflow, RBAC).

## Decisiones de alcance (para que quede explícito, no accidental)

- **Risk score explicable, no Machine Learning**: con 2 años de datos por site, un
  modelo entrenado sería puro overfitting. Un score con pesos justificados es lo que
  de verdad se puede defender ante un H&S Manager o un auditor.
- **Power BI como herramienta principal**, no Tableau/Looker: es la herramienta que
  pide el mercado corporate en Barcelona y la que usa la capa analítica de plataformas
  EHS enterprise reales (Power BI embebido en Enablon Open Insights, por ejemplo).
- **Detección de EPI (YOLOv8) como módulo aparte, no núcleo**: el objetivo del proyecto
  es analítica de negocio, no computer vision. Se documenta como extensión (`ppe_module/`)
  para no diluir el foco ni inflar el scope de forma artificial.

## Roadmap (v2, si hay tiempo)

- Serie temporal real de formación (actualmente snapshot trimestral único)
- Módulo de detección de EPI funcional sobre dataset público
- Deploy del dashboard en Power BI Service con refresh automático
