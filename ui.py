import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.agent import CommodityPredictionAgent, MATERIAL_MAP
import datetime

# --- UI Config ---
st.set_page_config(
    page_title="MaterialPrice AI Predictor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern Styling (Glassmorphism inspired) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .header-text {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/construction.png", width=120)
    st.title("Settings")
    
    # Material selection
    selected_material = st.selectbox(
        "Select Material",
        options=list(MATERIAL_MAP.keys()),
        index=0,
        help="Select a construction material or commodity for prediction."
    )
    
    st.divider()
    st.info("💡 **How it works:** Analyzes 3 months of YFinance data + real-time news sentiment via LLM analysis.")

# --- Main Dashboard ---
st.markdown(f"<h1 class='header-text'>🏗️ {selected_material.upper()} PRICE PREDICTOR</h1>", unsafe_allow_html=True)

if st.button("🚀 Run Prediction Agent"):
    with st.spinner("Analyzing market patterns & news sentiment..."):
        # Run prediction agent
        agent = CommodityPredictionAgent(selected_material)
        result = agent.run_prediction_pipeline()

        if result.get("success"):
            # 1. Metrics section
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Current Probability Ticker",
                    value=result["symbol"]
                )
            with col2:
                st.metric(
                    label="Next Day Prediction",
                    value=f"${result['predicted_price']:.2f}"
                )
            with col3:
                sentiment = result["current_sentiment"]
                sentiment_label = "Bullish 📈" if sentiment > 0.1 else ("Bearish 📉" if sentiment < -0.1 else "Neutral 😐")
                st.metric(
                    label="Market Sentiment",
                    value=sentiment_label,
                    delta=f"{sentiment:.2f}"
                )

            st.divider()

            # 2. Historical Chart
            st.subheader(f"📊 90-Day Price Movement ({result['symbol']})")
            df_hist = result["historical_data"]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_hist['Date'], 
                y=df_hist['Close'],
                mode='lines',
                line=dict(color='#ff4b4b', width=3),
                fill='tozeroy',
                name="History"
            ))
            
            # Add prediction point
            last_date = df_hist['Date'].iloc[-1]
            next_date = last_date + datetime.timedelta(days=1)
            fig.add_trace(go.Scatter(
                x=[last_date, next_date],
                y=[df_hist['Close'].iloc[-1], result['predicted_price']],
                mode='lines+markers',
                line=dict(color='#00ff00', width=4, dash='dash'),
                name="Prediction"
            ))

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                hovermode='x unified',
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)

            st.success(f"Prediction logic using **{result['model_type']}** complete.")
        
        else:
            st.error(f"Prediction failed: {result.get('error')}")

else:
    st.info("Click 'Run Prediction Agent' above to analyze the market.")
    
# Footer
st.markdown("<br><hr><center><small>Powered by Antigravity Agent Tool • v2.0</small></center>", unsafe_allow_html=True)
