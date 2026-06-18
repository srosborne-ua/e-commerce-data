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

on_time_query = """select
                case
                    when o.order_delivered_customer_date::timestamp <= o.order_estimated_delivery_date::timestamp
                    then 'On Time'
                    when o.order_delivered_customer_date::timestamp <= o.order_estimated_delivery_date::timestamp + Interval '3 days'
                    then '1-3 days late'
                    when o.order_delivered_customer_date::timestamp <= o.order_estimated_delivery_date::timestamp + Interval '7 days'
                    then '4-7 days late'
                    else '7+ days late'
                    end as arrival_time_status, ROUND(AVG(r.review_score), 2) AS avg_review_score, COUNT(*) AS order_count
                from orders o 
                Join order_reviews r on r.order_id = o.order_id
                where o.order_delivered_customer_date IS NOT NULL
                AND o.order_estimated_delivery_date IS NOT NULL
                GROUP BY arrival_time_status
                ORDER BY avg_review_score DESC
                """

revenue_by_category = """
                    SELECT
                        ct.product_category_name_english AS category,
                        ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
                        ROUND(SUM(oi.freight_value)::numeric, 2) AS total_freight,
                        ROUND((SUM(oi.freight_value) / SUM(oi.price) * 100)::numeric, 1) AS freight_pct,
                        COUNT(DISTINCT oi.order_id) AS order_count
                    FROM order_items oi
                    JOIN products p ON p.product_id = oi.product_id
                    JOIN category_translation ct ON ct.product_category_name = p.product_category_name
                    GROUP BY category
                    ORDER BY total_revenue DESC
                    LIMIT 20;
                    """

customer_segmentation = customer_segmentation = """
WITH rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp::timestamp) AS last_order,
        COUNT(DISTINCT o.order_id)                 AS frequency,
        ROUND(SUM(op.payment_value)::numeric, 2)   AS monetary
    FROM orders o
    JOIN customers c       ON c.customer_id = o.customer_id
    JOIN order_payments op ON op.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
scored AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY last_order) AS r_score,
        NTILE(4) OVER (ORDER BY frequency)  AS f_score,
        NTILE(4) OVER (ORDER BY monetary)   AS m_score
    FROM rfm
),
labeled AS (
    SELECT *,
        (r_score + f_score + m_score) AS rfm_total,
        CASE
            WHEN (r_score + f_score + m_score) >= 10 THEN 'Champions'
            WHEN (r_score + f_score + m_score) >= 7  THEN 'Loyal'
            WHEN (r_score + f_score + m_score) >= 5  THEN 'At Risk'
            ELSE 'Lost'
        END AS segment
    FROM scored
)
SELECT segment,
       COUNT(*)                             AS customer_count,
       ROUND(AVG(monetary)::numeric, 2)     AS avg_spend,
       ROUND(AVG(frequency)::numeric, 2)    AS avg_orders
FROM labeled
GROUP BY segment
ORDER BY avg_spend DESC
"""

month_revenue = """
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp::timestamp)::date AS month,
        ROUND(SUM(op.payment_value)::numeric, 2) AS monthly_revenue
    FROM orders o
    JOIN order_payments op ON op.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
),
lagged AS (
    SELECT *,
        LAG(monthly_revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly
)
SELECT
    month,
    monthly_revenue,
    prev_revenue,
    ROUND(((monthly_revenue - prev_revenue) / prev_revenue * 100)::numeric, 1) AS mom_pct_change
FROM lagged
ORDER BY month
"""
OUTPUT_DIR = Path("/Users/sageosborne/Documents/e-commerce-data/output")
OUTPUT_DIR.mkdir(exist_ok=True)

queries = {
    "delivery_review":    on_time_query,
    "category_revenue":   revenue_by_category,
    "rfm_segments":       customer_segmentation,
    "mom_revenue":        month_revenue,
}

for name, query in queries.items():
    df = pd.read_sql(query, engine)
    df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
    print(f"exported {name}: {len(df)} rows")