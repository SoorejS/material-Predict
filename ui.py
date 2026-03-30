import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from app.agent import CommodityPredictionAgent, MATERIAL_DATABASE
from app.engine.cost_engine import ConstructionCostEngine
import datetime

# --- UI Config ---
st.set_page_config(
    page_title="CCIE V5.0 | Decision Intelligence Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- V5.0 Elite Styling ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .header-text {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .subheader-text { color: #8b949e; margin-bottom: 25px; font-size: 1.1rem; }
    .status-card {
        background: rgba(30, 41, 59, 0.7);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
    }
    .risk-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
    }
    .recommendation-pill {
        background: #064e3b;
        color: #34d399;
        padding: 4px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/brain.png", width=70)
    st.title("CCIE V5.0")
    
    app_mode = st.radio("Intelligence Mode", ["Price Analysis", "Decision Intelligence (V5.0 Elite)"])
    
    st.divider()
    
    selected_nation = st.selectbox(
        "Market Region",
        options=["Global", "India", "UK", "Europe"],
        index=1
    )

    st.divider()
    if app_mode == "Decision Intelligence (V5.0 Elite)":
        st.subheader("📐 Project Geometry")
        plot_w = st.number_input("Width (ft)", value=20)
        plot_l = st.number_input("Length (ft)", value=30)
        floors = st.number_input("Floors", value=2, min_value=1)
        soil = st.selectbox("Soil Profile", ["Hard", "Medium", "Soft"])
        
        with st.expander("🛠️ Decision Factors"):
            c_ratio = st.number_input("Cement (kg/m³)", value=350, step=10)
            s_ratio = st.number_input("Steel (kg/sqft)", value=4.5, step=0.1)
            time_drift = st.slider("Forecast Monthly Drift (%)", 0.0, 10.0, 5.0) / 100.0
    else:
        selected_material = st.selectbox("Select Material", list(MATERIAL_DATABASE.keys()))

# --- Main Dashboard ---

if app_mode == "Price Analysis":
    st.markdown(f"<h1 class='header-text'>🏗️ MARKET INTELLIGENCE: {selected_material.upper()}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Phase-aware trend forecasting into the next 90 days.</p>", unsafe_allow_html=True)

    if st.button(f"🚀 Execute Sentiment Analysis"):
        with st.spinner("Analyzing world markets..."):
            agent = CommodityPredictionAgent(selected_material, nation=selected_nation)
            result = agent.run_prediction_pipeline()

            if result.get("success"):
                c1, c2, c3 = st.columns(3)
                sym = "₹" if result['currency'] == "INR" else "$"
                c1.metric("Asset Ticker", result["symbol"])
                c2.metric("Next-Day Target", f"{sym}{result['predicted_price']:,}")
                sent = result["current_sentiment"]
                c3.metric("Sentiment Index", "Positive 🔥" if sent > 0.1 else "Neutral ☁️", delta=f"{sent:.2f}")

                st.divider()
                df_hist = result["historical_data"]
                fig = px.line(df_hist, x="Date", y="Close", title="Historical Volatility (90D)",
                             template="plotly_dark", color_discrete_sequence=['#3b82f6'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Data Fetch Failed.")

else:
    # V5.0 DECISION INTELLIGENCE
    st.markdown("<h1 class='header-text'>🧠 DECISION INTELLIGENCE PLATFORM</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subheader-text'>Simulating {plot_w}x{plot_l} {floors}-Floor Project in {selected_nation}.</p>", unsafe_allow_html=True)

    if st.button("🏗️ Run Executive Decision Simulation"):
        with st.spinner("Analyzing Procurement Arbitrage & Risk Benchmarks..."):
            # 1. Fetch Dynamic Market Data
            agent_c = CommodityPredictionAgent("cement", nation=selected_nation)
            agent_s = CommodityPredictionAgent("steel", nation=selected_nation)
            p_cement = agent_c.run_prediction_pipeline()["predicted_price"]
            p_steel = agent_s.run_prediction_pipeline()["predicted_price"]
            
            # 2. Execute V5.0 Decision Engine
            engine = ConstructionCostEngine(plot_w, plot_l, floors, soil, nation=selected_nation)
            engine.estimator.rules["m3_concrete"]["cement_kg"] = c_ratio
            engine.estimator.rules["structural"]["steel_kg_per_sqft"] = s_ratio
            
            prices = {"cement": p_cement, "steel": p_steel, "currency": "INR" if selected_nation == "India" else "USD"}
            report = engine.calculate_project_costs(prices, monthly_drift=time_drift)
            
            # 3. EXECUTIVE CARD: Decision & Benchmarking
            st.markdown(f"""
            <div class='status-card'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div>
                        <span class='risk-badge' style='background: #1e293b; color: #fff;'>MARKET STATUS</span>
                        <h2 style='margin: 10px 0;'>{report['risk_analysis']['status']}</h2>
                        <p style='color: #8b949e;'>Current Estimate: <b>{report['summary']['currency']} {report['risk_analysis']['cost_per_sqft']}/sqft</b> 
                        (Standard: {report['risk_analysis']['market_benchmark']}/sqft)</p>
                    </div>
                    <div style='text-align: right;'>
                        <span class='risk-badge' style='background: {'#ef4444' if 'High' in report['risk_analysis']['category'] else '#10b981'};'>Project Risk: {report['risk_analysis']['category']}</span>
                        <h2 style='margin: 10px 0;'>{prices['currency']} {report['summary']['total_cost']:,}</h2>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 4. PROCUREMENT ADVISOR CARD
            st.subheader("🛍️ Procurement Advisor")
            cols = st.columns(len(report["procurement_advice"]))
            for i, advice in enumerate(report["procurement_advice"]):
                with cols[i]:
                    st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.02); padding: 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);'>
                        <span class='recommendation-pill'>{advice['material'].upper()} BUY SIGNAL: {advice['buy_signal']}</span>
                        <h4 style='margin: 10px 0;'>{advice['recommendation']}</h4>
                        <p style='font-size: 0.9rem; color: #34d399;'>Estimated Saving: {prices['currency']} {advice['potential_savings']:,}</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
            
            # 5. Visual Analytics (Charts)
            c_left, c_right = st.columns([2, 1])
            with c_left:
                st.subheader("📈 Project Expenditure Timeline")
                timeline_df = pd.DataFrame([{"Segment": k, "Cost": v["cost"], "Phase": v["phase"]} for k,v in report["segments"].items()])
                fig_bar = px.bar(timeline_df, x="Segment", y="Cost", color="Phase", template="plotly_dark", barmode='group')
                st.plotly_chart(fig_bar, use_container_width=True)
            with c_right:
                st.subheader("🍰 Financial Split")
                fig_pie = px.pie(timeline_df, values="Cost", names="Segment", hole=0.5, template="plotly_dark")
                st.plotly_chart(fig_pie, use_container_width=True)

            # 6. Scenario Simulation Comparison
            st.subheader("🏢 Scenario Analysis Tool")
            scenario_df = pd.DataFrame([
                {"Scenario": "Your Selection", "Cost": report['summary']['total_cost'], "Risk": report['risk_analysis']['category']},
                {"Scenario": "Standard Soils", "Cost": report['summary']['total_cost'] * 0.9, "Risk": "Low 🟢"},
                {"Scenario": "Premium Reinforce", "Cost": report['summary']['total_cost'] * 1.25, "Risk": "Medium 🟡"}
            ])
            st.table(scenario_df)

# Footer
st.markdown("<br><hr><center><small><b>CCIE Intelligence Platform v5.0</b> • Powered by Antigravity Decision Engine</small></center>", unsafe_allow_html=True)
