import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.agent import CommodityPredictionAgent, MATERIAL_DATABASE
from app.engine.cost_engine import ConstructionCostEngine
import datetime

# --- UI Config ---
st.set_page_config(
    page_title="CCIE | Construction Cost Intelligence Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern Styling ---
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
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/construction.png", width=80)
    st.title("CCIE Control Panel")
    
    app_mode = st.radio("Select Mode", ["Price Predictor", "Project Estimator (CCIE)"])
    
    st.divider()
    
    selected_nation = st.selectbox(
        "Select Nation",
        options=["Global", "India", "UK", "Europe"],
        index=1,
        help="Adjusts currency and local market data."
    )

    st.divider()
    if app_mode == "Project Estimator (CCIE)":
        st.subheader("📐 Project Specs")
        plot_w = st.number_input("Plot Width (ft)", value=20)
        plot_l = st.number_input("Plot Length (ft)", value=30)
        floors = st.number_input("No. of Floors", value=2, min_value=1)
        soil = st.selectbox("Soil Type", ["Hard", "Medium", "Soft"])
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
    st.markdown("<h1 class='header-text'>🧱 PROJECT COST INTELLIGENCE (CCIE)</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subheader-text'>Estimating {plot_w}x{plot_l} ({plot_w*plot_l} sqft) {floors}-Floor Villa costs with predictive pricing.</p>", unsafe_allow_html=True)

    if st.button("🏗️ Calculate Full Project Estimate"):
        with st.spinner("Fetching predictive prices and estimating quantities..."):
            # 1. Fetch dynamic prices for core materials
            agent_c = CommodityPredictionAgent("cement", nation=selected_nation)
            agent_s = CommodityPredictionAgent("steel", nation=selected_nation)
            
            p_cement = agent_c.run_prediction_pipeline()["predicted_price"]
            p_steel = agent_s.run_prediction_pipeline()["predicted_price"]
            
            # 2. Run Cost Engine
            engine = ConstructionCostEngine(plot_w, plot_l, floors, soil)
            prices = {
                "cement": p_cement,
                "steel": p_steel,
                "currency": "INR" if selected_nation == "India" else "USD"
            }
            report = engine.calculate_project_costs(prices)
            
            # 3. Display High-Level Summary
            c1, c2, c3 = st.columns(3)
            sym = "₹" if prices['currency'] == "INR" else "$"
            c1.metric("Total Project Cost", f"{sym}{report['summary']['total_cost']:,}")
            c2.metric("Total Cement", f"{report['summary']['total_cement_bags']} Bags")
            c3.metric("Total Steel", f"{report['summary']['total_steel_kg']} Kg")
            
            st.divider()
            
            # 4. Segment-wise Breakdown
            st.subheader("📋 Segment-wise Breakdown")
            seg_data = []
            for name, data in report["segments"].items():
                seg_data.append({
                    "Segment": name,
                    "Cement (Bags)": data["cement_bags"],
                    "Steel (Kg)": data.get("steel_kg", 0.0),
                    f"Cost ({prices['currency']})": data["cost"]
                })
            
            st.table(pd.DataFrame(seg_data))
            
            st.info("⚠️ Note: These are estimated quantities based on civil engineering rules and the specific floor plan provided.")

# Footer
st.markdown("<br><hr><center><small>Powered by Antigravity CCIE Engine v3.0</small></center>", unsafe_allow_html=True)
