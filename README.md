# 🛵 Estimated Time of Arrival (ETA) Prediction for a Food Delivery Company

Predicting food delivery time (ETA) using machine learning to improve customer experience, courier allocation, and operational efficiency.

---

## 📌 Project Overview

Accurate delivery time estimates are critical for food delivery platforms. Underestimating the ETA leads to disappointed customers, while overestimating it can reduce conversion. This project builds a regression model that predicts how long an order will take to arrive, based on order, restaurant, courier, and environmental factors.

## 🎯 Objectives

- Explore and understand the key factors that influence delivery time.
- Build and evaluate machine learning models to predict ETA (in minutes).
- Deliver insights and recommendations in a business **report**.
- Present results through an interactive **dashboard**.

## 📊 Dataset

The dataset contains food delivery order records with features such as:

| Category | Example Features |
|---|---|
| Courier | age, rating, vehicle type, vehicle condition |
| Location | restaurant & delivery coordinates, distance, city type |
| Order | order type, order date, time ordered, time picked up |
| Environment | weather conditions, road traffic density, festival |
| Target | `time_taken (min)` |

> Place raw data in `data/raw/` and processed data in `data/processed/` (data files are not tracked by Git).

## 🗂️ Project Structure

```
ETA-Prediction-for-a-Food-Delivery-Company/
├── data/
│   ├── raw/            # Original, immutable dataset
│   └── processed/      # Cleaned & feature-engineered data
├── notebooks/          # Jupyter notebooks (EDA, modeling, evaluation)
├── src/                # Reusable Python scripts (preprocessing, features, training)
├── models/             # Trained model artifacts
├── report/             # Final report / presentation (PDF, PPT, figures)
├── dashboard/          # Dashboard files (Tableau / Power BI / Looker Studio / Streamlit)
├── requirements.txt    # Python dependencies
└── README.md
```

## 🔄 Workflow

1. **Business Understanding** – define the problem and success metrics.
2. **Data Understanding & EDA** – distributions, correlations, and key drivers of delivery time.
3. **Data Preparation** – cleaning, handling missing values, outliers, and encoding.
4. **Feature Engineering** – haversine distance, time of day, day of week, preparation time, etc.
5. **Modeling** – baseline (Linear Regression) vs. tree-based models (Random Forest, XGBoost, LightGBM).
6. **Evaluation** – MAE, RMSE, and R² on a held-out test set.
7. **Reporting & Dashboard** – communicate insights and model results to stakeholders.

## 📈 Evaluation Metrics

| Metric | Description |
|---|---|
| **MAE** | Average absolute error in minutes — easy to interpret for the business |
| **RMSE** | Penalizes large errors more heavily |
| **R²** | Proportion of variance in delivery time explained by the model |

## 🏆 Results

_To be updated after modeling._

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | – | – | – |
| Random Forest | – | – | – |
| XGBoost | – | – | – |

## 📑 Report

The full analysis, insights, and business recommendations are available in the [`report/`](report/) folder.

## 📊 Dashboard

The interactive dashboard is available in the [`dashboard/`](dashboard/) folder.

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/SNSetyowati/ETA-Prediction-for-a-Food-Delivery-Company.git
cd ETA-Prediction-for-a-Food-Delivery-Company

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook
```

## 🛠️ Tools & Technologies

Python · Pandas · NumPy · Scikit-learn · XGBoost · LightGBM · Matplotlib · Seaborn · Jupyter · Streamlit / Tableau

## 👤 Author

**SN Setyowati**
- GitHub: [@SNSetyowati](https://github.com/SNSetyowati)
