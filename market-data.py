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

print(frames["customers"].head)
print(frames["geolocation"].info())