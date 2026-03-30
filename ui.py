import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from app.agent import CommodityPredictionAgent, MATERIAL_DATABASE
from app.engine.cost_engine import ConstructionCostEngine
import datetime

# --- UI Config ---
st.set_page_config(
    page_title="Elite CCIE | Construction Cost Intelligence Engine",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Elite Modern Styling ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .header-text {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .subheader-text {
        color: #888;
        margin-bottom: 30px;
    }
    .confidence-badge {
        background: #203a43;
        color: #00ff00;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/construction-crane.png", width=80)
    st.title("CCIE Control Panel")
    
    app_mode = st.radio("Select Mode", ["Price Predictor", "Executive Project Estimator (Elite CCIE)"])
    
    st.divider()
    
    selected_nation = st.selectbox(
        "Select Nation",
        options=["Global", "India", "UK", "Europe"],
        index=1,
        help="Adjusts currency and local market data."
    )

    st.divider()
    if app_mode == "Executive Project Estimator (Elite CCIE)":
        st.subheader("📐 Elite Project Specs")
        plot_w = st.number_input("Plot Width (ft)", value=20)
        plot_l = st.number_input("Plot Length (ft)", value=30)
        floors = st.number_input("No. of Floors", value=2, min_value=1)
        soil = st.selectbox("Soil Type", ["Hard", "Medium", "Soft"])
        
        with st.expander("🛠️ Advanced Settings"):
            st.caption("Override design constants")
            c_ratio = st.number_input("Cement per m³ (kg)", value=350, step=10)
            s_ratio = st.number_input("Steel per Sqft (kg)", value=4.5, step=0.1)
            time_drift = st.slider("Monthly Price Drift (%)", 0.0, 10.0, 5.0) / 100.0
            
    else:
        selected_material = st.selectbox(
            "Select Material",
            options=list(MATERIAL_DATABASE.keys()),
            index=0
        )

# --- Main Dashboard ---

if app_mode == "Price Predictor":
    st.markdown(f"<h1 class='header-text'>🏗️ {selected_material.upper()} PRICE PREDICTOR</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Real-time market sentiment & regression-based price forecasting.</p>", unsafe_allow_html=True)

    if st.button(f"🚀 Run Analysis for {selected_nation}"):
        with st.spinner("Processing market data..."):
            agent = CommodityPredictionAgent(selected_material, nation=selected_nation)
            result = agent.run_prediction_pipeline()

            if result.get("success"):
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Current Ticker", result["symbol"])
                with col2: 
                    sym = "₹" if result['currency'] == "INR" else "$"
                    st.metric(f"Prediction ({result['currency']})", f"{sym}{result['predicted_price']:,}")
                with col3:
                    sent = result["current_sentiment"]
                    label = "Bullish 📈" if sent > 0.1 else ("Bearish 📉" if sent < -0.1 else "Neutral 😐")
                    st.metric("Sentiment", label, delta=f"{sent:.2f}")

                st.divider()
                st.subheader(f"📊 90-Day Trend ({result['symbol']})")
                df_hist = result["historical_data"]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_hist['Date'], y=df_hist['Close'], fill='tozeroy', line=dict(color='#ff4b4b')))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Error: {result.get('error')}")

else:
    # ELITE CCIE MODE
    st.markdown("<div style='display: flex; align-items: center; justify-content: space-between;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='header-text'>🏗️ ELITE PROJECT INTELLIGENCE ENGINE</h1>", unsafe_allow_html=True)
    st.markdown("<div class='confidence-badge'>AI CONFIDENCE: HIGH (±10%)</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<p class='subheader-text'>Geometry-aware estimation for {plot_w}x{plot_l} ({plot_w*plot_l} sqft) {floors}-Floor Project.</p>", unsafe_allow_html=True)

    if st.button("🏗️ Calculate Full Project Estimate"):
        with st.spinner("Analyzing Geometry & Simulating Time-Based Costs..."):
            # 1. Fetch Dynamic Market Trends
            agent_c = CommodityPredictionAgent("cement", nation=selected_nation)
            agent_s = CommodityPredictionAgent("steel", nation=selected_nation)
            
            p_cement = agent_c.run_prediction_pipeline()["predicted_price"]
            p_steel = agent_s.run_prediction_pipeline()["predicted_price"]
            
            # 2. Run Elite Cost Engine (Geometry + Time + Uncertainty)
            engine = ConstructionCostEngine(plot_w, plot_l, floors, soil)
            
            # Apply Overrides
            engine.estimator.rules["m3_concrete"]["cement_kg"] = c_ratio
            engine.estimator.rules["structural"]["steel_kg_per_sqft"] = s_ratio
            
            prices = {
                "cement": p_cement,
                "steel": p_steel,
                "currency": "INR" if selected_nation == "India" else "USD"
            }
            report = engine.calculate_project_costs(prices, monthly_drift=time_drift)
            
            # 3. High-Level Financials
            c1, c2, c3, c4 = st.columns(4)
            sym = "₹" if prices['currency'] == "INR" else "$"
            c1.metric("Predicted Total Cost", f"{sym}{report['summary']['total_cost']:,}")
            c2.metric("Min Estimate (-10%)", f"{sym}{report['summary']['cost_min']:,}")
            c3.metric("Max Estimate (+10%)", f"{sym}{report['summary']['cost_max']:,}")
            c4.metric("Steel Needed", f"{report['summary']['total_steel_kg']} Kg")
            
            st.divider()
            
            # 4. Phase-Based Time Charts & Geometry Insights
            left_col, right_col = st.columns([2, 1])
            
            with left_col:
                st.subheader("📈 Time-Based Cost Breakdown (Phases)")
                # Generate Timeline Chart
                labels = list(report["segments"].keys())
                costs = [seg["cost"] for seg in report["segments"].values()]
                phases = [seg["phase"] for seg in report["segments"].values()]
                
                timeline_df = pd.DataFrame({"Segment": labels, "Cost": costs, "Construction Phase": phases})
                fig_time = px.bar(timeline_df, x="Segment", y="Cost", color="Construction Phase", 
                                  title="Project Expenditure vs Construction Time Cycle",
                                  color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig_time, use_container_width=True)
                
            with right_col:
                st.subheader("🍰 Structural Cost Share")
                # Pie Chart
                fig_pie = px.pie(values=costs, names=labels, hole=.4, 
                                 color_discrete_sequence=px.colors.qualitative.Prism)
                st.plotly_chart(fig_pie, use_container_width=True)

            st.divider()
            
            # 5. Elite Segment Analysis Table
            st.subheader("📋 Geometry-Aware Segment Details")
            seg_data = []
            for name, data in report["segments"].items():
                row = {
                    "Segment": name,
                    "Phase": data["phase"],
                    "Cement (Bags)": data["cement_bags"],
                    "Steel (Kg)": data.get("steel_kg", 0.0),
                    f"Cost ({prices['currency']})": f"{sym}{data['cost']:,}"
                }
                if "num_rooms" in data:
                    row["Geometry (Rooms)"] = data["num_rooms"]
                seg_data.append(row)
            
            st.table(pd.DataFrame(seg_data))
            
            st.success(f"Elite BoQ generation for **{selected_nation}** market complete with **{time_drift*100}%** monthly volatility factor.")

# Footer
st.markdown("<br><hr><center><small>Powered by Antigravity Elite CCIE Engine v4.0 • Arch-Level Intelligence Tool</small></center>", unsafe_allow_html=True)
