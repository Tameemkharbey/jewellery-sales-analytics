import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analytics import monthly_revenue
from theme import (ACCENT, BLUE, CATEGORICAL, CURRENCY, MUTED, SLATE, SURFACE, TEXT,
                   fmt_compact)

REVENUE_HOVER = f"%{{y}}<br>{CURRENCY} %{{x:,.0f}}<extra></extra>"
UNITS_HOVER = "%{y}<br>%{x:,.0f} units<extra></extra>"
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _hbar(data, x, y, title, hover):
    data = data.sort_values(x).assign(Label=lambda d: d[x].map(fmt_compact))
    data["Rank"] = ["Other"] * (len(data) - 1) + ["Top"]
    fig = px.bar(data, x=x, y=y, orientation="h", text="Label", title=title, color="Rank",
                 color_discrete_map={"Top": ACCENT, "Other": SLATE})
    fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate=hover,
                      marker_cornerradius=4, textfont_color=MUTED)
    fig.update_xaxes(range=[0, data[x].max() * 1.2], title=None)
    fig.update_yaxes(title=None, categoryorder="array", categoryarray=data[y].tolist())
    fig.update_layout(showlegend=False, height=max(300, 40 * len(data) + 96))
    return fig


def kpi_metrics(df):
    if df.empty:
        return {"total_revenue": 0, "total_units": 0, "best_store": "N/A", "top_product": "N/A",
                "best_store_revenue": 0, "top_product_units": 0, "transactions": 0,
                "avg_transaction": 0, "top_salesperson": "N/A", "top_salesperson_revenue": 0}
    store_rev = df.groupby("Store Name")["Total Sale Amount"].sum()
    product_units = df.groupby("Product Name")["Quantity Sold"].sum()
    people_rev = df.groupby("Salesperson Name")["Total Sale Amount"].sum()
    revenue = df["Total Sale Amount"].sum()
    return {
        "total_revenue": revenue,
        "total_units": df["Quantity Sold"].sum(),
        "best_store": store_rev.idxmax(),
        "top_product": product_units.idxmax(),
        "best_store_revenue": store_rev.max(),
        "top_product_units": product_units.max(),
        "transactions": len(df),
        "avg_transaction": revenue / len(df),
        "top_salesperson": people_rev.idxmax(),
        "top_salesperson_revenue": people_rev.max(),
    }


def revenue_trend_chart(df, bounds=None):
    monthly = monthly_revenue(df, bounds)
    revenue, complete = monthly["Total Sale Amount"], monthly["Complete"]
    partial = ~complete
    near_partial = partial | ~complete.shift(1, fill_value=True) | ~complete.shift(-1, fill_value=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Date"], y=revenue.where(near_partial), mode="lines", name="Partial month",
        line=dict(color=ACCENT, width=2, dash="dot"), hoverinfo="skip",
        showlegend=bool(partial.any())))
    fig.add_trace(go.Scatter(
        x=monthly["Date"], y=revenue.where(complete), mode="lines+markers", name="Revenue",
        line=dict(color=ACCENT, width=2.5), marker=dict(size=7, color=ACCENT),
        fill="tozeroy", fillcolor="rgba(201,162,75,0.08)",
        hovertemplate=f"%{{x|%b %Y}}<br>{CURRENCY} %{{y:,.0f}}<extra></extra>"))
    if partial.any():
        fig.add_trace(go.Scatter(
            x=monthly.loc[partial, "Date"], y=revenue[partial], mode="markers", showlegend=False,
            marker=dict(size=9, symbol="circle-open", color=ACCENT, line=dict(width=2)),
            hovertemplate=f"%{{x|%b %Y}} (partial month)<br>{CURRENCY} %{{y:,.0f}}<extra></extra>"))
    if complete.any():
        peak = revenue.where(complete).idxmax()
        fig.add_annotation(
            x=monthly.loc[peak, "Date"], y=revenue[peak], ax=0, ay=-34, showarrow=True,
            arrowhead=0, arrowcolor=MUTED, bgcolor=SURFACE, bordercolor=ACCENT,
            font=dict(color=TEXT, size=11),
            text=f"Peak {CURRENCY} {fmt_compact(revenue[peak])}")
    fig.update_layout(title=f"Monthly Revenue ({CURRENCY})",
                      legend=dict(orientation="h", y=1.14, x=1, xanchor="right"))
    fig.update_xaxes(title=None, tickformat="%b %Y",
                     range=[monthly["Date"].min() - pd.Timedelta(days=12),
                            monthly["Date"].max() + pd.Timedelta(days=12)])
    fig.update_yaxes(title=None, range=[0, revenue.max() * 1.28])
    return fig


