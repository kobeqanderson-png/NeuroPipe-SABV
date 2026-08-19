"""
Page 5: Linear Regression Modeling
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.branding import apply_subtle_branding
except ModuleNotFoundError:
    def apply_subtle_branding(*args, **kwargs):
        return None
from src.navigation import apply_global_chrome, render_top_navigation

st.set_page_config(page_title="NeuroPipe-SABV | Regression", page_icon=None, layout="wide")

apply_global_chrome()
render_top_navigation("Regression")

st.title("Linear Regression Modeling")

if st.session_state.df_processed is None:
    st.warning("No processed data available. Please run the **Process Data** pipeline first.")
    st.stop()

df_processed = st.session_state.df_processed
numeric_cols = df_processed.select_dtypes(include=['number']).columns.tolist()

st.markdown("""
Build linear regression models to understand relationships between variables in your data.
""")

st.divider()

def render_branded_figure(fig) -> None:
    """Render figure after applying subtle attribution mark."""
    apply_subtle_branding(
        fig,
        enabled=st.session_state.get("branding_enabled", False),
        text_alpha=0.02,
        logo_alpha=0.03,
    )
    st.pyplot(fig)

if len(numeric_cols) < 2:
    st.warning("Linear regression requires at least two numeric columns.")
    st.stop()

# Model configuration
st.header("Model Configuration")

reg_col1, reg_col2 = st.columns(2)

with reg_col1:
    target_col = st.selectbox(
        "Target variable (Y)",
        numeric_cols,
        key="reg_target",
    )

with reg_col2:
    feature_candidates = [c for c in numeric_cols if c != target_col]
    default_features = feature_candidates[: min(3, len(feature_candidates))]
    feature_cols = st.multiselect(
        "Feature variables (X)",
        feature_candidates,
        default=default_features,
        key="reg_features",
    )

st.divider()

# Model hyperparameters
st.header("Model Parameters")

model_col1, model_col2, model_col3 = st.columns(3)
with model_col1:
    test_size = st.slider("Test split ratio", min_value=0.1, max_value=0.4, value=0.2, step=0.05)
with model_col2:
    random_state = st.number_input("Random state", min_value=0, value=42, step=1)
with model_col3:
    fit_intercept = st.checkbox("Fit intercept", value=True)

st.divider()

# Polynomial features
st.header("Feature Engineering")

poly_col1, poly_col2 = st.columns(2)
with poly_col1:
    use_poly = st.checkbox("Add polynomial features", value=False, key="use_poly_features")
with poly_col2:
    poly_degree = st.slider("Polynomial degree", 2, 4, 2, disabled=not use_poly) if use_poly else 2

st.divider()

if st.button("Run Linear Regression", type="primary", use_container_width=True):
    if not feature_cols:
        st.warning("Select at least one feature variable.")
    else:
        with st.spinner("Training model..."):
            try:
                model_df = df_processed[[target_col] + feature_cols].dropna()

                if len(model_df) < 10:
                    st.warning("Not enough complete rows for a stable train/test split. Need at least 10 rows.")
                else:
                    X = model_df[feature_cols].copy()
                    y = model_df[target_col]

                    if use_poly:
                        for col in feature_cols:
                            for d in range(2, poly_degree + 1):
                                X[f"{col}_pow{d}"] = np.power(X[col], d)

                    X_train, X_test, y_train, y_test = train_test_split(
                        X,
                        y,
                        test_size=test_size,
                        random_state=int(random_state),
                    )

                    model = LinearRegression(fit_intercept=fit_intercept)
                    model.fit(X_train, y_train)
                    y_pred_train = model.predict(X_train)
                    y_pred_test = model.predict(X_test)

                    mae = mean_absolute_error(y_test, y_pred_test)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
                    r2 = r2_score(y_test, y_pred_test)
                    train_r2 = r2_score(y_train, y_pred_train)

                    st.success("Model trained successfully!")
                    
                    st.divider()
                    st.subheader("Model Performance")
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    with metric_col1:
                        st.metric("R² (Test)", f"{r2:.4f}")
                    with metric_col2:
                        st.metric("R² (Train)", f"{train_r2:.4f}")
                    with metric_col3:
                        st.metric("MAE", f"{mae:.4f}")
                    with metric_col4:
                        st.metric("RMSE", f"{rmse:.4f}")

                    coef_df = pd.DataFrame({
                        "Feature": X.columns,
                        "Coefficient": model.coef_,
                    }).sort_values("Coefficient", key=np.abs, ascending=False)

                    st.subheader("Model Coefficients")
                    st.dataframe(coef_df, use_container_width=True)
                    
                    st.caption(f"Intercept: {model.intercept_:.6f}")

                    st.divider()

                    # Visualizations
                    col_coef1, col_coef2 = st.columns(2)
                    with col_coef1:
                        st.subheader("Coefficient Importance")
                        fig, ax = plt.subplots(figsize=(8, 6))
                        colors = ["#22c55e" if x >= 0 else "#ef4444" for x in coef_df["Coefficient"]]
                        ax.barh(coef_df["Feature"], np.abs(coef_df["Coefficient"]), color=colors, edgecolor="black")
                        ax.set_xlabel("Absolute Coefficient Value")
                        ax.set_title("Feature Importance (|Coefficient|)")
                        ax.invert_yaxis()
                        render_branded_figure(fig)
                        plt.close()

                    with col_coef2:
                        st.subheader("Predicted vs Actual")
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.scatter(y_test, y_pred_test, alpha=0.7, edgecolor="black", color="#3498db")
                        y_min = min(float(np.min(y_test)), float(np.min(y_pred_test)))
                        y_max = max(float(np.max(y_test)), float(np.max(y_pred_test)))
                        ax.plot([y_min, y_max], [y_min, y_max], linestyle="--", color="gray", label="Perfect prediction")
                        ax.set_xlabel("Actual Values")
                        ax.set_ylabel("Predicted Values")
                        ax.set_title("Predicted vs Actual (Test Set)")
                        ax.legend()
                        render_branded_figure(fig)
                        plt.close()

                    st.subheader("Residual Analysis")
                    residuals = y_test - y_pred_test
                    res_col1, res_col2 = st.columns(2)
                    
                    with res_col1:
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.scatter(y_pred_test, residuals, alpha=0.7, edgecolor="black", color="#3498db")
                        ax.axhline(y=0, linestyle="--", color="gray")
                        ax.set_xlabel("Predicted Values")
                        ax.set_ylabel("Residuals")
                        ax.set_title("Residual Plot")
                        render_branded_figure(fig)
                        plt.close()

                    with res_col2:
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.hist(residuals, bins=15, edgecolor="black", alpha=0.7, color="#22c55e")
                        ax.set_xlabel("Residuals")
                        ax.set_ylabel("Frequency")
                        ax.set_title("Residual Distribution")
                        render_branded_figure(fig)
                        plt.close()

            except Exception as exc:
                st.error(f"Model training failed: {exc}")

st.info("Build models to understand relationships in your data and prepare for publication.")
