from datetime import timedelta
from io import BytesIO
from pathlib import Path

import streamlit as st

import charts
from analytics import build_insights
from components import (callout, empty_state, filter_chips, highlight_card, insights_panel,
                        kpi_card, page_header, record_count, section_title, sidebar_brand,
                        sidebar_footer, sidebar_label, skeleton)
from data_loader import apply_filters, load_data
from forecasting import HORIZON_DAYS, run_forecast, summarize_forecast
from theme import CURRENCY, fmt_compact, inject_css

DATA_PATH = Path(__file__).parent / "jewellery_sales_data.csv"

st.set_page_config(page_title="Jewellery Sales Dashboard", page_icon="💎", layout="wide")
inject_css()


@st.cache_data
def get_data(path):
    return load_data(path)


@st.cache_data(show_spinner=False)
def get_forecast(df):
    return run_forecast(df)


@st.cache_data(show_spinner=False)
def to_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()


def pct_change(current, previous):
    return (current - previous) / previous * 100 if previous else None


def share(part, whole):
    return part / whole * 100 if whole else 0


def show(fig, key):
    st.plotly_chart(fig, width="stretch", theme=None, key=key)


with st.spinner("Loading data..."):
    df = get_data(str(DATA_PATH))

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
all_stores = sorted(df["Store Name"].unique())
all_people = sorted(df["Salesperson Name"].unique())
all_products = sorted(df["Product Name"].unique())
st.session_state.setdefault("filter_version", 0)


def reset_filters():
    st.session_state["filter_version"] += 1


version = st.session_state["filter_version"]

PRESETS = ["30D", "90D", "All"]


def preset_range(preset):
    if preset == "30D":
        return max(min_date, max_date - timedelta(days=29)), max_date
    if preset == "90D":
        return max(min_date, max_date - timedelta(days=89)), max_date
    return min_date, max_date

with st.sidebar:
    sidebar_brand()
    chips = st.empty()
    sidebar_label("Filters")
    with st.expander(":material/calendar_month: Period", expanded=True):
        preset = st.segmented_control("Quick range", PRESETS, default="All", required=True,
                                      width="stretch", key=f"f_preset_{version}")
        date_range = st.date_input("Date range", value=preset_range(preset),
                                   min_value=min_date, max_value=max_date,
                                   key=f"f_dates_{version}_{preset}")
    with st.expander(":material/storefront: Stores"):
        stores = st.multiselect("Stores", all_stores, default=all_stores,
                                key=f"f_stores_{version}", label_visibility="collapsed")
    with st.expander(":material/badge: Salespeople"):
        people = st.multiselect("Salespeople", all_people, default=all_people,
                                key=f"f_people_{version}", label_visibility="collapsed")
    with st.expander(":material/diamond: Products"):
        products = st.multiselect("Products", all_products, default=all_products,
                                  key=f"f_products_{version}", label_visibility="collapsed")
    st.button("Reset filters", icon=":material/restart_alt:", on_click=reset_filters,
              width="stretch")
    counter = st.empty()
    sidebar_footer(DATA_PATH.name, f"{max_date:%d %b %Y}")

if len(date_range) != 2:
    st.info("Select both a start and an end date.")
    st.stop()

with chips:
    filter_chips([
        (f"{date_range[0]:%d %b} – {date_range[1]:%d %b %Y}",
         tuple(date_range) != (min_date, max_date)),
        (f"{len(stores)}/{len(all_stores)} stores", len(stores) != len(all_stores)),
        (f"{len(people)}/{len(all_people)} people", len(people) != len(all_people)),
        (f"{len(products)}/{len(all_products)} products", len(products) != len(all_products)),
    ])
filtered_df = apply_filters(df, date_range, stores, people, products)
with counter:
    record_count(len(filtered_df), len(df))
if filtered_df.empty:
    empty_state("No data matches these filters",
                "Widen the date range or reselect stores, people or products.")
    st.button("Reset filters", icon=":material/restart_alt:", on_click=reset_filters,
              key="reset_empty")
    st.stop()

start, end = date_range
bounds = (start, end)
page_header("Sales Performance",
            f"Reporting period {start:%d %b %Y} – {end:%d %b %Y}",
            f"{len(filtered_df):,} transactions · data through {max_date:%d %b %Y}")

