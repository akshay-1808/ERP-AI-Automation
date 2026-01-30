import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from sklearn.preprocessing import MinMaxScaler
from datetime import date

# DATABASE CONNECTION
USERNAME = "root"
PASSWORD = quote_plus("Saga@3351")
HOST = "localhost"
PORT = "3306"
DB_NAME = "erp_db"

engine = create_engine(
    f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
)

# 1. LOAD SUPPLIER PERFORMANCE DATA

query = """
SELECT
    supplier_id,
    avg_delivery_delay_days,
    defect_rate,
    cost_index
FROM Suppliers
"""

df = pd.read_sql(query, engine)

if df.empty:
    raise Exception("❌ No supplier data found")

# 2. NORMALIZE METRICS
scaler = MinMaxScaler()

df[[
    "delivery_score",
    "quality_score",
    "cost_score"
]] = scaler.fit_transform(df[[
    "avg_delivery_delay_days",
    "defect_rate",
    "cost_index"
]])

# Invert scores so higher = better
df["delivery_score"] = 1 - df["delivery_score"]
df["quality_score"] = 1 - df["quality_score"]
df["cost_score"] = 1 - df["cost_score"]


# 3. FINAL SUPPLIER SCORE
df["supplier_score"] = (
    0.4 * df["cost_score"]
    + 0.3 * df["delivery_score"]
    + 0.3 * df["quality_score"]
)

df["score_date"] = date.today()

# 4. SAVE SCORES
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

print("✅ Supplier scoring completed successfully")
