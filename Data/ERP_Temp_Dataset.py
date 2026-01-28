import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

# ------------------ Products ------------------
products = []
fabric_types = ["Cotton", "Silk", "Denim", "Linen", "Polyester"]

for i in range(1, 51):
    products.append([
        i,
        f"Fabric_{i}",
        random.choice(fabric_types),
        round(random.uniform(100, 500), 2),
        random.randint(200, 500),
        random.randint(5, 15)
    ])

products_df = pd.DataFrame(products, columns=[
    "product_id", "product_name", "fabric_type",
    "unit_price", "reorder_level", "lead_time_days"
])

# ------------------ Suppliers ------------------
suppliers = []
for i in range(1, 21):
    suppliers.append([
        i,
        f"Supplier_{i}",
        round(random.uniform(3.0, 5.0), 2),
        random.randint(5, 12)
    ])

suppliers_df = pd.DataFrame(suppliers, columns=[
    "supplier_id", "supplier_name", "rating", "avg_delivery_days"
])

# ------------------ Customers ------------------
customers = []
regions = ["North", "South", "East", "West"]
for i in range(1, 101):
    customers.append([i, f"Customer_{i}", random.choice(regions)])

customers_df = pd.DataFrame(customers, columns=[
    "customer_id", "customer_name", "region"
])

# ------------------ Sales Orders ------------------
orders = []
order_items = []
start_date = datetime(2023, 1, 1)

order_id = 1
item_id = 1

for _ in range(20000):
    customer_id = random.randint(1, 100)
    order_date = start_date + timedelta(days=random.randint(0, 720))
    delivery_date = order_date + timedelta(days=random.randint(3, 10))

    orders.append([
        order_id,
        customer_id,
        order_date,
        delivery_date,
        0
    ])

    total_amount = 0
    for _ in range(random.randint(1, 4)):
        product_id = random.randint(1, 50)
        quantity = random.randint(10, 200)
        price = products_df.loc[products_df.product_id == product_id, "unit_price"].values[0]
        total_amount += quantity * price

        order_items.append([
            item_id,
            order_id,
            product_id,
            quantity
        ])
        item_id += 1

    orders[-1][4] = round(total_amount, 2)
    order_id += 1

orders_df = pd.DataFrame(orders, columns=[
    "order_id", "customer_id", "order_date",
    "delivery_date", "total_amount"
])

order_items_df = pd.DataFrame(order_items, columns=[
    "item_id", "order_id", "product_id", "quantity"
])

# ------------------ Inventory ------------------
inventory = []
for i in range(1, 51):
    inventory.append([
        i,
        i,
        random.randint(100, 1500),
        f"WH-{random.randint(1,3)}",
        datetime.now().date()
    ])

inventory_df = pd.DataFrame(inventory, columns=[
    "inventory_id", "product_id", "current_stock",
    "warehouse_location", "last_updated"
])

# ------------------ Production Batches ------------------
batches = []
for i in range(1, 15001):
    batches.append([
        i,
        random.randint(1, 50),
        start_date + timedelta(days=random.randint(0, 720)),
        random.randint(200, 1000),
        random.randint(0, 50)
    ])

batches_df = pd.DataFrame(batches, columns=[
    "batch_id", "product_id", "production_date",
    "quantity_produced", "defect_quantity"
])

# ------------------ Quality Reports ------------------
quality = []
for i in range(1, 15001):
    quality.append([
        i,
        i,
        start_date + timedelta(days=random.randint(0, 720)),
        round(random.uniform(70, 98), 2),
        random.choice(["OK", "Minor Issue", "Rejected"])
    ])

quality_df = pd.DataFrame(quality, columns=[
    "report_id", "batch_id", "inspection_date",
    "quality_score", "remarks"
])

# ------------------ Purchase Orders ------------------
pos = []
for i in range(1, 5001):
    supplier_id = random.randint(1, 20)
    order_date = start_date + timedelta(days=random.randint(0, 720))
    expected = order_date + timedelta(days=random.randint(5, 15))

    pos.append([
        i,
        supplier_id,
        order_date,
        expected,
        round(random.uniform(50000, 200000), 2),
        random.choice(["Completed", "Pending", "Delayed"])
    ])

pos_df = pd.DataFrame(pos, columns=[
    "po_id", "supplier_id", "order_date",
    "expected_delivery", "total_amount", "status"
])
pos_df["order_date"] = pd.to_datetime(pos_df["order_date"])


# ------------------ Invoices ------------------
invoices = []

for i in range(1, 5001):
    po_row = pos_df.loc[pos_df.po_id == i].iloc[0]
    po_amount = po_row["total_amount"]
    invoice_date = po_row["order_date"] + timedelta(days=5)

    mismatch = random.choice([0, 0, 0, 1])

    invoices.append([
        i,
        i,
        invoice_date,
        po_amount + random.uniform(-5000, 5000) if mismatch else po_amount,
        random.choice(["Paid", "Unpaid"])
    ])

invoices_df = pd.DataFrame(invoices, columns=[
    "invoice_id", "po_id", "invoice_date",
    "invoice_amount", "payment_status"
])


# ------------------ SAVE FILES ------------------
products_df.to_csv("Products.csv", index=False)
inventory_df.to_csv("Inventory.csv", index=False)
suppliers_df.to_csv("Suppliers.csv", index=False)
customers_df.to_csv("Customers.csv", index=False)
orders_df.to_csv("Sales_Orders.csv", index=False)
order_items_df.to_csv("Sales_Order_Items.csv", index=False)
batches_df.to_csv("Production_Batches.csv", index=False)
quality_df.to_csv("Quality_Reports.csv", index=False)
pos_df.to_csv("Purchase_Orders.csv", index=False)
invoices_df.to_csv("Invoices.csv", index=False)

print("✅ ERP synthetic data generated successfully!")
