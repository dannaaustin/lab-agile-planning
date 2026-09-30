# Cómo se orquestaría y auditaría esto a escala Enterprise

Este documento explica la diferencia entre "ejecutar dos scripts a mano en mi Mac"
(lo que hace este repo por defecto) y cómo se plantearía lo mismo en una empresa
real con varios sites, varios analistas y necesidad de auditoría. Útil como
narrativa de entrevista si preguntan "¿y esto cómo escalaría?".

## 1. El problema de fondo: drift de entorno

Si tú ejecutas el pipeline en tu Mac con pandas 3.0 y tu compañero lo ejecuta en su
Windows con pandas 2.1, en teoría el mismo código puede dar resultados ligeramente
distintos (cambios de comportamiento entre versiones de librería). Esto se llama
**drift de entorno** y es la razón número uno por la que "en mi máquina funciona" no
es suficiente en un equipo.

**Solución: contenerización.** Este repo incluye un `Dockerfile` que empaqueta
Python 3.12 + las dependencias exactas + el código. Con Docker instalado, tu
compañero (esté en Windows o Linux) ejecuta:

```bash
docker build -t safety-hub .
docker run --rm -v $(pwd)/data:/app/data safety-hub
```

Y obtiene exactamente el mismo resultado que tú, sin instalar Python ni configurar
nada. El sistema operativo deja de ser relevante.

## 2. El problema de los CSVs locales

Ahora mismo el pipeline escribe CSVs en tu disco local. Si tu compañero quiere ver
el dashboard, tiene que ejecutar él mismo el pipeline y generar sus propios CSVs —
funciona, pero cada uno tiene "su" versión de los datos, no hay una fuente única de
verdad.

**Solución real (siguiente paso, no implementado en este repo por alcance):**
en vez de escribir a CSV local, el paso de carga escribiría a una tabla en
**BigQuery** (que ya conoces) o una base compartida (Postgres/Supabase). Power BI
—desde cualquier máquina, con Power BI Desktop en Windows o Power BI Service desde
el navegador en Mac— se conecta a esa fuente compartida. Así todo el mundo ve
siempre los mismos datos, y de paso resuelve tu pregunta de Mac vs Windows para
Power BI específicamente: la fuente deja de ser un archivo local y pasa a ser un
endpoint en la nube al que cualquier SO se conecta igual.

Este es exactamente el patrón **ETL/ELT**: *Extract* (lo que hace `generate_data.py`,
simulando la extracción desde el sistema fuente), *Transform* (lo que hace
`kpi_engine.py`), *Load* (escribir a la capa compartida en vez de a disco local).

## 3. Orquestación: quién dispara el pipeline y cuándo

Este repo incluye `orchestration/run_pipeline.py`, que encadena los dos pasos y
escribe un manifest de auditoría. Es la versión mínima de lo que en producción
harían herramientas como:

- **Airflow** (el más usado en la industria) — defines el pipeline como un DAG
  (grafo de tareas con dependencias), con reintentos automáticos, alertas si falla
  un paso, y programación (ej. "cada noche a las 2am, tras el cierre de turno").
- **Prefect / Dagster** — alternativas más modernas, mismo concepto.
- A tu escala, **GitHub Actions con un cron trigger** sería más que suficiente y no
  requiere infraestructura adicional.

La diferencia conceptual importante: el código de negocio (`kpi_engine.py`) no
cambia al escalar. Lo que cambia es la capa que decide *cuándo* y *dónde* se
ejecuta.

## 4. CI/CD: red de seguridad para trabajo en equipo

Este repo incluye `.github/workflows/ci.yml`. Cada vez que se hace push o se abre
un Pull Request, GitHub ejecuta el pipeline completo en un entorno limpio (una
máquina virtual nueva, sin nada instalado salvo lo que el propio pipeline instala)
y valida que el output tiene la forma esperada (8 sites, columna `risk_score`
presente, valores en rango 0-100).

Si tu compañero cambia algo y rompe el pipeline, se ve **antes** de que ese cambio
llegue a `main` — no cuando alguien intenta abrir el dashboard y no entiende por qué
falla.

## 5. Auditoría y lineage (trazabilidad)

`run_pipeline.py` escribe `data/processed/run_manifest.json` en cada ejecución,
con: timestamp de inicio/fin, commit de git exacto que generó esos datos, y el
número de filas de cada tabla. Esto responde a la pregunta de auditoría más básica:
*"¿con qué versión del código y en qué momento se generó el dashboard que estoy
viendo?"*

A escala enterprise esto se llama **data lineage**, y normalmente se acompaña de:

- **Control de acceso (RBAC)** — quién puede ejecutar/modificar el pipeline (ej.
  el equipo de datos) vs quién solo puede consumir el dashboard (ej. management).
  En Power BI esto se gestiona a nivel de workspace con permisos de Azure AD.
- **Versionado de datos**, no solo de código — herramientas como DVC o
  simplemente escribir cada carga con timestamp/partición (en vez de sobrescribir)
  permiten volver atrás a "los datos tal como estaban el 3 de marzo".
- **Logs centralizados** — en vez de `print()`, en producción se usaría el módulo
  `logging` de Python enviando a un sistema centralizado (ej. Azure Monitor, dado
  que Schneider es cliente típico de stack Microsoft).

## Resumen para entrevista

Si te preguntan "¿esto cómo lo llevarías a producción?", la respuesta corta y
defendible es:

1. Contenerizar (Docker) para eliminar drift de entorno entre máquinas.
2. Mover la capa de datos de CSV local a una base compartida (BigQuery/Postgres) para
   que todos —independientemente del SO— lean la misma fuente.
3. Orquestar con un scheduler (Airflow a gran escala, GitHub Actions con cron a
   escala de equipo pequeño).
4. Añadir CI para que ningún cambio rompa el pipeline sin que se detecte.
5. Mantener un manifest/log de cada ejecución para poder auditar qué generó qué.

Y puedes decir con total honestidad: "Implementé los puntos 1, 3 (versión ligera) y
5 en el repo; documenté cómo abordaría el punto 2 porque requiere infraestructura de
BigQuery/cloud que no tenía sentido montar para un proyecto de portfolio, pero sé
exactamente qué cambiaría y por qué."
