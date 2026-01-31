import requests
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# ===============================
# DATABASE CONFIG (STRICT SCHEMA)
# ===============================
DB_USER = "root"
DB_PASSWORD = quote_plus("Saga@3351")
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "erp_db"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ===============================
# OLLAMA CONFIG
# ===============================
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "mistral"

# ===============================
# INTENT DETECTION (SAFE)
# ===============================
def detect_intent(query: str):
    q = query.lower()

    if "low stock" in q or "reorder" in q:
        return "REORDER_STATUS"

    if "purchase order" in q or "po" in q:
        if any(char.isdigit() for char in q):
            return "PO_EXPLANATION"
        return "PURCHASE_ORDERS"

    if "supplier" in q:
        return "SUPPLIERS"

    return "UNKNOWN"

# ===============================
# ERP DATA QUERIES (SCHEMA-ACCURATE)
# ===============================
def fetch_reorder_status():
    query = """
    SELECT
        rr.product_id,
        p.product_name,
        rr.current_stock,
        rr.predicted_demand,
        rr.reorder_quantity,
        rr.recommendation_date
    FROM reorder_recommendations rr
    JOIN products p
        ON rr.product_id = p.product_id
    """
    return pd.read_sql(query, engine)

def fetch_purchase_orders():
    query = """
    SELECT
        po.po_id,
        s.supplier_name,
        po.order_date,
        po.expected_delivery,
        po.total_amount,
        po.po_status
    FROM purchase_orders po
    LEFT JOIN suppliers s
        ON po.supplier_id = s.supplier_id
    ORDER BY po.order_date DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

def explain_po(po_id):
    query = """
    SELECT
        po.po_id,
        p.product_name,
        poi.order_quantity,
        po.po_status
    FROM purchase_orders po
    JOIN purchase_order_items poi
        ON po.po_id = poi.po_id
    JOIN products p
        ON poi.product_id = p.product_id
    WHERE po.po_id = :po_id
    """
    return pd.read_sql(text(query), engine, params={"po_id": po_id})

def fetch_suppliers():
    query = """
    SELECT
        supplier_id,
        supplier_name,
        rating,
        avg_delivery_days
    FROM suppliers
    """
    return pd.read_sql(query, engine)

# ===============================
# LLAMA EXPLANATION
# ===============================
def llama_explain(user_query, df):
    prompt = f"""
You are an ERP assistant.

User question:
{user_query}

ERP data (sample rows):
{df.head(5).to_string(index=False)}

Explain the result clearly in business-friendly language.
"""

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }

    res = requests.post(OLLAMA_URL, json=payload)

    if res.status_code != 200:
        return f"Ollama error: HTTP {res.status_code} → {res.text}"

    data = res.json()

    if "response" not in data:
        return f"Ollama error response: {data}"

    return data["response"]



# ===============================
# MAIN CHAT
# ===============================
def chat(user_query):
    intent = detect_intent(user_query)

    if intent == "REORDER_STATUS":
        df = fetch_reorder_status()

    elif intent == "PURCHASE_ORDERS":
        df = fetch_purchase_orders()

    elif intent == "PO_EXPLANATION":
        po_id = int("".join(filter(str.isdigit, user_query)))
        df = explain_po(po_id)

    elif intent == "SUPPLIERS":
        df = fetch_suppliers()

    else:
        return "I can answer only ERP-related questions (reorders, POs, suppliers)."

    if df.empty:
        return "No relevant data found."


    print("➡️ Received user query:", user_query)

    # sql_query = generate_sql(user_query)
    # print("✅ SQL generated:", sql_query)
    #
    # result = run_query(sql_query)
    # print("✅ DB query executed")
    #
    # answer = ask_llm(user_query, result)
    # print("✅ LLM responded")


    return llama_explain(user_query, df)

# ===============================
# CLI
# ===============================
if __name__ == "__main__":
    print("🧠 ERP LLaMA Assistant (Schema-Safe) — type 'exit' to quit\n")

    while True:
        q = input("Ask ERP: ")
        if q.lower() == "exit":
            break
        print("\n", chat(q), "\n")
