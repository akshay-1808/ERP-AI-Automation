import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from sklearn.preprocessing import MinMaxScaler
from datetime import date

# ===============================
# DATABASE CONNECTION
# ===============================
USERNAME = "root"
PASSWORD = quote_plus("Saga@3351")
HOST = "localhost"
PORT = "3306"
DB_NAME = ("erp_db")

engine = create_engine(
    f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
)

# ===============================
# 1. DELIVERY PERFORMANCE (PO LEVEL)
# ===============================
delivery_query = """
SELECT
    supplier_id,
    DATEDIFF(actual_delivery_date, expected_delivery_date) AS delivery_delay
FROM Purchase_Orders
WHERE actual_delivery_date IS NOT NULL
"""

delivery_df = pd.read_sql(delivery_query, engine)

delivery_perf = (
    delivery_df
    .groupby("supplier_id", as_index=False)
    .agg(avg_delivery_delay_days=("delivery_delay", "mean"))
)

# ===============================
# 2. COST PERFORMANCE (PO ITEM LEVEL)
# ===============================
cost_query = """
SELECT
    po.supplier_id,
    poi.unit_price
FROM Purchase_Order_Items poi
JOIN Purchase_Orders po
    ON poi.purchase_order_id = po.purchase_order_id
"""

cost_df = pd.read_sql(cost_query, engine)

cost_perf = (
    cost_df
    .groupby("supplier_id", as_index=False)
    .agg(avg_unit_cost=("unit_price", "mean"))
)

# ===============================
# 3. MERGE METRICS
# ===============================
df = delivery_perf.merge(cost_perf, on="supplier_id", how="inner")

if df.empty:
    raise Exception("❌ Not enough data to calculate supplier scores")

# ===============================
# 4. NORMALIZE (LOWER IS BETTER)
# ===============================
scaler = MinMaxScaler()

df[["delivery_score", "cost_score"]] = scaler.fit_transform(
    df[["avg_delivery_delay_days", "avg_unit_cost"]]
)

# invert so higher = better
df["delivery_score"] = 1 - df["delivery_score"]
df["cost_score"] = 1 - df["cost_score"]

# ===============================
# 5. FINAL SUPPLIER SCORE
# ===============================
df["supplier_score"] = (
    0.6 * df["delivery_score"] +
    0.4 * df["cost_score"]
)

df["score_date"] = date.today()

# ===============================
# 6. SAVE SCORES
# ===============================
df[[
    "supplier_id",
    "supplier_score",
    "score_date"
]].to_sql(
    "Supplier_Scores",
    con=engine,
    if_exists="append",
    index=False
)

print("✅ Supplier scoring completed using PO history")
