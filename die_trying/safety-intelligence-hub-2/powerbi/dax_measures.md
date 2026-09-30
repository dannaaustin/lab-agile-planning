# Medidas DAX sugeridas

Estas se pueden calcular ya en Python (`kpi_engine.py`) — para el dashboard base usa
directamente las columnas de `kpi_summary.csv`. Estas medidas DAX son para cuando
quieras mostrar que también sabes trabajar la capa de modelado dentro de Power BI
(útil si en la entrevista te preguntan "¿y si tuvieras que hacerlo en vivo?").

```dax
Avg TRIR =
AVERAGE(kpi_summary[TRIR])

Avg LTIFR =
AVERAGE(kpi_summary[LTIFR])

Total Recordable Incidents =
SUM(kpi_summary[recordable_incidents])

% Actions Overdue (Global) =
DIVIDE(
    SUMX(corrective_actions, IF(corrective_actions[status] = "Overdue", 1, 0)),
    COUNTROWS(corrective_actions)
)

Sites at Critical Priority =
CALCULATE(
    COUNTROWS(kpi_summary),
    kpi_summary[priority] = "Critical"
)

Near-Miss to Incident Ratio =
DIVIDE(
    SUM(kpi_summary[near_miss_count]),
    SUM(kpi_summary[recordable_incidents])
)
-- Ratio alto = buena cultura de reporte preventivo (más near-miss reportados
-- por cada incidente real). Es un indicador de madurez, no de peligro.
```
