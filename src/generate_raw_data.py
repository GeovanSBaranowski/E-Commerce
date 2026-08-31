import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

cities = [
    ("Florianopolis", "SC"),
    ("Porto Alegre", "RS"),
    ("Curitiba", "PR"),   
    ("Sao Paulo", "SP"),
    ("Rio De Janeiro", "RJ")
]

customers = []

for custumer_id in range(1, 101):
    city, state = random.choice(cities)
    signup_date = date(2024, 1, 1) + timedelta(days=random.randint(0,600))

    customer = {
        "custumer_id": custumer_id,
        "name": f"Cliente {custumer_id}",
        "email": f"cliente{custumer_id}@email.com",
        "signup_date": signup_date.isoformat(),
        "city": city,
        "state": state,
    }

    customers.append(customer)

categories = ["Eletronicos", "Livros", "Casa", "Esporte"]

products = []

for product_id in range(1,31):
    category = categories[(product_id - 1) % len(categories)]

    product = {
        "product_id": product_id,
        "product_name": f"{category} - produto {product_id}",
        "category": category,
        "unit_price": round(random.uniform(20,500), 2),
    }

    products.append(product)

orders = []
order_id = 10_000

while len(orders) < 1_000:
    items_in_order = random.randint(1,4)
    items_remaining = 1_000 - len(orders)

    for _ in range(min(items_in_order, items_remaining)):
        custumer = random.choice(customers)
        product = random.choice(products)
        order_date = date(2025,1,1) + timedelta(days=random.randint(0,365))

        order = {
            "order_id": order_id,
            "custumer_id": custumer["custumer_id"],
            "product_id": product["product_id"],
            "order_date": order_date.isoformat(),
            "quantity": random.randint(1,5),
            "unity_price": product["unit_price"],
            "status": random.choices(
                ["completed","cancelled","refunded"],
                weights=[90,7,3],
                k=1
            )[0],
        }

        orders.append(order)

    order_id += 1

custumers_df = pd.DataFrame(customers)
products_df = pd.DataFrame(products)
orders_df = pd.DataFrame(orders)

custumers_df.to_csv(RAW_DATA_DIR / "customers.csv", index=False)
products_df.to_csv(RAW_DATA_DIR / "products.csv", index=False)
orders_df.to_csv(RAW_DATA_DIR / "orders.csv", index=False)

print(f"Clientes gerados: {len(custumers_df)}")
print(f"Produtos gerados: {len(products_df)}")
print(f"Pedidos gerados: {len(orders_df)}")