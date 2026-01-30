create database ERP_db;
use erp_db;

CREATE TABLE Products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    fabric_type VARCHAR(50),
    unit_price DECIMAL(10,2),
    reorder_level INT,
    lead_time_days INT
);

CREATE TABLE Inventory (
    inventory_id INT PRIMARY KEY,
    product_id INT,
    current_stock INT,
    warehouse_location VARCHAR(50),
    last_updated DATE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

CREATE TABLE Suppliers (
    supplier_id INT PRIMARY KEY,
    supplier_name VARCHAR(100),
    rating DECIMAL(3,2),
    avg_delivery_days INT
);

CREATE TABLE Purchase_Orders (
    po_id INT PRIMARY KEY,
    supplier_id INT,
    order_date DATE,
    expected_delivery DATE,
    total_amount DECIMAL(12,2),
    status VARCHAR(20),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);

CREATE TABLE Production_Batches (
    batch_id INT PRIMARY KEY,
    product_id INT,
    production_date DATE,
    quantity_produced INT,
    defect_quantity INT,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    region VARCHAR(50)
);

CREATE TABLE Sales_Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    delivery_date DATE,
    total_amount DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE Sales_Order_Items (
    item_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES Sales_Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

CREATE TABLE Quality_Reports (
    report_id INT PRIMARY KEY,
    batch_id INT,
    inspection_date DATE,
    quality_score DECIMAL(4,2),
    remarks VARCHAR(255),
    FOREIGN KEY (batch_id) REFERENCES Production_Batches(batch_id)
);

CREATE TABLE Invoices (
    invoice_id INT PRIMARY KEY,
    po_id INT,
    invoice_date DATE,
    invoice_amount DECIMAL(12,2),
    payment_status VARCHAR(20),
    FOREIGN KEY (po_id) REFERENCES Purchase_Orders(po_id)
);


select * from purchase_orders;

ALTER TABLE purchase_orders
MODIFY COLUMN po_id INT NOT NULL AUTO_INCREMENT;

INSERT INTO purchase_orders (supplier_id, order_date, status)
            VALUES (5, '2026-01-30', 'CREATED');
 
 /* Foreign Key : invoices, purchase_order_items, */
            
-- ALTER TABLE purchase_order_items
-- DROP FOREIGN KEY purchase_order_items_ibfk_1;
-- ALTER TABLE purchase_orders
-- MODIFY COLUMN po_id INT NOT NULL AUTO_INCREMENT;
-- ALTER TABLE purchase_order_items
-- ADD CONSTRAINT purchase_order_items_ibfk_1
-- FOREIGN KEY (po_id)
-- REFERENCES purchase_orders(po_id)
-- ON UPDATE CASCADE
-- ON DELETE RESTRICT;