def store_share_chart(df):
    data = df.groupby("Store Name", as_index=False)["Total Sale Amount"].sum()
    fig = px.pie(data, names="Store Name", values="Total Sale Amount", hole=0.62,
                 title="Revenue Share by Store", color_discrete_sequence=CATEGORICAL)
    fig.update_traces(textinfo="percent", sort=False, marker_line_color=SURFACE,
                      marker_line_width=2,
                      hovertemplate=f"%{{label}}<br>{CURRENCY} %{{value:,.0f}}<extra></extra>")
    fig.add_annotation(text=f"<b>{fmt_compact(data['Total Sale Amount'].sum())}</b><br>"
                            f"<span style='font-size:11px;color:{MUTED}'>{CURRENCY}</span>",
                       showarrow=False, font=dict(size=20, color=TEXT))
    fig.update_layout(legend=dict(orientation="h", y=-0.12, font=dict(size=11)), height=420)
    return fig


def product_pareto_chart(df):
    data = (df.groupby("Product Name", as_index=False)["Total Sale Amount"].sum()
            .sort_values("Total Sale Amount", ascending=False).reset_index(drop=True))
    data["Cumulative"] = data["Total Sale Amount"].cumsum() / data["Total Sale Amount"].sum() * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=data["Product Name"], y=data["Total Sale Amount"], name="Revenue",
        marker=dict(color=[ACCENT] + [SLATE] * (len(data) - 1), cornerradius=4),
        hovertemplate=f"%{{x}}<br>{CURRENCY} %{{y:,.0f}}<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=data["Product Name"], y=data["Cumulative"], name="Cumulative share", mode="lines+markers",
        line=dict(color=BLUE, width=2), marker=dict(size=6),
        hovertemplate="%{x}<br>%{y:.0f}% of revenue<extra></extra>"), secondary_y=True)
    fig.update_layout(title="Product Revenue and Cumulative Share",
                      legend=dict(orientation="h", y=1.14, x=1, xanchor="right"), height=420)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None, secondary_y=False)
    fig.update_yaxes(title=None, range=[0, 105], dtick=25, ticksuffix="%", showgrid=False, secondary_y=True)
    return fig


def weekday_chart(df):
    revenue = df.groupby(df["Date"].dt.dayofweek)["Total Sale Amount"].sum().reindex(
        range(7), fill_value=0)
    fig = go.Figure(go.Bar(
        x=WEEKDAYS, y=revenue.values, text=[fmt_compact(v) for v in revenue.values],
        textposition="outside", cliponaxis=False, textfont_color=MUTED,
        marker=dict(color=[ACCENT if v == revenue.max() else SLATE for v in revenue.values],
                    cornerradius=4),
        hovertemplate=f"%{{x}}<br>{CURRENCY} %{{y:,.0f}}<extra></extra>"))
    fig.update_layout(title="Revenue by Day of Week", height=420)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None, range=[0, revenue.max() * 1.18])
    return fig


def store_revenue_chart(df):
    data = df.groupby("Store Name", as_index=False)["Total Sale Amount"].sum()
    return _hbar(data, "Total Sale Amount", "Store Name", f"Revenue by Store ({CURRENCY})",
                 REVENUE_HOVER)


def store_units_chart(df):
    data = df.groupby("Store Name", as_index=False)["Quantity Sold"].sum()
    return _hbar(data, "Quantity Sold", "Store Name", "Units Sold by Store", UNITS_HOVER)


