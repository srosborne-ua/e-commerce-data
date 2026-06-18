import pandas as pd 
from pathlib import Path

DATA_DIR = Path("/Users/sageosborne/Documents/e-commerce-data/data")

from pathlib import Path
import pandas as pd

DATA_DIR = Path("/Users/sageosborne/Documents/e-commerce-data/data")

frames = {
    "customers":          pd.read_csv(DATA_DIR / "olist_customers_dataset.csv"),
    "geolocation":        pd.read_csv(DATA_DIR / "olist_geolocation_dataset.csv"),
    "order_items":        pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv"),
    "order_payments":     pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv"),
    "order_reviews":      pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv"),
    "orders":             pd.read_csv(DATA_DIR / "olist_orders_dataset.csv"),
    "products":           pd.read_csv(DATA_DIR / "olist_products_dataset.csv"),
    "sellers":            pd.read_csv(DATA_DIR / "olist_sellers_dataset.csv"),
    "category_translation": pd.read_csv(DATA_DIR / "product_category_name_translation.csv"),
}

# for name, df in frames.items():
#     print(f"\n{name}: {df.shape[0]:,} rows, {df.shape[1]} cols — nulls: {df.isnull().sum().sum()}")
#     print(f"  columns: {list(df.columns)}")

# for name, df in frames.items():
#     print(f"\n{name}:")
#     print(df.head(1))

from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://localhost/olist")

# Load all frames into postgres — table name = dict key
# for name, df in frames.items():
#     df.to_sql(name, engine, if_exists="replace", index=False)
#     print(f"Loaded {name}: {len(df)} rows")

# order_status_query = """select distinct order_status
#                         from orders"""

# all_delivered_orders_query = """select * from orders where order_status = 'delivered'"""

# filtered_orders = """select order_id, order_status, order_purchase_timestamp
# from orders where order_purchase_timestamp > '2018-01-01' and order_status = 'delivered'
# order by order_purchase_timestamp asc"""

# order_type_count = """select order_status, count(order_status) from orders
# group by order_status 
# order by count(order_status) desc"""

# customer_order_join = """select order_id, order_status, customers.customer_state, customers.customer_city from orders
# join customers on customers.customer_id = orders.customer_id
# limit 10"""

total_rev = """select order_id, sum(price + freight_value) as order_revenue
                from order_items
                group by order_id
                order by order_revenue desc
                limit 10
                """

df = pd.read_sql(total_rev, engine)
print(df)



# print(pd.read_sql(query1, engine))