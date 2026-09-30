"""
kpi_engine.py
-------------
Calcula, a partir de los CSVs en data/raw/, los KPIs estándar de H&S
(lagging + leading) por site y un Risk Priority Score explicable
(NO caja negra: fórmula transparente, defendible en entrevista).

Por qué un score explicable y no un modelo ML:
- Con ~2 años de datos por site el dataset es demasiado pequeño para
  entrenar un modelo fiable sin overfitting.
- Un score explicable con pesos justificados es exactamente lo que
  un H&S Manager necesita para *actuar*, y es defendible ante auditoría.
- Deja la puerta abierta a un módulo predictivo real (ver docs/) una
  vez haya volumen de datos suficiente.

Uso:
    python3 kpi_engine.py

Salida: data/processed/kpi_summary.csv (listo para importar en Power BI)
"""

import pandas as pd
import os

RAW = "../data/raw"
OUT = "../data/processed"

HOURS_PER_EMPLOYEE_YEAR = 2000  # aprox. 40h/semana x 50 semanas


def load_data():
    sites = pd.read_csv(f"{RAW}/sites.csv")
    incidents = pd.read_csv(f"{RAW}/incidents.csv")
    near_misses = pd.read_csv(f"{RAW}/near_misses.csv")
    safety_visits = pd.read_csv(f"{RAW}/safety_visits.csv")
    audits = pd.read_csv(f"{RAW}/audits.csv")
    training = pd.read_csv(f"{RAW}/training.csv")
    actions = pd.read_csv(f"{RAW}/corrective_actions.csv")
    return sites, incidents, near_misses, safety_visits, audits, training, actions


def normalize_0_100(series):
    """Normaliza una serie a escala 0-100 (min-max). Si no hay varianza, devuelve 50 (neutro)."""
    if series.max() == series.min():
        return pd.Series([50.0] * len(series), index=series.index)
    return 100 * (series - series.min()) / (series.max() - series.min())


def compute_kpis():
    sites, incidents, near_misses, safety_visits, audits, training, actions = load_data()

    total_hours = sites.set_index("site_id")["headcount"] * HOURS_PER_EMPLOYEE_YEAR * 2  # 2 años de datos

    kpi = sites.set_index("site_id")[["site_name", "country", "headcount", "risk_profile"]].copy()

    # ---- LAGGING: TRIR y LTIFR ----
    recordable = incidents[incidents["recordable"]].groupby("site_id").size()
    lost_time = incidents[incidents["severity"] == "Lost Time"].groupby("site_id").size()

    kpi["recordable_incidents"] = recordable.reindex(kpi.index, fill_value=0)
    kpi["lost_time_incidents"] = lost_time.reindex(kpi.index, fill_value=0)
    kpi["total_hours_2y"] = total_hours

    kpi["TRIR"] = round(kpi["recordable_incidents"] * 200_000 / kpi["total_hours_2y"], 2)
    kpi["LTIFR"] = round(kpi["lost_time_incidents"] * 1_000_000 / kpi["total_hours_2y"], 2)

    # ---- LEADING: near-miss rate, safety visits, training, audits ----
    nm_count = near_misses.groupby("site_id").size()
    kpi["near_miss_count"] = nm_count.reindex(kpi.index, fill_value=0)
    kpi["near_miss_rate_per_100emp"] = round(kpi["near_miss_count"] / kpi["headcount"] * 100, 1)

    visits_count = safety_visits.groupby("site_id").size()
    kpi["safety_visits_count"] = visits_count.reindex(kpi.index, fill_value=0)

    train = training.set_index("site_id")["completion_rate"]
    kpi["training_completion_rate"] = train.reindex(kpi.index, fill_value=0)

    audit_findings = audits.groupby("site_id")["findings_count"].sum()
    audit_major = audits.groupby("site_id")["major_findings"].sum()
    kpi["audit_findings_total"] = audit_findings.reindex(kpi.index, fill_value=0)
    kpi["audit_major_findings"] = audit_major.reindex(kpi.index, fill_value=0)

    # ---- Corrective actions: % overdue (indicador de ejecución, muy valorado por management) ----
    act_by_site = actions.groupby("site_id")["status"].value_counts().unstack(fill_value=0)
    for col in ["Open", "Closed", "Overdue"]:
        if col not in act_by_site.columns:
            act_by_site[col] = 0
    act_by_site["total_actions"] = act_by_site[["Open", "Closed", "Overdue"]].sum(axis=1)
    act_by_site["pct_overdue"] = round(act_by_site["Overdue"] / act_by_site["total_actions"] * 100, 1)
    kpi["pct_actions_overdue"] = act_by_site["pct_overdue"].reindex(kpi.index, fill_value=0)

    # ------------------------------------------------------------------
    # RISK PRIORITY SCORE (0-100, mayor = más prioritario)
    # Fórmula transparente y documentada — pesos justificados en docs/business_case.md
    #   30% severidad de incidentes (TRIR normalizado)
    #   20% acciones correctivas vencidas (pct_actions_overdue)
    #   20% hallazgos de auditoría (major findings normalizado)
    #   15% brecha de formación (100 - training_completion_rate)
    #   15% near-miss rate INVERTIDO -> más reporte de near-miss = mejor cultura,
    #       no peor riesgo (insight clave del proyecto, ver README)
    # ------------------------------------------------------------------
    trir_n = normalize_0_100(kpi["TRIR"])
    overdue_n = normalize_0_100(kpi["pct_actions_overdue"])
    audit_n = normalize_0_100(kpi["audit_major_findings"])
    training_gap_n = normalize_0_100(100 - kpi["training_completion_rate"] * 100)
    nm_rate_n = normalize_0_100(kpi["near_miss_rate_per_100emp"])
    reporting_culture_bonus = 100 - nm_rate_n  # más reporte -> resta al score de riesgo

    kpi["risk_score"] = round(
        0.30 * trir_n +
        0.20 * overdue_n +
        0.20 * audit_n +
        0.15 * training_gap_n +
        0.15 * reporting_culture_bonus,
        1,
    )

    def priority_label(score):
        if score >= 70:
            return "Critical"
        if score >= 50:
            return "High"
        if score >= 30:
            return "Medium"
        return "Low"

    kpi["priority"] = kpi["risk_score"].apply(priority_label)

    kpi = kpi.reset_index().sort_values("risk_score", ascending=False)
    return kpi


def main():
    os.makedirs(OUT, exist_ok=True)
    kpi = compute_kpis()
    kpi.to_csv(f"{OUT}/kpi_summary.csv", index=False)

    print("KPI summary calculado -> data/processed/kpi_summary.csv\n")
    cols_show = ["site_id", "site_name", "TRIR", "LTIFR", "near_miss_rate_per_100emp",
                 "pct_actions_overdue", "risk_score", "priority"]
    print(kpi[cols_show].to_string(index=False))


if __name__ == "__main__":
    main()
