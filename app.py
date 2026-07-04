
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.gas_separation import GasInputs, calculate_gas, interpretation

st.set_page_config(page_title="HydrogenOrg V4.5 Gas Separation & Argon Recovery Simulator", page_icon="🧪", layout="wide")
st.title("HydrogenOrg V4.5 — Gas Separation & Argon Recovery Simulator")
st.subheader("Integrated Engineering Phase — Module 5")
st.info("This module estimates H₂/O₂ separation, residual water condensation, Argon recovery, Argon makeup demand, separation energy and safety purge readiness.")

with st.expander("Engineering architecture", expanded=True):
    st.markdown("""
**V4.4 reactor outlet → H₂/O₂ separation → water condensation → Argon drying/purification → Argon recirculation → purge/safety loop**

The goal is a semi-closed Argon loop, not disposable Argon use.
""")

with st.sidebar:
    st.header("V4.5 Scenario Builder")
    st.subheader("Input from V4.4")
    h2 = st.slider("H₂ from V4.4 (kg/day)", 0.0, 5000.0, 184.9, 0.5)
    o2 = st.slider("O₂ from V4.4 (kg/day)", 0.0, 40000.0, 1478.8, 1.0)
    residual = st.slider("Residual steam / water from V4.4 (kg/day)", 0.0, 50000.0, 1374.0, 10.0)
    reactor_safety = st.slider("Reactor safety score from V4.4 (%)", 0, 100, 81, 1)
    recomb = st.slider("Recombination signal from V4.4 (%)", 0, 100, 16, 1)
    recoverable_heat = st.slider("Recoverable reactor heat from V4.4 (kWh/day)", 0, 50000, 4300, 100)

    st.subheader("Argon loop")
    argon_feed = st.slider("Argon feed / circulating volume (Nm³/day)", 10.0, 100000.0, 2160.0, 10.0)
    argon_recovery = st.slider("Argon recovery efficiency (%)", 0, 99, 88, 1)
    argon_purification = st.slider("Argon purification efficiency (%)", 0, 99, 92, 1)
    argon_leakage = st.slider("Argon leakage (%)", 0.0, 10.0, 1.2, 0.1)
    argon_cost = st.slider("Argon makeup cost (CHF/Nm³)", 0.01, 5.00, 0.65, 0.01)

    st.subheader("Gas separation")
    h2_sep = st.slider("H₂ separation efficiency (%)", 40, 99, 88, 1)
    h2_purity = st.slider("H₂ purity target signal (%)", 80.0, 99.99, 98.5, 0.1)
    o2_sep = st.slider("O₂ separation efficiency (%)", 40, 99, 84, 1)
    o2_purity = st.slider("O₂ purity target signal (%)", 80.0, 99.9, 96.0, 0.1)
    condenser = st.slider("Residual water condenser efficiency (%)", 40, 99, 88, 1)

    st.subheader("Energy and safety")
    sep_energy = st.slider("Gas separation energy (kWh/kg H₂)", 0.05, 20.0, 2.8, 0.05)
    ar_energy = st.slider("Argon purification energy (kWh/Nm³)", 0.001, 1.0, 0.035, 0.001)
    cond_energy = st.slider("Water condensation energy (kWh/kg)", 0.000, 0.500, 0.035, 0.005)
    purge_fraction = st.slider("Safety purge fraction (%)", 0.0, 20.0, 3.0, 0.1)
    sensors = st.slider("Gas sensor coverage (%)", 0, 100, 76, 1)
    purge_readiness = st.slider("Safety purge readiness (%)", 0, 100, 78, 1)