tab_overview, tab_stores, tab_people, tab_products, tab_forecast, tab_data = st.tabs([
    ":material/dashboard: Overview", ":material/storefront: Stores",
    ":material/groups: Salespeople", ":material/diamond: Products",
    ":material/query_stats: Forecast", ":material/table_view: Data"])

with tab_overview:
    kpis = charts.kpi_metrics(filtered_df)
    span = (end - start).days + 1
    prev_start, prev_end = start - timedelta(days=span), start - timedelta(days=1)
    has_prev = prev_start >= min_date
    deltas = dict.fromkeys(("revenue", "units", "avg", "tx"))
    if has_prev:
        prev = apply_filters(df, (prev_start, prev_end), stores, people, products)
        prev_rev = prev["Total Sale Amount"].sum()
        prev_avg = prev_rev / len(prev) if len(prev) else 0
        deltas = {
            "revenue": pct_change(kpis["total_revenue"], prev_rev),
            "units": pct_change(kpis["total_units"], prev["Quantity Sold"].sum()),
            "avg": pct_change(kpis["avg_transaction"], prev_avg),
            "tx": pct_change(kpis["transactions"], len(prev)),
        }

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("revenue", "Total Revenue", f"{CURRENCY} {fmt_compact(kpis['total_revenue'])}",
                 f"{CURRENCY} {kpis['total_revenue']:,.0f}", deltas["revenue"], 0.0)
    with c2:
        kpi_card("units", "Units Sold", f"{kpis['total_units']:,.0f}",
                 f"{kpis['total_units'] / max(kpis['transactions'], 1):.2f} units per sale",
                 deltas["units"], 0.05)
    with c3:
        kpi_card("bag", "Avg Transaction Value", f"{CURRENCY} {kpis['avg_transaction']:,.0f}",
                 "revenue per transaction", deltas["avg"], 0.1)
    with c4:
        kpi_card("activity", "Transactions", f"{kpis['transactions']:,}",
                 f"across {filtered_df['Store Name'].nunique()} stores", deltas["tx"], 0.15)
    if has_prev:
        st.caption(f"Change vs previous {span} days "
                   f"({prev_start:%d %b} – {prev_end:%d %b %Y}), same filters.")
    else:
        st.caption("No earlier period in the data to compare against.")

    h1, h2, h3 = st.columns(3)
    with h1:
        highlight_card("store", "Top store", kpis["best_store"],
                       f"{CURRENCY} {fmt_compact(kpis['best_store_revenue'])} · "
                       f"{share(kpis['best_store_revenue'], kpis['total_revenue']):.1f}% of revenue",
                       share(kpis["best_store_revenue"], kpis["total_revenue"]), 0.2)
    with h2:
        highlight_card("gem", "Top product", kpis["top_product"],
                       f"{kpis['top_product_units']:,.0f} units · "
                       f"{share(kpis['top_product_units'], kpis['total_units']):.1f}% of volume",
                       share(kpis["top_product_units"], kpis["total_units"]), 0.25)
    with h3:
        highlight_card("users", "Top salesperson", kpis["top_salesperson"],
                       f"{CURRENCY} {fmt_compact(kpis['top_salesperson_revenue'])} · "
                       f"{share(kpis['top_salesperson_revenue'], kpis['total_revenue']):.1f}% "
                       "of revenue",
                       share(kpis["top_salesperson_revenue"], kpis["total_revenue"]), 0.3)

    insights = build_insights(filtered_df, bounds)
    if insights:
        insights_panel(insights)

    section_title("Revenue trend", "Monthly revenue; dotted line marks partial months")
    left, right = st.columns([2, 1])
    with left:
        show(charts.revenue_trend_chart(filtered_df, bounds), "trend")
    with right:
        show(charts.store_share_chart(filtered_df), "share")

    section_title("Product mix and timing")
    left, right = st.columns([3, 2])
    with left:
        show(charts.product_pareto_chart(filtered_df), "pareto")
    with right:
        show(charts.weekday_chart(filtered_df), "weekday")

with tab_stores:
    section_title("Store analysis", "Revenue and unit volume per store")
    left, right = st.columns(2)
    with left:
        show(charts.store_revenue_chart(filtered_df), "st_rev")
    with right:
        show(charts.store_units_chart(filtered_df), "st_units")
    section_title("Store summary")
    store_summary = charts.store_table(filtered_df)
    st.dataframe(
        store_summary, width="stretch", hide_index=True,
        column_config={
            "Total Units Sold": st.column_config.NumberColumn(format="localized"),
            "Total Revenue": st.column_config.ProgressColumn(
                format="localized", min_value=0,
                max_value=float(store_summary["Total Revenue"].max())),
        })

