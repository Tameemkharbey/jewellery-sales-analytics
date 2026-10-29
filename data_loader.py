import pandas as pd

NUMERIC_COLUMNS = ["Quantity Sold", "Unit Price", "Total Sale Amount"]


def load_data(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df.reset_index(drop=True)


def apply_filters(df, date_range, stores, salespeople, products):
    start, end = date_range
    mask = (
        (df["Date"] >= pd.Timestamp(start))
        & (df["Date"] <= pd.Timestamp(end))
        & df["Store Name"].isin(stores)
        & df["Salesperson Name"].isin(salespeople)
        & df["Product Name"].isin(products)
    )
    return df[mask]
