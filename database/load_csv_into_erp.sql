
#Loading data from each csv file into erpdb

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/purchase_order_items.csv'
INTO TABLE purchase_order_items
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

select * from invoices;

use erp_db;

SELECT p.product_name, SUM(soi.quantity) AS total_sold
FROM Sales_Order_Items soi
JOIN Products p ON soi.product_id = p.product_id
GROUP BY p.product_name;

#Demand Forecast Table
CREATE TABLE Demand_Forecast (
    product_id INT,
    predicted_demand INT,
    forecast_date DATE
);

select *from demand_forecast;
select * from products;

#Recorder Engine
CREATE TABLE IF NOT EXISTS Reorder_Recommendations (
    product_id INT,
    current_stock INT,
    predicted_demand INT,
    reorder_quantity INT,
    recommendation_date DATE
);

select * from products;

#PO items
CREATE TABLE IF NOT EXISTS Purchase_Order_Items (
    po_item_id INT AUTO_INCREMENT PRIMARY KEY,
    po_id INT,
    product_id INT,
    order_quantity INT,
    FOREIGN KEY (po_id) REFERENCES Purchase_Orders(po_id)
);
select * from purchase_order_items;




