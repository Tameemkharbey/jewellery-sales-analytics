import pandas as pd

from theme import CURRENCY, fmt_compact


def monthly_revenue(df, bounds=None):
    monthly = df.set_index("Date")["Total Sale Amount"].resample("MS").sum().reset_index()
    low, high = (pd.Timestamp(b) for b in (bounds or (df["Date"].min(), df["Date"].max())))
    month_end = monthly["Date"] + pd.offsets.MonthEnd(0)
    monthly["Complete"] = (monthly["Date"] >= low) & (month_end <= high)
    return monthly


def _pct(current, previous):
    return (current - previous) / previous * 100 if previous else None


def build_insights(df, bounds=None):
    insights = []

    monthly = monthly_revenue(df, bounds)
    full = monthly[monthly["Complete"]].reset_index(drop=True)
    if len(full) >= 2:
        peak = full.loc[full["Total Sale Amount"].idxmax()]
        change = _pct(full["Total Sale Amount"].iloc[-1], full["Total Sale Amount"].iloc[-2])
        if change is not None:
            direction = "above" if change >= 0 else "below"
            insights.append(
                f"Revenue peaked in {peak['Date']:%B %Y} at {CURRENCY} "
                f"{fmt_compact(peak['Total Sale Amount'])}. The latest full month "
                f"({full['Date'].iloc[-1]:%B}) is {abs(change):.1f}% {direction} the month before.")

    revenue = df.groupby("Product Name")["Total Sale Amount"].sum().sort_values(ascending=False)
    units = df.groupby("Product Name")["Quantity Sold"].sum().sort_values(ascending=False)
    if len(revenue) >= 3 and revenue.sum() > 0:
        share = revenue.head(3).sum() / revenue.sum() * 100
        insights.append(f"The top 3 products ({', '.join(revenue.head(3).index)}) generate "
                        f"{share:.0f}% of revenue.")
    if len(revenue) >= 2 and units.index[0] != revenue.index[0]:
        insights.append(
            f"{units.index[0]} leads on volume ({units.iloc[0]:,.0f} units), but "
            f"{revenue.index[0]} leads on revenue, so higher-priced pieces drive the top line.")

    stores = df.groupby("Store Name")["Total Sale Amount"].sum().sort_values(ascending=False)
    if len(stores) >= 2 and stores.iloc[-1] > 0:
        gap = (stores.iloc[0] - stores.iloc[-1]) / stores.iloc[-1] * 100
        if gap < 15:
            insights.append(f"Store performance is tightly grouped: {stores.index[0]} leads "
                            f"{stores.index[-1]} by only {gap:.1f}%.")
        else:
            insights.append(f"{stores.index[0]} leads {stores.index[-1]} by {gap:.1f}% in "
                            "revenue, a gap worth reviewing.")
    return insights
