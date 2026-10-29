# Jewellery Sales Analytics

Executive sales dashboard built with Streamlit, Plotly and Prophet.

## Features
- Revenue, units, average transaction value and period-over-period change
- Store, salesperson and product analysis with rankings and heatmap
- 30-day demand forecast per product with stock recommendation
- Quick-range and multi-select filters, CSV and Excel export

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

Data is read from `jewellery_sales_data.csv` (columns: Date, Store Name, Salesperson Name, Product Name, Quantity Sold, Unit Price, Total Sale Amount).
