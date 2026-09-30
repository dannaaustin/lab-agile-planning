# Montaje del dashboard en Power BI Desktop

## 1. Importar datos

`Obtener datos` → `Texto/CSV` → importar los 8 archivos:
- `data/raw/sites.csv`
- `data/raw/incidents.csv`
- `data/raw/near_misses.csv`
- `data/raw/safety_visits.csv`
- `data/raw/audits.csv`
- `data/raw/training.csv`
- `data/raw/corrective_actions.csv`
- `data/processed/kpi_summary.csv` (tabla principal — ya viene con KPIs y risk score calculados)

## 2. Modelo de datos

En `Vista de modelo`, crea relaciones (todas 1-a-muchos desde `sites`):

- `sites[site_id]` → `incidents[site_id]`
- `sites[site_id]` → `near_misses[site_id]`
- `sites[site_id]` → `safety_visits[site_id]`
- `sites[site_id]` → `audits[site_id]`
- `sites[site_id]` → `corrective_actions[site_id]`
- `kpi_summary` puede quedar independiente (ya está agregada) o relacionarse 1-a-1 con `sites`

## 3. Páginas del dashboard (estructura recomendada)

### Página 1 — Executive Summary
- 4 tarjetas KPI: TRIR medio, LTIFR medio, % acciones overdue, near-miss rate medio
- Mapa/tabla de sites ordenados por `risk_score` con color condicional (`priority`)
- Gráfico de barras: risk_score por site

### Página 2 — Leading vs Lagging
- Scatter plot: eje X = `TRIR` (lagging), eje Y = `near_miss_rate_per_100emp` (leading)
- Esto visualiza directamente el insight del README (reporte alto ≠ riesgo alto)
- Filtro por site

### Página 3 — Corrective Actions Tracker
- Tabla de `corrective_actions` filtrable por `status`
- % overdue por site (barras)
- Tiempo medio de cierre

### Página 4 — Site Deep Dive
- Filtro de página por `site_id`
- Todos los KPIs de ese site + tendencia de incidentes por trimestre

## 4. Formato

- Usa el tema de color por defecto de Power BI o uno corporate neutro (evita colores
  "festival"/marca personal aquí — este dashboard debe leerse como corporate serio)
- Colores de prioridad: Crítico = rojo, Alto = naranja, Medio = amarillo, Bajo = verde
  (consistente con `priority` de `kpi_summary.csv`)

## 5. Publicar

- Guarda como `.pbix`
- Si vas a compartir públicamente (portfolio/LinkedIn), exporta capturas o un vídeo corto
  en vez de publicar en Power BI Service público, para no exponer nada por error
