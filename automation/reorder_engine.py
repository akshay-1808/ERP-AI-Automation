import pandas as pd
from datetime import date
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# DATABASE CONNECTION

USERNAME = "root"
PASSWORD = quote_plus("Saga@3351")
HOST = "localhost"
PORT = "3306"
DB_NAME = "erp_db"

engine = create_engine(
    f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
)

# 1. FETCH INVENTORY + DEMAND
query = """
SELECT
    i.product_id,
    i.current_stock,
    d.predicted_demand
FROM Inventory i
JOIN Demand_Forecast d
    ON i.product_id = d.product_id
"""

df = pd.read_sql(query, engine)

# ===============================
# 2. REORDER CALCULATION
# ===============================
df["safety_stock"] = (0.2 * df["predicted_demand"]).round().astype(int)
df["required_stock"] = df["predicted_demand"] + df["safety_stock"]
df["reorder_quantity"] = df["required_stock"] - df["current_stock"]
df["reorder_quantity"] = df["reorder_quantity"].clip(lower=0)

reorder_df = df[df["reorder_quantity"] > 0].copy()

if reorder_df.empty:
    print("ℹ️ No reorder required today")
    exit()

reorder_df["recommendation_date"] = date.today()

# 3. SAVE REORDER RECOMMENDATIONS
reorder_df[[
    "product_id",
    "current_stock",
    "predicted_demand",
    "reorder_quantity",
    "recommendation_date"
]].to_sql(
    "reorder_recommendations",
    con=engine,
    if_exists="append",
    index=False
)

print("✅ Reorder recommendations saved")

# 4. SELECT DEFAULT SUPPLIER
supplier_query = """
SELECT supplier_id
FROM Suppliers
ORDER BY supplier_id
LIMIT 1
"""

supplier_df = pd.read_sql(supplier_query, engine)

if supplier_df.empty:
    raise Exception("❌ No suppliers found")

supplier_id = int(supplier_df.iloc[0]["supplier_id"])

# 5. CREATE PURCHASE ORDER HEADER
with engine.begin() as conn:
    result = conn.execute(
        text("""
            INSERT INTO purchase_orders (supplier_id, order_date, status)
            VALUES (:supplier_id, :order_date, 'CREATED')
        """),
        {
            "supplier_id": supplier_id,
            "order_date": date.today()
        }
    )
    po_id = result.lastrowid

print(f"✅ Purchase Order {po_id} created")

# 6. CREATE PURCHASE ORDER ITEMS
po_items = []

for _, row in reorder_df.iterrows():
    po_items.append({
        "po_id": po_id,
        "product_id": int(row["product_id"]),
        "order_quantity": int(row["reorder_quantity"])
    })

po_items_df = pd.DataFrame(po_items)

po_items_df.to_sql(
    "purchase_order_items",
    con=engine,
    if_exists="append",
    index=False
)

print("✅ Purchase Order items inserted")

# DONE
print("🎯 Reorder → Purchase Order automation completed successfully")
