"""
generate_data.py
-----------------
Genera un dataset sintético pero estructuralmente realista de Health & Safety
para una empresa industrial ficticia multi-site (8 plantas, ~1.500 trabajadores).

La taxonomía de campos está diseñada siguiendo la lógica estándar de
plataformas EHS enterprise (registro de incidentes, near-miss, safety visits,
auditorías, formación y acciones correctivas) y los KPIs habituales del
sector (TRIR, LTIFR, near-miss rate) — NO reproduce ningún dataset, esquema
de base de datos ni código propietario de ningún proveedor concreto.

Uso:
    python3 generate_data.py

Salida: 7 CSVs en data/raw/
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(42)  # seed fija -> reproducible
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)
N_DAYS = (END_DATE - START_DATE).days

# ---------------------------------------------------------------------------
# 1. SITES (8 plantas con distinto perfil de riesgo base -> genera variedad
#    real en los KPIs, no ruido uniforme)
# ---------------------------------------------------------------------------
SITES = pd.DataFrame({
    "site_id": [f"S{i:02d}" for i in range(1, 9)],
    "site_name": [
        "Barcelona Plant", "Toulouse Plant", "Milan Plant", "Lyon Warehouse",
        "Porto Plant", "Rotterdam DC", "Warsaw Plant", "Munich Assembly",
    ],
    "country": ["ES", "FR", "IT", "FR", "PT", "NL", "PL", "DE"],
    "headcount": RNG.integers(90, 320, size=8),
    "risk_profile": ["medium", "high", "medium", "low", "medium", "low", "high", "medium"],
})
# convertir risk_profile a multiplicador base para generar incidentes de forma coherente
PROFILE_MULT = {"low": 0.6, "medium": 1.0, "high": 1.6}
SITES["risk_mult"] = SITES["risk_profile"].map(PROFILE_MULT)

DEPARTMENTS = ["Production", "Logistics", "Maintenance", "Quality", "R&D", "Warehouse"]
EVENT_TYPES_INCIDENT = ["Slip/Fall", "Manual Handling", "Machine Contact", "Chemical Exposure",
                        "Electrical", "Vehicle/Forklift", "Struck By Object", "Ergonomic"]
NEAR_MISS_CATEGORIES = ["Unsafe Act", "Unsafe Condition", "PPE Non-Compliance",
                        "Near-Collision", "Housekeeping", "Equipment Malfunction"]


def random_dates(n):
    offsets = RNG.integers(0, N_DAYS, size=n)
    return [START_DATE + timedelta(days=int(o)) for o in offsets]


# ---------------------------------------------------------------------------
# 2. INCIDENTS (lagging indicators)
# ---------------------------------------------------------------------------
def generate_incidents():
    rows = []
    incident_id = 1
    for _, site in SITES.iterrows():
        # nº de incidentes esperado proporcional a headcount y risk_mult
        expected = max(2, int(site["headcount"] * site["risk_mult"] * 0.06))
        n = RNG.poisson(expected)
        for _ in range(n):
            severity = RNG.choice(
                ["Near-Miss-Level", "First Aid", "Medical Treatment", "Lost Time", "Fatality"],
                p=[0.0, 0.45, 0.32, 0.22, 0.01],
            )
            lost_time_days = 0
            if severity == "Lost Time":
                lost_time_days = int(RNG.integers(1, 30))
            elif severity == "Fatality":
                lost_time_days = 999  # marcador, se excluye de cálculos de severidad media

            rows.append({
                "incident_id": f"INC-{incident_id:05d}",
                "site_id": site["site_id"],
                "date": random_dates(1)[0].date().isoformat(),
                "department": RNG.choice(DEPARTMENTS),
                "event_type": RNG.choice(EVENT_TYPES_INCIDENT),
                "severity": severity,
                "recordable": severity in ["Medical Treatment", "Lost Time", "Fatality"],
                "lost_time_days": lost_time_days,
                "root_cause_identified": bool(RNG.random() > 0.15),
            })
            incident_id += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. NEAR MISSES (leading indicator — cultura de reporte)
# ---------------------------------------------------------------------------
def generate_near_misses():
    rows = []
    nm_id = 1
    for _, site in SITES.iterrows():
        # OJO: cultura de reporte alta != sitio peligroso. Se modela con un factor
        # de "reporting maturity" independiente del risk_mult para poder mostrar
        # el insight "más near-miss reportado != más incidentes" en el dashboard.
        reporting_maturity = RNG.uniform(0.7, 1.6)
        expected = max(5, int(site["headcount"] * reporting_maturity * 0.10))
        n = RNG.poisson(expected)
        for _ in range(n):
            report_date = random_dates(1)[0]
            days_to_close = int(RNG.integers(0, 25))
            rows.append({
                "near_miss_id": f"NM-{nm_id:05d}",
                "site_id": site["site_id"],
                "date": report_date.date().isoformat(),
                "category": RNG.choice(NEAR_MISS_CATEGORIES),
                "severity_potential": RNG.choice(["Low", "Medium", "High"], p=[0.5, 0.35, 0.15]),
                "days_to_close": days_to_close,
                "closed": bool(RNG.random() > 0.1),
            })
            nm_id += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. SAFETY VISITS (leading indicator — actividad preventiva)
# ---------------------------------------------------------------------------
def generate_safety_visits():
    rows = []
    visit_id = 1
    for _, site in SITES.iterrows():
        n = RNG.poisson(40)  # ~40 visitas/site en el periodo
        for _ in range(n):
            rows.append({
                "visit_id": f"SV-{visit_id:05d}",
                "site_id": site["site_id"],
                "date": random_dates(1)[0].date().isoformat(),
                "observations_raised": int(RNG.integers(0, 6)),
                "positive_observations": int(RNG.integers(0, 8)),
            })
            visit_id += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. AUDITS (auditorías ISO 45001 / internas)
# ---------------------------------------------------------------------------
def generate_audits():
    rows = []
    audit_id = 1
    for _, site in SITES.iterrows():
        n = RNG.integers(3, 7)  # auditorías por site en 2 años
        for _ in range(n):
            findings = int(RNG.integers(0, 12))
            rows.append({
                "audit_id": f"AUD-{audit_id:05d}",
                "site_id": site["site_id"],
                "date": random_dates(1)[0].date().isoformat(),
                "type": RNG.choice(["Internal", "Corporate", "ISO 45001 External"]),
                "findings_count": findings,
                "major_findings": int(RNG.binomial(findings, 0.2)) if findings else 0,
                "score_pct": round(float(RNG.uniform(65, 98)), 1),
            })
            audit_id += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 6. TRAINING (formación H&S)
# ---------------------------------------------------------------------------
def generate_training():
    rows = []
    for _, site in SITES.iterrows():
        completion_rate = round(float(RNG.uniform(0.68, 0.99)), 3)
        rows.append({
            "site_id": site["site_id"],
            "quarter": "2025-Q4",  # snapshot simplificado, ampliable a serie temporal
            "employees_required": int(site["headcount"]),
            "employees_completed": int(site["headcount"] * completion_rate),
            "completion_rate": completion_rate,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 7. CORRECTIVE ACTIONS (cierre del loop incidentes/near-miss -> acción)
# ---------------------------------------------------------------------------
def generate_corrective_actions(incidents_df, near_misses_df):
    rows = []
    action_id = 1
    today = END_DATE

    source_events = (
        [(r.incident_id, r.site_id, r.date, "Incident") for r in incidents_df.itertuples()]
        + [(r.near_miss_id, r.site_id, r.date, "Near-Miss") for r in near_misses_df.itertuples()
           if RNG.random() > 0.4]  # no todos los near-miss generan acción formal
    )

    for source_id, site_id, event_date, source_type in source_events:
        due_date = pd.to_datetime(event_date) + timedelta(days=int(RNG.integers(7, 45)))
        is_closed = bool(RNG.random() > 0.28)
        closed_date = None
        if is_closed:
            closed_date = due_date + timedelta(days=int(RNG.integers(-10, 20)))
            closed_date = closed_date.date().isoformat()
        overdue = (not is_closed) and (due_date.date() < today.date())

        rows.append({
            "action_id": f"ACT-{action_id:05d}",
            "source_id": source_id,
            "source_type": source_type,
            "site_id": site_id,
            "priority": RNG.choice(["Low", "Medium", "High"], p=[0.3, 0.5, 0.2]),
            "due_date": due_date.date().isoformat(),
            "status": "Closed" if is_closed else ("Overdue" if overdue else "Open"),
            "closed_date": closed_date,
        })
        action_id += 1
    return pd.DataFrame(rows)


def main():
    out_dir = "raw"
    import os
    os.makedirs(out_dir, exist_ok=True)

    sites = SITES.drop(columns=["risk_mult"])
    incidents = generate_incidents()
    near_misses = generate_near_misses()
    safety_visits = generate_safety_visits()
    audits = generate_audits()
    training = generate_training()
    corrective_actions = generate_corrective_actions(incidents, near_misses)

    sites.to_csv(f"{out_dir}/sites.csv", index=False)
    incidents.to_csv(f"{out_dir}/incidents.csv", index=False)
    near_misses.to_csv(f"{out_dir}/near_misses.csv", index=False)
    safety_visits.to_csv(f"{out_dir}/safety_visits.csv", index=False)
    audits.to_csv(f"{out_dir}/audits.csv", index=False)
    training.to_csv(f"{out_dir}/training.csv", index=False)
    corrective_actions.to_csv(f"{out_dir}/corrective_actions.csv", index=False)

    print("Dataset generado en data/raw/:")
    for name, df in [("sites", sites), ("incidents", incidents), ("near_misses", near_misses),
                      ("safety_visits", safety_visits), ("audits", audits),
                      ("training", training), ("corrective_actions", corrective_actions)]:
        print(f"  {name:20s} {len(df):5d} filas")


if __name__ == "__main__":
    main()