inputs = GasInputs(h2, o2, residual, reactor_safety, recomb, recoverable_heat, argon_feed, argon_recovery, argon_purification, argon_leakage, argon_cost, h2_sep, h2_purity, o2_sep, o2_purity, condenser, sep_energy, ar_energy, cond_energy, purge_fraction, sensors, purge_readiness)
r = calculate_gas(inputs)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Separated H₂", f"{r['separated_h2_kg_day']:.1f} kg/day", f"{r['h2_purity_signal_pct']:.1f}% purity signal")
c2.metric("Separated O₂", f"{r['separated_o2_kg_day']:.1f} kg/day", f"{r['o2_purity_signal_pct']:.1f}% purity signal")
c3.metric("Recovered Argon", f"{r['recovered_argon_nm3_day']:.0f} Nm³/day", f"{r['argon_loop_score']:.0f}/100 loop")
c4.metric("Argon makeup", f"{r['argon_makeup_nm3_day']:.1f} Nm³/day", f"CHF {r['argon_makeup_cost_chf_day']:.0f}/day")
c5.metric("Process score", f"{r['process_score']:.0f}/100", "gas loop signal")

c6, c7, c8, c9 = st.columns(4)
c6.metric("Net sep. energy", f"{r['net_separation_energy_kwh_day']:.0f} kWh/day", f"{r['kwh_per_kg_h2_sep']:.2f} kWh/kg H₂")
c7.metric("Gas quality", f"{r['gas_quality_score']:.0f}/100", "H₂/O₂ purity")
c8.metric("Safety score", f"{r['safety_score']:.0f}/100", "purge + sensors")
c9.metric("H₂/O₂ risk", f"{r['h2_o2_safety_risk_pct']:.0f}%", "separation risk")

tabs = st.tabs(["Overview", "H₂/O₂ separation", "Argon recovery", "Water condensation", "Energy & cost", "Safety model", "Downstream export", "Validation roadmap"])

with tabs[0]:
    st.header("Gas separation and semi-closed Argon loop")
    st.markdown("The reactor should operate as a **semi-closed Argon loop**: separate H₂/O₂, condense H₂O, dry/purify Argon, recirculate Argon, and purge only when needed.")
    st.success(interpretation(r))

with tabs[1]:
    st.header("H₂/O₂ separation")
    st.dataframe(pd.DataFrame({
        "Metric": ["H₂ from reactor", "Separated H₂", "H₂ loss", "H₂ purity signal", "O₂ from reactor", "Separated O₂", "O₂ loss", "O₂ purity signal"],
        "Value": [f"{h2:.1f} kg/day", f"{r['separated_h2_kg_day']:.1f} kg/day", f"{r['h2_loss_kg_day']:.1f} kg/day", f"{r['h2_purity_signal_pct']:.2f}%", f"{o2:.1f} kg/day", f"{r['separated_o2_kg_day']:.1f} kg/day", f"{r['o2_loss_kg_day']:.1f} kg/day", f"{r['o2_purity_signal_pct']:.2f}%"]
    }), use_container_width=True)

with tabs[2]:
    st.header("Argon recovery")
    st.dataframe(pd.DataFrame({
        "Metric": ["Argon circulating", "Recovered Argon", "Process loss", "Leakage loss", "Makeup required", "Makeup cost", "Argon loop score"],
        "Value": [f"{argon_feed:.1f} Nm³/day", f"{r['recovered_argon_nm3_day']:.1f} Nm³/day", f"{r['argon_process_loss_nm3_day']:.1f} Nm³/day", f"{r['argon_leakage_loss_nm3_day']:.1f} Nm³/day", f"{r['argon_makeup_nm3_day']:.1f} Nm³/day", f"CHF {r['argon_makeup_cost_chf_day']:.2f}/day", f"{r['argon_loop_score']:.1f}/100"]
    }), use_container_width=True)

with tabs[3]:
    st.header("Water condensation")
    st.dataframe(pd.DataFrame({
        "Metric": ["Residual steam / water", "Condensed water", "Remaining water vapor"],
        "Value": [f"{residual:.1f} kg/day", f"{r['condensed_water_kg_day']:.1f} kg/day", f"{r['remaining_water_vapor_kg_day']:.1f} kg/day"]
    }), use_container_width=True)

