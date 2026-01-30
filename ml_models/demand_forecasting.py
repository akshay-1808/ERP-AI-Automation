import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from sklearn.linear_model import LinearRegression
from datetime import date

# Step 1:Connect to MySQL Database

USERNAME = "root"
PASSWORD = quote_plus("Saga@3351")  # handles @ # !
HOST = "localhost"
PORT = "3306"
DB_NAME = "erp_db"

engine = create_engine(
    f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
)

# Step 2: Extract Data from erp_db

query = """
SELECT 
    soi.product_id,
    so.order_date,
    soi.quantity
FROM Sales_Order_Items soi
JOIN Sales_Orders so
    ON soi.order_id = so.order_id
"""

sales_df = pd.read_sql(query, engine)


# Step 3: Feature Engineering (Time series)

sales_df["order_date"] = pd.to_datetime(sales_df["order_date"])
sales_df["year_month"] = sales_df["order_date"].dt.to_period("M")

monthly_demand = (
    sales_df
    .groupby(["product_id", "year_month"])
    .agg({"quantity": "sum"})
    .reset_index()
)

monthly_demand["year_month"] = monthly_demand["year_month"].dt.to_timestamp()


# Step 4: ML model (Linear regression)

forecasts = []

for product_id in monthly_demand["product_id"].unique():
    product_data = monthly_demand[
        monthly_demand["product_id"] == product_id
    ].copy()

    # Need at least 3 months to forecast
    if len(product_data) < 3:
        continue

    product_data = product_data.sort_values("year_month")
    product_data["time_index"] = range(len(product_data))

    X = product_data[["time_index"]]
    y = product_data["quantity"]

    model = LinearRegression()
    model.fit(X, y)

    next_time_index = [[product_data["time_index"].max() + 1]]
    predicted_demand = model.predict(next_time_index)[0]

    forecasts.append({
        "product_id": product_id,
        "predicted_demand": int(round(predicted_demand)),
        "forecast_date": date.today()
    })

forecast_df = pd.DataFrame(forecasts)


# Step 5: Save forecast back to erp_db

forecast_df.to_sql(
    "demand_forecast",
    con=engine,
    if_exists="append",
    index=False
)

print("✅ Demand forecasting completed and saved to ERP database")
