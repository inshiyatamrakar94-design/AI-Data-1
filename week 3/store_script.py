import mysql.connector
import csv

# --- 1. CONNECTION & DATABASE SETUP ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Admin2026!"  # <-- Change to ur MySQL password
)
cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS store_db")
cursor.execute("USE store_db")

# --- 2. TABLE CREATION ---
cursor.execute("DROP TABLE IF EXISTS orders")
cursor.execute("DROP TABLE IF EXISTS customers")
cursor.execute("DROP TABLE IF EXISTS products")

cursor.execute("""
    CREATE TABLE customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        city VARCHAR(100)
    )
""")

cursor.execute("""
    CREATE TABLE products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        price DECIMAL(10, 2)
    )
""")

cursor.execute("""
    CREATE TABLE orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        product_id INT,
        quantity INT,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
""")

# --- 3. DATA INSERTION (Parameterized %s) ---
cust_data = [('Alice', 'NY'),
                 ('Bob', 'LA'),
                 ('Charlie', 'NY'), 
                 ('David', 'CHI'),
                 ('Eve', 'LA'),
                 ('Frank', 'MIA'),
                 ('Grace', 'CHI'),
                 ('Heidi', 'NY'),
                 ('Ivan', 'SEA'),
                 ('Judy', 'SEA')]
cursor.executemany("INSERT INTO customers (name, city) VALUES (%s, %s)", cust_data)

prod_data = [('Laptop', 1200), ('Mouse', 25), ('Keyboard', 50), ('Monitor', 300),
             ('USB-C Cable', 15), ('Headphones', 100), ('Webcam', 80), ('Desk Lamp', 45)]
cursor.executemany("INSERT INTO products (name, price) VALUES (%s, %s)", prod_data)

# 20 randomized orders (cust_id, prod_id, quantity)
order_data = [
    (1, 1, 1), (1, 2, 2), (2, 3, 1), (2, 4, 1), (2, 5, 3), (3, 1, 1), (4, 6, 2), (4, 7, 1),
    (4, 8, 1), (5, 2, 5), (6, 3, 2), (7, 4, 1), (8, 1, 1), (8, 5, 2), (8, 8, 1), (9, 6, 1),
    (10, 7, 2), (1, 8, 1), (2, 2, 1), (3, 4, 1)
]
cursor.executemany("INSERT INTO orders (customer_id, product_id, quantity) VALUES (%s, %s, %s)", order_data)
db.commit()

# --- 4. DATA ANALYSIS QUERIES ---

# Query 1: Total money spent per customer
q1 = """
    SELECT c.name, SUM(p.price * o.quantity) as total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    GROUP BY c.name
    ORDER BY total_spent DESC
"""
cursor.execute(q1)
revenue_results = cursor.fetchall()

# Query 2: Most ordered product by total quantity
q2 = """
    SELECT p.name, SUM(o.quantity) as total_qty
    FROM products p
    JOIN orders o ON p.id = o.product_id
    GROUP BY p.name
    ORDER BY total_qty DESC LIMIT 1
"""
cursor.execute(q2)
most_ordered = cursor.fetchone()

# Query 3: Customers with more than 2 orders
q3 = """
    SELECT c.name, COUNT(o.id) as order_count
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.name
    HAVING order_count > 2
"""
cursor.execute(q3)
frequent_buyers = cursor.fetchall()

# Query 4: Average order value per city
q4 = """
    SELECT c.city, AVG(p.price * o.quantity) as avg_val
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    GROUP BY c.city
"""
cursor.execute(q4)
city_avg = cursor.fetchall()

# --- 5. PRINT RESULTS ---
print("\n--- Total Revenue Per Customer ---")
for row in revenue_results: print(f"{row[0]}: ${row[1]:.2f}")

print(f"\n--- Most Ordered Product ---\n{most_ordered[0]} ({most_ordered[1]} units)")

print("\n--- Customers with > 2 Orders ---")
for row in frequent_buyers: print(f"{row[0]} ({row[1]} orders)")

print("\n--- Avg Order Value Per City ---")
for row in city_avg: print(f"{row[0]}: ${row[1]:.2f}")

# --- 6. EXPORT TO CSV ---
with open('revenue_report.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Customer Name', 'Total Spent'])
    writer.writerows(revenue_results)

print("\n✔ revenue_report.csv has been generated.")

cursor.close()
db.close()

