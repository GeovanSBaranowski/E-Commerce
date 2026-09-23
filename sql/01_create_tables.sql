CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    signup_date DATE NOT NULL,
    city TEXT NOT NULL,
    state CHAR(2) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id BIGSERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    order_date DATE NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    status TEXT NOT NULL CHECK (
        status IN ('completed', 'cancelled', 'refunded')
    )
);