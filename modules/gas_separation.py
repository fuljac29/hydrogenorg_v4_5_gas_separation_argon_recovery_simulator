
from dataclasses import dataclass
from typing import Dict

@dataclass
class GasInputs:
    h2_kg_day: float
    o2_kg_day: float
    residual_steam_kg_day: float
    reactor_safety_pct: float
    recombination_pct: float
    recoverable_heat_kwh_day: float
    argon_feed_nm3_day: float
    argon_recovery_pct: float
    argon_purification_pct: float
    argon_leakage_pct: float
    argon_cost_chf_nm3: float
    h2_sep_pct: float
    h2_purity_target_pct: float
    o2_sep_pct: float
    o2_purity_target_pct: float
    condenser_pct: float
    sep_energy_kwh_kg_h2: float
    argon_purification_energy_kwh_nm3: float
    water_condensation_energy_kwh_kg: float
    purge_fraction_pct: float
    sensor_coverage_pct: float
    purge_readiness_pct: float

def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))

def calculate_gas(i: GasInputs) -> Dict[str, float]:
    h2s = clamp(i.h2_sep_pct) / 100.0
    o2s = clamp(i.o2_sep_pct) / 100.0
    ar_rec = clamp(i.argon_recovery_pct) / 100.0
    ar_pur = clamp(i.argon_purification_pct) / 100.0
    ar_leak = max(0.0, min(1.0, i.argon_leakage_pct / 100.0))
    condenser = clamp(i.condenser_pct) / 100.0
    purge = max(0.0, min(1.0, i.purge_fraction_pct / 100.0))

    sep_h2 = i.h2_kg_day * h2s
    h2_loss = max(0.0, i.h2_kg_day - sep_h2)
    sep_o2 = i.o2_kg_day * o2s
    o2_loss = max(0.0, i.o2_kg_day - sep_o2)

    condensed = i.residual_steam_kg_day * condenser
    vapor_left = max(0.0, i.residual_steam_kg_day - condensed)

    recovered_ar = i.argon_feed_nm3_day * ar_rec * ar_pur
    ar_process_loss = max(0.0, i.argon_feed_nm3_day - recovered_ar)
    ar_leak_loss = i.argon_feed_nm3_day * ar_leak
    ar_makeup = ar_process_loss + ar_leak_loss
    ar_cost = ar_makeup * i.argon_cost_chf_nm3

    water_fraction_left = vapor_left / max(i.residual_steam_kg_day, 1.0)
    h2_purity = clamp(i.h2_purity_target_pct - i.recombination_pct * 0.035 - water_fraction_left * 1.2)
    o2_purity = clamp(i.o2_purity_target_pct - i.recombination_pct * 0.025 - water_fraction_left * 1.0)

    gas_sep_energy = i.h2_kg_day * i.sep_energy_kwh_kg_h2
    ar_energy = recovered_ar * i.argon_purification_energy_kwh_nm3
    cond_energy = condensed * i.water_condensation_energy_kwh_kg
    purge_energy = i.argon_feed_nm3_day * purge * 0.06

    gross_energy = gas_sep_energy + ar_energy + cond_energy + purge_energy
    heat_offset = min(gross_energy * 0.35, max(0.0, i.recoverable_heat_kwh_day) * 0.12)
    net_energy = max(0.0, gross_energy - heat_offset)
    kwh_per_kg_h2 = net_energy / max(sep_h2, 0.001)

    h2o2_risk = clamp(
        i.recombination_pct * 0.35
        + (100.0 - i.reactor_safety_pct) * 0.25
        + (100.0 - i.purge_readiness_pct) * 0.20
        + (100.0 - i.sensor_coverage_pct) * 0.20
    )

    argon_loop_score = clamp(
        i.argon_recovery_pct * 0.38
        + i.argon_purification_pct * 0.28
        + (100.0 - i.argon_leakage_pct * 8.0) * 0.18
        + max(0.0, 100.0 - ar_makeup / max(i.argon_feed_nm3_day, 1.0) * 100.0) * 0.16
    )

    gas_quality = clamp(
        h2_purity * 0.34
        + o2_purity * 0.22
        + i.h2_sep_pct * 0.20
        + i.o2_sep_pct * 0.14
        + i.condenser_pct * 0.10
    )

    safety_score = clamp(
        (100.0 - h2o2_risk) * 0.36
        + i.sensor_coverage_pct * 0.24
        + i.purge_readiness_pct * 0.22
        + i.reactor_safety_pct * 0.18
    )

    energy_score = max(0.0, 100.0 - min(100.0, kwh_per_kg_h2 * 15.0))
    argon_loss_score = max(0.0, 100.0 - ar_makeup / max(i.argon_feed_nm3_day, 1.0) * 100.0)

    process_score = clamp(
        argon_loop_score * 0.24
        + gas_quality * 0.24
        + safety_score * 0.22
        + energy_score * 0.12
        + h2_purity * 0.10
        + argon_loss_score * 0.08
    )

    return {
        "separated_h2_kg_day": sep_h2, "h2_loss_kg_day": h2_loss,
        "separated_o2_kg_day": sep_o2, "o2_loss_kg_day": o2_loss,
        "condensed_water_kg_day": condensed, "remaining_water_vapor_kg_day": vapor_left,
        "recovered_argon_nm3_day": recovered_ar, "argon_process_loss_nm3_day": ar_process_loss,
        "argon_leakage_loss_nm3_day": ar_leak_loss, "argon_makeup_nm3_day": ar_makeup,
        "argon_makeup_cost_chf_day": ar_cost, "h2_purity_signal_pct": h2_purity,
        "o2_purity_signal_pct": o2_purity, "separation_energy_kwh_day": gas_sep_energy,
        "argon_purification_energy_kwh_day": ar_energy, "condensation_energy_kwh_day": cond_energy,
        "purge_energy_penalty_kwh_day": purge_energy, "gross_separation_energy_kwh_day": gross_energy,
        "heat_offset_kwh_day": heat_offset, "net_separation_energy_kwh_day": net_energy,
        "kwh_per_kg_h2_sep": kwh_per_kg_h2, "h2_o2_safety_risk_pct": h2o2_risk,
        "argon_loop_score": argon_loop_score, "gas_quality_score": gas_quality,
        "safety_score": safety_score, "process_score": process_score
    }

def interpretation(r):
    if r["process_score"] >= 78 and r["argon_loop_score"] >= 75 and r["safety_score"] >= 75:
        return "Strong gas separation and Argon recovery scenario. H2/O2 separation, Argon loop recovery and safety assumptions are aligned for downstream system integration."
    if r["argon_loop_score"] < 60:
        return "Argon loop performance is limiting. Improve Argon recovery, purification efficiency or reduce leakage before scale-up interpretation."
    if r["h2_o2_safety_risk_pct"] > 55:
        return "H2/O2 separation safety risk is high. Improve purge readiness, sensors and recombination control."
    if r["gas_quality_score"] < 65:
        return "Gas quality is not yet strong enough. Improve H2/O2 separation efficiency, condensation and purity assumptions."
    if r["argon_makeup_nm3_day"] > r["recovered_argon_nm3_day"] * 0.25:
        return "Argon makeup demand is too high. The reactor should operate closer to a semi-closed Argon loop."
    return "Promising gas separation and Argon recovery scenario. Continue optimizing purity, purge logic, sensor coverage and Argon loss."
