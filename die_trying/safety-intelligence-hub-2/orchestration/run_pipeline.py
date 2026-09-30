"""
run_pipeline.py
----------------
Orquestador del pipeline completo: genera datos -> calcula KPIs -> escribe un
manifest de auditoría (cuándo se ejecutó, con qué commit de git, cuántas filas
se generaron por tabla).

Esto es el equivalente, a escala de portfolio, de lo que en producción sería un
DAG de Airflow/Prefect/Dagster. La lógica de negocio (generate_data.py,
kpi_engine.py) no cambia -- lo que cambia a escala enterprise es QUIÉN dispara
esto (un scheduler) y DÓNDE corre (un contenedor con recursos dedicados), no el
código de negocio en sí. Ver docs/enterprise_workflow.md para el contexto completo.

Uso:
    python3 orchestration/run_pipeline.py
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def run_step(description, cwd, script):
    print(f"\n>>> {description}")
    result = subprocess.run(
        [sys.executable, script], cwd=cwd, capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Fallo en paso: {description}")
    return result


def get_git_commit():
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return commit
    except Exception:
        return "no-git-repo-detected"


def row_counts(csv_dir):
    counts = {}
    for csv_file in sorted(Path(csv_dir).glob("*.csv")):
        counts[csv_file.name] = int(len(pd.read_csv(csv_file)))
    return counts


def main():
    started_at = datetime.now(timezone.utc).isoformat()

    run_step("Paso 1/2 — Generando dataset sintético", ROOT / "data", "generate_data.py")
    run_step("Paso 2/2 — Calculando KPIs y risk score", ROOT / "analysis", "kpi_engine.py")

    manifest = {
        "run_started_utc": started_at,
        "run_finished_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "raw_row_counts": row_counts(ROOT / "data" / "raw"),
        "processed_row_counts": row_counts(ROOT / "data" / "processed"),
    }

    manifest_path = ROOT / "data" / "processed" / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(f"\nPipeline completo. Manifest de auditoría escrito en: {manifest_path}")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
