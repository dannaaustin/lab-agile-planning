# Portfolio writeup — CV / LinkedIn / entrevista

Frases calibradas a lo que el proyecto realmente hace (nada que no puedas defender si
te piden que abras el código en la entrevista).

## Para CV (línea de proyecto)

> **Safety Intelligence Hub** — Sistema de analítica H&S multi-site (datos sintéticos,
> 8 plantas). Diseño de dataset con taxonomía de industria (incidentes, near-miss,
> auditorías, acciones correctivas), cálculo de KPIs estándar (TRIR, LTIFR) y modelo de
> priorización de riesgo explicable. Dashboard en Power BI. Python, pandas, DAX.

## Para LinkedIn (post o sección "Proyectos destacados")

> Construí un sistema de priorización de riesgo H&S para una empresa multi-site
> simulada: 8 plantas, ~1.500 empleados, datos de incidentes/near-miss/auditorías con
> la misma taxonomía que usan plataformas EHS enterprise. El punto interesante no es el
> dashboard — es el modelo de scoring: descubrí (en los datos sintéticos) que la planta
> con más reportes de near-miss no era la más peligrosa, era la que mejor cultura
> preventiva tenía. Diseñé el risk score para reflejar eso en vez de penalizarlo.
> Python + Power BI + DAX. Repo en GitHub.

## Para entrevista — si preguntan "¿por qué este proyecto?"

"Vi la vacante de Schneider de Transformación Digital en H&S y en vez de solo aplicar
quise entender de verdad cómo se piensa un problema de datos de seguridad — no solo
hacer un dashboard bonito. Lo que más tiempo me llevó no fue el código, fue decidir
cómo ponderar el risk score sin que fuera arbitrario, y decidir qué NO meter (dejé la
detección de EPI como módulo aparte para no perder foco)."

## Si preguntan "¿está conectado a datos reales?"

Responde con honestidad: no, es un dataset sintético diseñado con estructura realista
para poder mostrar todo el pipeline (generación → KPIs → priorización → dashboard) sin
depender de acceso a datos de ninguna empresa. Es exactamente lo que dice
`docs/business_case.md` — no lo escondas, es un punto a favor de tu criterio, no en contra.
