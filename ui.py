import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from app.agent import CommodityPredictionAgent, MATERIAL_DATABASE
from engine.cost_engine import EliteCostEngine
from utils.export import BOQExporter
import datetime
import os

# --- UI Config ---
st.set_page_config(
    page_title="CCIE ELITE | Advanced Construction Intelligence",
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
        padding: 22px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .header-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 2px;
    }
    .subheader-text { color: #888; font-size: 1.1rem; margin-bottom: 25px; }
    .advice-card {
        background: rgba(30,41,59,0.6);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #22c55e;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/construction-crane.png", width=80)
    st.title("CCIE ELITE V6.0")
    
    app_mode = st.radio("System Mode", ["Market Analysis", "Elite BOQ Estimator"])
    
    st.divider()
    
    selected_nation = st.selectbox(
        "Market Region",
        options=["India", "USA", "UK", "Europe"],
        index=0
    )

    st.divider()
    if app_mode == "Elite BOQ Estimator":
        st.subheader("📐 Project Geometry")
        plot_w = st.number_input("Width (ft)", value=20)
        plot_l = st.number_input("Length (ft)", value=30)
        floors = st.number_input("Floors", value=2, min_value=1)
        soil = st.selectbox("Soil Type", ["Hard", "Medium", "Soft"])
        
        with st.expander("🛠️ Advanced Simulation"):
            st.caption("Override design assumptions")
            c_ratio = st.number_input("Cement/m3 (kg)", value=350, step=10)
            s_ratio = st.number_input("Steel/sqft (kg)", value=4.5, step=0.1)
            time_drift = st.slider("Forecast Drift (%)", 0.0, 10.0, 5.0) / 100.0
    else:
        selected_material = st.selectbox("Predict Asset", list(MATERIAL_DATABASE.keys()))

# --- Main Dashboard ---

if app_mode == "Market Analysis":
    st.markdown(f"<h1 class='header-text'>🏗️ MARKET ANALYSIS: {selected_material.upper()}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Real-time volatility and news sentiment prediction.</p>", unsafe_allow_html=True)

    if st.button("🚀 Analyze Market Sentiment"):
        with st.spinner("Processing news and history..."):
            agent = CommodityPredictionAgent(selected_material, nation=selected_nation.lower())
            result = agent.run_prediction_pipeline()

            if result.get("success"):
                c1, c2, c3 = st.columns(3)
                sym = "₹" if result['currency'] == "INR" else "$"
                c1.metric("Asset Sym", result["symbol"])
                c2.metric("Predicted Target", f"{sym}{result['predicted_price']:,}")
                sent = result["current_sentiment"]
                c3.metric("Sentiment", "Positive 🔥" if sent > 0.1 else "Neutral ☁️", delta=f"{sent:.2f}")

                st.divider()
                df_hist = result["historical_data"]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_hist['Date'], y=df_hist['Close'], fill='tozeroy', line=dict(color='#ff4b4b')))
                fig.update_layout(template="plotly_dark", margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Market Analysis Failed.")

else:
    # ELITE BOQ ESTIMATOR
    st.markdown("<h1 class='header-text'>🧠 ELITE PROJECT ESTIMATOR (CCIE)</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subheader-text'>Predictive BOQ for {plot_w}x{plot_l} {floors}-Floor Project in {selected_nation}.</p>", unsafe_allow_html=True)

    if st.button("🏗️ Run Full Project Simulation"):
        with st.spinner("Executing Architecture-Level Simulation..."):
            # 1. Fetch Dynamic Predictive Prices for core materials
            # We predict Cement and Steel as core drivers
            try:
                agent_c = CommodityPredictionAgent("cement", nation=selected_nation.lower())
                agent_s = CommodityPredictionAgent("steel", nation=selected_nation.lower())
                
                prices = {
                    "cement": agent_c.run_prediction_pipeline()["predicted_price"],
                    "steel": agent_s.run_prediction_pipeline()["predicted_price"],
                    "bricks": 12.0  # Base bricks cost (Standard)
                }
                
                # 2. Run Elite Cost Engine
                engine = EliteCostEngine(plot_w, plot_l, floors, soil, nation=selected_nation.lower())
                
                # Apply Simulation Overrides
                engine.estimator.rules["concrete"]["cement_kg_per_m3"] = c_ratio
                engine.estimator.rules["structural"]["steel_kg_per_sqft"] = s_ratio
                
                report = engine.generate_elite_boq(prices, monthly_drift=time_drift)
                
                # 3. High-Level Financials
                c1, c2, c3, c4 = st.columns(4)
                sym = "₹" if report['currency'] == "INR" else "$"
                c1.metric("Predicted Project Cost", f"{sym}{report['total_cost']:,}")
                c2.metric("Cost Range (Min/Max)", f"{sym}{report['uncertainty']['cost_min']:,} - {sym}{report['uncertainty']['cost_max']:,}")
                c3.metric("Confidence Level", f"{report['uncertainty']['confidence_pct']}%")
                c4.metric("Built Area", f"{report['built_area_sqft']:,} sqft")
                
                st.divider()

                # 4. Procurement Cards
                st.subheader("🛍️ Automated Procurement Strategy")
                cols = st.columns(len(report["procurement_advice"]))
                for i, advice in enumerate(report["procurement_advice"]):
                    with cols[i]:
                        st.markdown(f"""
                        <div class='advice-card'>
                            <span style='font-size: 0.8rem; font-weight: bold;'>{advice['material'].upper()} SIGNAL: {advice['strategy']}</span>
                            <h4 style='margin: 10px 0;'>{advice['recommendation']}</h4>
                            <p style='color: #22c55e; font-size: 0.9rem;'>Potential Saving: {sym}{advice['est_savings']:,}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.divider()

                # 5. Visual Breakdown Charts
                left_col, right_col = st.columns([2, 1])
                with left_col:
                    st.subheader("🏢 Structural Expenditure Chart")
                    seg_data = [{"Segment": k, "Cost": v["cost"], "Phase": v["phase"]} for k,v in report["segments"].items()]
                    df_seg = pd.DataFrame(seg_data)
                    fig_bar = px.bar(df_seg, x="Segment", y="Cost", color="Phase", template="plotly_dark", barmode='group')
                    st.plotly_chart(fig_bar, use_container_width=True)
                with right_col:
                    st.subheader("🍰 Financial Split")
                    fig_pie = px.pie(df_seg, values="Cost", names="Segment", hole=0.5, template="plotly_dark")
                    st.plotly_chart(fig_pie, use_container_width=True)

                # 6. Detailed BOQ Data Table
                st.subheader("📋 Segmented Bill of Quantities")
                st.table(df_seg)
                
                # 7. EXPORT Deliverable
                st.subheader("💾 Export Deliverables")
                exporter = BOQExporter(report)
                json_path = exporter.export_json()
                with open(json_path, 'r') as f:
                    st.download_button("📩 Download Final BOQ (JSON)", data=f, file_name=json_path)

            except Exception as e:
                st.error(f"Engine Simulation Failed: {str(e)}")

# Footer
st.markdown("<br><hr><center><small><b>CCIE ELITE v6.0</b> • Advanced Construction Cost Intelligence Platform</small></center>", unsafe_allow_html=True)