with tab_people:
    section_title("Salesperson analysis", "Top 10 salespeople by revenue")
    show(charts.salesperson_chart(filtered_df), "people")
    section_title("Salesperson ranking", "All salespeople ranked by revenue")
    ranking = charts.salesperson_table(filtered_df)
    st.dataframe(
        ranking, width="stretch", hide_index=True,
        column_config={
            "Units Sold": st.column_config.NumberColumn(format="localized"),
            "Total Revenue": st.column_config.NumberColumn(format="localized"),
            "Avg Sale": st.column_config.NumberColumn(format="localized"),
            "Revenue Share (%)": st.column_config.ProgressColumn(
                format="%.1f%%", min_value=0, max_value=float(ranking["Revenue Share (%)"].max())),
        })

with tab_products:
    section_title("Product analysis", "Volume and revenue per product")
    left, right = st.columns(2)
    with left:
        show(charts.product_units_chart(filtered_df), "pr_units")
    with right:
        show(charts.product_revenue_chart(filtered_df), "pr_rev")
    section_title("Where each product sells", "Revenue by store and product")
    show(charts.store_product_heatmap(filtered_df), "heatmap")

with tab_forecast:
    section_title("Sales forecast", f"Next {HORIZON_DAYS} days, by product")
    ranked = filtered_df.groupby("Product Name")["Quantity Sold"].sum().sort_values(ascending=False)
    product = st.selectbox("Product to forecast", list(ranked.index), index=0)
    product_df = filtered_df[filtered_df["Product Name"] == product]
    history_days = (product_df["Date"].max() - product_df["Date"].min()).days + 1
    if history_days < 30:
        st.info(f"Not enough history to forecast {product}: {history_days} days of sales in "
                "the selected period (at least 30 needed). Widen the date range.")
    else:
        loader = st.empty()
        with loader:
            skeleton()
        result = get_forecast(product_df)
        loader.empty()
        summary = summarize_forecast(result)
        baseline = result["avg_monthly_sales"]

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            kpi_card("revenue", f"Predicted units ({HORIZON_DAYS}d)", f"{summary['total']:,.0f}",
                     result["top_product"], delay=0.0)
        with f2:
            kpi_card("units", "Low estimate", f"{summary['low']:,.0f}",
                     "lower bound (combined)", delay=0.05)
        with f3:
            kpi_card("units", "High estimate", f"{summary['high']:,.0f}",
                     "upper bound (combined)", delay=0.1)
        with f4:
            kpi_card("activity", "Historical baseline", f"{baseline:,.0f}",
                     f"average units per {HORIZON_DAYS} days", delay=0.15)

        gap = pct_change(summary["total"], baseline)
        if gap is not None and gap > 0:
            callout("Recommendation: increase stock",
                    f"Projected demand of {summary['total']:,.0f} units over the next "
                    f"{HORIZON_DAYS} days is {gap:.0f}% above the historical baseline of "
                    f"{baseline:,.0f} units for {product}. Plan additional inventory.", "pos")
        else:
            below = f"{abs(gap):.0f}% below" if gap is not None else "in line with"
            callout("Recommendation: maintain current stock",
                    f"Projected demand of {summary['total']:,.0f} units over the next "
                    f"{HORIZON_DAYS} days is {below} the historical baseline of "
                    f"{baseline:,.0f} units for {product}. No stock increase is indicated.",
                    "neu")
        show(charts.forecast_chart(result), "forecast")
        if not result["prophet_used"]:
            st.warning("Prophet is unavailable, so this forecast uses a LinearRegression "
                       "fallback (no seasonality; the interval is based on residual spread).")

with tab_data:
    section_title("Raw data", f"{len(filtered_df):,} records matching the current filters")
    d1, d2, _ = st.columns([1, 1, 4])
    with d1:
        st.download_button("Download CSV", filtered_df.to_csv(index=False).encode("utf-8"),
                           "jewellery_sales_filtered.csv", "text/csv",
                           icon=":material/download:", width="stretch")
    with d2:
        st.download_button(
            "Download Excel", to_excel(filtered_df), "jewellery_sales_filtered.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:", width="stretch")
    st.dataframe(filtered_df, width="stretch", hide_index=True)
