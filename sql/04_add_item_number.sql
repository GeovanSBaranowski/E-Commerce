BEGIN;

ALTER TABLE order_items
    ADD COLUMN IF NOT EXISTS item_number INTEGER CHECK (item_number > 0);

WITH numbered_items AS (
    SELECT
        order_item_id,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY order_item_id
        ) AS item_number
    FROM order_items
)
UPDATE order_items AS oi
SET item_number = ni.item_number
FROM numbered_items AS ni
WHERE oi.order_item_id = ni.order_item_id
  AND oi.item_number IS NULL;

ALTER TABLE order_items
    ALTER COLUMN item_number SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_order_items_order_id_item_number
    ON order_items (order_id, item_number);

COMMIT;