def store_table(df):
    return (
        df.groupby("Store Name", as_index=False)
        .agg(**{"Total Units Sold": ("Quantity Sold", "sum"),
                "Total Revenue": ("Total Sale Amount", "sum")})
        .sort_values("Total Revenue", ascending=False)
        .reset_index(drop=True)
    )


def salesperson_chart(df):
    data = (
        df.groupby("Salesperson Name", as_index=False)["Total Sale Amount"].sum()
        .nlargest(10, "Total Sale Amount")
    )
    return _hbar(data, "Total Sale Amount", "Salesperson Name",
                 f"Top 10 Salespeople by Revenue ({CURRENCY})", REVENUE_HOVER)


def salesperson_table(df):
    table = (
        df.groupby("Salesperson Name", as_index=False)
        .agg(Transactions=("Total Sale Amount", "size"),
             **{"Units Sold": ("Quantity Sold", "sum"),
                "Total Revenue": ("Total Sale Amount", "sum")})
        .sort_values("Total Revenue", ascending=False)
        .reset_index(drop=True)
    )
    table["Avg Sale"] = (table["Total Revenue"] / table["Transactions"]).round(0)
    table["Revenue Share (%)"] = (table["Total Revenue"] / table["Total Revenue"].sum() * 100).round(1)
    table.insert(0, "Rank", range(1, len(table) + 1))
    return table


def product_units_chart(df):
    data = df.groupby("Product Name", as_index=False)["Quantity Sold"].sum()
    return _hbar(data, "Quantity Sold", "Product Name", "Units Sold by Product", UNITS_HOVER)


def product_revenue_chart(df):
    data = df.groupby("Product Name", as_index=False)["Total Sale Amount"].sum()
    return _hbar(data, "Total Sale Amount", "Product Name", f"Revenue by Product ({CURRENCY})",
                 REVENUE_HOVER)


def store_product_heatmap(df):
    pivot = df.pivot_table(index="Store Name", columns="Product Name",
                           values="Total Sale Amount", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, aspect="auto", text_auto=".2s", title=f"Revenue by Store and Product ({CURRENCY})",
                    color_continuous_scale=[[0, SURFACE], [1, ACCENT]])
    fig.update_traces(hovertemplate=f"%{{y}}<br>%{{x}}<br>{CURRENCY} %{{z:,.0f}}<extra></extra>")
    fig.update_layout(coloraxis_showscale=False, height=max(300, 58 * len(pivot) + 130))
    fig.update_xaxes(title=None, side="top")
    fig.update_yaxes(title=None)
    return fig


def forecast_chart(result):
    history = result["history"].assign(ma7=lambda d: d["y"].rolling(7, min_periods=1).mean())
    forecast = result["forecast"]
    future = forecast[forecast["ds"] > history["ds"].max()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=future["ds"], y=future["yhat_upper"], mode="lines",
                             line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=future["ds"], y=future["yhat_lower"], mode="lines",
                             line=dict(width=0), fill="tonexty",
                             fillcolor="rgba(201,162,75,0.16)", name="Confidence interval",
                             hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=history["ds"], y=history["y"], mode="lines", name="Daily actual",
                             line=dict(color=BLUE, width=1), opacity=0.35,
                             hovertemplate="Daily actual: %{y:.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=history["ds"], y=history["ma7"], mode="lines",
                             name="7-day average", line=dict(color=BLUE, width=2.2),
                             hovertemplate="7-day average: %{y:.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=future["ds"], y=future["yhat"], mode="lines", name="Forecast",
                             line=dict(color=ACCENT, width=2.4, dash="dash"),
                             hovertemplate="Forecast: %{y:.1f}<extra></extra>"))
    fig.update_layout(title=f"{result['top_product']} - Daily Units Forecast",
                      hovermode="x unified", height=420,
                      legend=dict(orientation="h", y=1.14, x=1, xanchor="right"))
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Units")
    return fig
