import numpy as np
import pandas as pd

HORIZON_DAYS = 30


def _daily_series(df, product):
    daily = (
        df[df["Product Name"] == product]
        .groupby("Date", as_index=False)["Quantity Sold"].sum()
        .rename(columns={"Date": "ds", "Quantity Sold": "y"})
    )
    full_range = pd.date_range(daily["ds"].min(), daily["ds"].max(), freq="D")
    return (
        daily.set_index("ds").reindex(full_range, fill_value=0)
        .rename_axis("ds").reset_index()
    )


def _prophet_forecast(daily):
    from prophet import Prophet

    model = Prophet(daily_seasonality=False)
    model.fit(daily)
    future = model.make_future_dataframe(periods=HORIZON_DAYS)
    return model.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def _linear_forecast(daily):
    from sklearn.linear_model import LinearRegression

    x = np.arange(len(daily)).reshape(-1, 1)
    y = daily["y"].to_numpy()
    model = LinearRegression().fit(x, y)
    resid_std = float(np.std(y - model.predict(x)))
    total = len(daily) + HORIZON_DAYS
    dates = pd.date_range(daily["ds"].min(), periods=total, freq="D")
    yhat = model.predict(np.arange(total).reshape(-1, 1))
    margin = 1.96 * resid_std
    return pd.DataFrame({
        "ds": dates,
        "yhat": yhat,
        "yhat_lower": yhat - margin,
        "yhat_upper": yhat + margin,
    })


def run_forecast(df):
    product_units = df.groupby("Product Name")["Quantity Sold"].sum()
    top_product = product_units.idxmax()
    daily = _daily_series(df, top_product)

    avg_monthly_sales = float(daily["y"].sum() / len(daily) * HORIZON_DAYS)

    try:
        forecast = _prophet_forecast(daily)
        prophet_used = True
    except ImportError:
        forecast = _linear_forecast(daily)
        prophet_used = False

    return {
        "forecast": forecast,
        "history": daily,
        "prophet_used": prophet_used,
        "top_product": top_product,
        "avg_monthly_sales": avg_monthly_sales,
    }


def summarize_forecast(result):
    history_end = result["history"]["ds"].max()
    future = result["forecast"][result["forecast"]["ds"] > history_end]
    total = float(future["yhat"].clip(lower=0).sum())
    half_width = (future["yhat_upper"] - future["yhat_lower"]) / 2
    spread = float(np.sqrt((half_width ** 2).sum()))
    return {"total": total, "low": max(total - spread, 0.0), "high": total + spread}