with tabs[4]:
    st.header("Energy & cost")
    df = pd.DataFrame({
        "Metric": ["Gas separation energy", "Argon purification energy", "Water condensation energy", "Purge energy penalty", "Gross separation energy", "Heat offset", "Net separation energy", "kWh/kg H₂ separation", "Argon makeup cost"],
        "Value": [f"{r['separation_energy_kwh_day']:.1f} kWh/day", f"{r['argon_purification_energy_kwh_day']:.1f} kWh/day", f"{r['condensation_energy_kwh_day']:.1f} kWh/day", f"{r['purge_energy_penalty_kwh_day']:.1f} kWh/day", f"{r['gross_separation_energy_kwh_day']:.1f} kWh/day", f"{r['heat_offset_kwh_day']:.1f} kWh/day", f"{r['net_separation_energy_kwh_day']:.1f} kWh/day", f"{r['kwh_per_kg_h2_sep']:.2f} kWh/kg", f"CHF {r['argon_makeup_cost_chf_day']:.2f}/day"]
    })
    st.dataframe(df, use_container_width=True)
    chart = pd.DataFrame({"Energy stream": ["Gas sep", "Argon purif.", "Condensation", "Purge", "Heat offset"], "kWh/day": [r["separation_energy_kwh_day"], r["argon_purification_energy_kwh_day"], r["condensation_energy_kwh_day"], r["purge_energy_penalty_kwh_day"], r["heat_offset_kwh_day"]]})
    fig, ax = plt.subplots()
    ax.bar(chart["Energy stream"], chart["kWh/day"])
    ax.set_ylabel("kWh/day")
    ax.set_title("V4.5 separation energy streams")
    plt.xticks(rotation=20, ha="right")
    st.pyplot(fig)

with tabs[5]:
    st.header("Safety model")
    st.dataframe(pd.DataFrame({
        "Metric": ["H₂/O₂ safety risk", "Sensor coverage", "Purge readiness", "Reactor safety input", "V4.5 safety score"],
        "Value": [f"{r['h2_o2_safety_risk_pct']:.1f}%", f"{sensors:.1f}%", f"{purge_readiness:.1f}%", f"{reactor_safety:.1f}/100", f"{r['safety_score']:.1f}/100"]
    }), use_container_width=True)

with tabs[6]:
    st.header("Export data for V4.6 / V4.7")
    st.json({
        "module": "V4.5 Gas Separation & Argon Recovery Simulator",
        "separated_h2_kg_day": round(r["separated_h2_kg_day"], 2),
        "separated_o2_kg_day": round(r["separated_o2_kg_day"], 2),
        "condensed_water_kg_day": round(r["condensed_water_kg_day"], 2),
        "remaining_water_vapor_kg_day": round(r["remaining_water_vapor_kg_day"], 2),
        "recovered_argon_nm3_day": round(r["recovered_argon_nm3_day"], 2),
        "argon_makeup_nm3_day": round(r["argon_makeup_nm3_day"], 2),
        "argon_makeup_cost_chf_day": round(r["argon_makeup_cost_chf_day"], 2),
        "net_separation_energy_kwh_day": round(r["net_separation_energy_kwh_day"], 2),
        "kwh_per_kg_h2_sep": round(r["kwh_per_kg_h2_sep"], 3),
        "h2_purity_signal_pct": round(r["h2_purity_signal_pct"], 2),
        "o2_purity_signal_pct": round(r["o2_purity_signal_pct"], 2),
        "argon_loop_score": round(r["argon_loop_score"], 1),
        "gas_quality_score": round(r["gas_quality_score"], 1),
        "safety_score": round(r["safety_score"], 1),
        "process_score": round(r["process_score"], 1),
    })
    st.caption("These values are intended to feed V4.6 Thermal Recovery & Safety and V4.7 Integrated System Balance.")

with tabs[7]:
    st.header("Validation roadmap")
    st.markdown("""
### Key validation needs

1. Gas composition after plasma reactor: H₂, O₂, H₂O, Ar and trace species.  
2. H₂/O₂ separation method and purity measurement.  
3. Condenser performance for residual steam and water vapor.  
4. Argon drying, purification and recirculation efficiency.  
5. Argon leakage and makeup requirement.  
6. Purge logic under abnormal H₂/O₂ conditions.  
7. Gas sensor coverage, calibration and response time.  
8. Independent safety review before any industrial-performance claim.  
""")

st.markdown("---")
st.caption("HydrogenOrg V4.5 is a conceptual engineering simulator. It does not represent certified industrial gas-separation performance data.")
