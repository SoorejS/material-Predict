import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from app.agent import CommodityPredictionAgent, MATERIAL_DATABASE
from engine.cost_engine import EliteCostEngine
from utils.export import EliteExporter
import os

# --- V7.0 UI Config (Final Polish) ---
st.set_page_config(
    page_title="CCIE ELITE V7.0 | Advanced Construction & Financial Intelligence",
    page_icon="🦾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Elite V7.0 Style Overhaul ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric {
        background: rgba(255, 255, 255, 0.04);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .header-text {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 2px;
        letter-spacing: -1.5px;
    }
    .subheader-text { color: #8b949e; font-size: 1.15rem; margin-bottom: 25px; }
    .advice-card {
        background: rgba(30,41,59,0.5);
        padding: 22px;
        border-radius: 12px;
        border-left: 6px solid #22c55e;
        margin-bottom: 15px;
    }
    .opt-card {
        background: rgba(59,130,246,0.1);
        padding: 22px;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 15px;
    }
    .download-btn {
        margin-right: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/blueprint.png", width=75)
    st.title("CCIE ELITE V7.0")
    
    app_mode = st.radio("Intelligence Platform", ["Market Analysis", "Elite Optimizer (CCIE)"])
    
    selected_nation = st.selectbox(
        "Market Region",
        options=["India", "USA", "UK", "Europe"],
        index=0
    )

    st.divider()
    if app_mode == "Elite Optimizer (CCIE)":
        st.subheader("📐 High-Precision Geometry")
        plot_w = st.number_input("Width (ft)", value=20)
        plot_l = st.number_input("Length (ft)", value=30)
        floors = st.number_input("Floors", value=2, min_value=1)
        soil = st.selectbox("Soil Profile Type", ["Hard", "Medium", "Soft"])
        
        with st.expander("🛠️ Advanced Engineering Overrides"):
            c_ratio = st.number_input("Cement/m3 (kg)", value=350, step=10)
            s_ratio = st.number_input("Steel/sqft (kg)", value=4.5, step=0.1)
            time_drift = st.slider("Market Price Drift (%)", -5.0, 10.0, 5.0) / 100.0
    else:
        selected_material = st.selectbox("Predict Market Asset", list(MATERIAL_DATABASE.keys()))

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
                c1.metric("Ticker", result["symbol"])
                c2.metric("Predicted Target", f"{sym}{result['predicted_price']:,}")
                sent = result["current_sentiment"]
                c3.metric("Sentiment", "Bullish 🔥" if sent > 0.1 else "Neutral ☁️", delta=f"{sent:.2f}")

                st.divider()
                df_hist = result["historical_data"]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_hist['Date'], y=df_hist['Close'], fill='tozeroy', line=dict(color='#3b82f6')))
                fig.update_layout(template="plotly_dark", margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)

else:
    # ELITE OPTIMIZER
    st.markdown("<h1 class='header-text'>💪 ELITE CCIE: DECISION & FINANCIAL PLATFORM</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subheader-text'>Dimension-specific material estimation & procurement hedging for {plot_w}x{plot_l} ({floors} Floors).</p>", unsafe_allow_html=True)

    if st.button("🏗️ Execute Architecture-Level Simulation"):
        with st.spinner("Calculating Financial Optimizations..."):
            try:
                agent_c = CommodityPredictionAgent("cement", nation=selected_nation.lower())
                agent_s = CommodityPredictionAgent("steel", nation=selected_nation.lower())
                
                prices = {
                    "cement": agent_c.run_prediction_pipeline()["predicted_price"],
                    "steel": agent_s.run_prediction_pipeline()["predicted_price"],
                    "bricks": 12.0
                }
                
                engine = EliteCostEngine(plot_w, plot_l, floors, soil, nation=selected_nation.lower())
                engine.estimator.rules["concrete"]["cement_kg_per_m3"] = c_ratio
                engine.estimator.rules["structural"]["steel_kg_per_sqft"] = s_ratio
                
                report = engine.generate_elite_boq(prices, monthly_drift=time_drift)
                
                # 3. Financial Card Summary (Metric Box)
                c1, c2, c3, c4 = st.columns(4)
                sym = "₹" if report['currency'] == "INR" else "$"
                c1.metric("Predicted Total Project Cost", f"{sym}{report['total_cost']:,}")
                c2.metric("Min/Max Confidence Range", f"{sym}{report['uncertainty']['cost_min']:,} - {sym}{report['uncertainty']['cost_max']:,}")
                c3.metric("Cost Accuracy Level", f"{report['uncertainty']['confidence_pct']}%")
                c4.metric("Built Area Estimation", f"{report['built_area_sqft']:,} sqft")
                
                st.divider()

                # 4. EXPORT DELIVERABLES (NEW V7.0 FEATURES)
                st.subheader("💾 Export Industry-Ready Deliverables")
                col_exp1, col_exp2 = st.columns(2)
                exporter = EliteExporter(report, plot_w, plot_l)
                
                with col_exp1:
                    xl_path = exporter.generate_excel()
                    with open(xl_path, 'rb') as f:
                        st.download_button("📊 Download Multi-Sheet Excel BOQ", data=f, file_name=xl_path, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
                with col_exp2:
                    pdf_path = exporter.generate_pdf()
                    with open(pdf_path, 'rb') as f:
                        st.download_button("📩 Download Executive PDF Report", data=f, file_name=pdf_path, mime="application/pdf")

                st.divider()

                # 5. Optimization Intelligence
                st.subheader("💡 Strategic Financial Optimizations")
                opt_cols = st.columns(len(report["optimizations"]))
                for i, opt in enumerate(report["optimizations"]):
                    with opt_cols[i]:
                        st.markdown(f"""
                        <div class='opt-card'>
                            <span style='font-size: 0.8rem; font-weight: bold;'>IMPACT: {opt['impact']}</span>
                            <h4 style='margin: 10px 0;'>{opt['action']}</h4>
                            <p style='color: #22c55e; font-size: 0.95rem; font-weight: 800;'>Potential Savings: {opt['est_saving']}</p>
                            <p style='color: #8b949e; font-size: 0.85rem;'>{opt['rationale']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.divider()

                # 6. Material Breakdown Tables (Dimension Specific)
                st.subheader("📋 Dimension-Specific Material BOQ")
                breakdown_df = pd.DataFrame([{"Segment": k, "Cost": f"{sym}{v['cost']:,}", "Phase": v['phase']} for k,v in report['segments'].items()])
                st.table(breakdown_df)
                
                with st.expander("🔍 Detailed Raw Segment Geometry"):
                    st.json(report["segments"])

                # 7. Analytics
                st.divider()
                st.subheader("🍰 Structural Expenditure Split")
                fig_pie = px.pie(breakdown_df, values=[v['cost'] for v in report['segments'].values()], names="Segment", hole=0.5, template="plotly_dark", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, use_container_width=True)

            except Exception as e:
                st.error(f"Elite Simulation Error: {str(e)}")

# Footer
st.markdown("<br><hr><center><small><b>CCIE ELITE PLATFORM v7.0</b> • Advanced Architectural Decision Intelligence Engine</small></center>", unsafe_allow_html=True)
