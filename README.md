# 🏗️ Construction Material & Commodity Prediction AI Agent

This project provides a production-level AI agent for predicting prices of **construction materials** (Cement, PVC, Land, Steel) and **commodities** (Gold, Oil) using market data and news sentiment.

## 🚀 Supported Materials & Proxies

*   **🧱 Cement**: `ULTRACEMCO.NS` (India) / `CX` (Global)
*   **🔵 PVC**: `WLK` (Westlake Corp)
*   **🌳 Land/Real Estate**: `VNQ` (Vanguard Real Estate ETF)
*   **🏗️ Steel/Rebar**: `NUE` (Nucor) / `SR=F`
*   **🪜 Aluminum**: `AA` (Alcoa)
*   **🛢️ Bitumen**: `VMC` (Asphalt proxy)
*   **💧 Waterproofing**: `CSL` (Carlisle Companies)
*   **🏠 Insulation**: `OC` (Owens Corning)
*   **🪟 Glass**: `TGLS` (Architectural Glass)
*   **🧴 Sealants/Coatings**: `RPM` (RPM International)
*   **🪵 Lumber**: `LBS=F`
*   **💰 Commodities**: Gold (`GC=F`), Oil (`CL=F`), Silver (`SI=F`)

## 🛠️ Key Features

*   **📈 Historical Data**: Fetches 3 months of daily price data using `yfinance`.
*   **📰 News Sentiment**: Scrapes recent headlines and performs sentiment analysis (with mock fallback for demo).
*   **🧠 Baseline ML**: Trains a Linear Regression model with lag features (past 5 days) and aggregate sentiment.
*   **🤖 Antigravity Tool Wrapper**: A modular interface ready to be plugged into an agent.

## 📁 Project Structure

```text
/commodity-ai-agent
├── app/
│   ├── agent.py               # Main pipeline orchestration
├── data/
│   ├── market_data.py         # YFinance data fetcher
│   ├── news_data.py           # NewsAPI logic and mock fallback
├── features/
│   ├── feature_engineering.py  # Lag features and sentiment integration
├── models/
│   ├── train.py               # Model training (Linear Regression)
│   ├── predict.py             # Prediction logic
├── services/
│   ├── sentiment.py           # Sentiment analysis (LLM call placeholder)
├── antigravity_tool.py         # Tool wrapper for Antigravity Agent
├── main.py                    # Entry point for CLI
├── requirements.txt           # Project dependencies
└── .env.example               # Environment variables template
```

## ⚙️ Initial Setup

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Setup**:
    Copy `.env.example` to `.env` and add your **NewsAPI** key (optional, mock fallback is provided).
    ```bash
    copy .env.example .env
    ```

## 📊 Usage

### 🌐 Launching the Dashboard (NEW)
To open the interactive, premium UI dashboard:
```bash
streamlit run ui.py
```
*(Displays metrics, interactive charts, and sentiment analysis).*

### Running via CLI
To predict the price for **Cement**:
```bash
python main.py --material cement
```

For **PVC**:
```bash
python main.py --material pvc
```

For **Land (Real Estate Proxy)**:
```bash
python main.py --material land
```

### Using as an Antigravity Tool
Import the `material_prediction_tool` from `antigravity_tool.py`:

```python
from antigravity_tool import material_prediction_tool
print(material_prediction_tool("cement"))
```

## 🛠️ Production Upgrades (Future Roadmap)

1.  **Model Upgrade**: Switch to **XGBoost** or **CatBoost** for better non-linear capture.
2.  **Sentiment**: Implement real LLM calls (Claude/GPT-4) in `services/sentiment.py`.
3.  **Logging**: Centralized ELK stack or cloud-based logging for monitoring.
4.  **Scaling**: Dockerize the application and run on a schedule (e.g., Cron/Airflow).
5.  **Streaming**: Integrate real-time price feeds for low-latency analysis.
