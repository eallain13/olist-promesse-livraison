WITH commandes AS (
    SELECT
        order_id,
        customer_id,
        order_purchase_timestamp,
        (epoch(order_delivered_customer_date) - epoch(order_purchase_timestamp)) / 86400.0 AS delai_jours,
        (epoch(order_estimated_delivery_date) - epoch(order_purchase_timestamp)) / 86400.0 AS promesse_jours,
        order_approved_at AS apres_achat_validation,
        order_delivered_carrier_date AS apres_achat_remise_transporteur
    FROM read_csv('olist_orders_dataset.csv')
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
)
, articles AS (
    SELECT
        i.order_id,
        COUNT(*) AS n_articles,
        COUNT(DISTINCT i.seller_id) AS n_vendeurs,
        arg_max(i.seller_id, i.price) AS seller_id,
        SUM(i.price) AS prix_total,
        SUM(i.freight_value) AS fret_total,
        SUM(p.product_weight_g) AS poids_total_g,
        SUM(p.product_length_cm * p.product_height_cm * p.product_width_cm) AS volume_total_cm3,
        arg_max(coalesce(t.product_category_name_english, p.product_category_name), i.price) AS categorie_principale,
        MAX(i.shipping_limit_date) AS limite_expedition
    FROM read_csv('olist_order_items_dataset.csv') AS i
    LEFT JOIN read_csv('olist_products_dataset.csv') AS p ON p.product_id = i.product_id
    LEFT JOIN read_csv('product_category_name_translation.csv') AS t
        ON t.product_category_name = p.product_category_name
    GROUP BY i.order_id
)
, paiements AS (
    SELECT
        order_id,
        arg_max(payment_type, payment_value) AS type_paiement_principal,
        MAX(payment_installments) AS n_echeances,
        COUNT(*) AS n_paiements
    FROM read_csv('olist_order_payments_dataset.csv')
    GROUP BY order_id
)
, geo AS (
    SELECT
        geolocation_zip_code_prefix AS prefixe,
        median(geolocation_lat) AS lat,
        median(geolocation_lng) AS lng
    FROM read_csv('olist_geolocation_dataset.csv', types = {'geolocation_zip_code_prefix': 'VARCHAR'})
    GROUP BY geolocation_zip_code_prefix
)
, avis AS (
    SELECT order_id, AVG(review_score) AS note_avis
    FROM read_csv('olist_order_reviews_dataset.csv')
    GROUP BY order_id
)
SELECT
    c.order_id,
    a.seller_id,
    c.order_purchase_timestamp,
    c.delai_jours,
    c.promesse_jours,
    a.n_articles,
    a.n_vendeurs,
    a.prix_total,
    a.fret_total,
    a.poids_total_g,
    a.volume_total_cm3,
    a.categorie_principale,
    pa.type_paiement_principal,
    pa.n_echeances,
    pa.n_paiements,
    s.seller_zip_code_prefix,
    s.seller_state,
    gs.lat AS seller_lat,
    gs.lng AS seller_lng,
    cu.customer_zip_code_prefix,
    cu.customer_state,
    gc.lat AS customer_lat,
    gc.lng AS customer_lng,
    c.apres_achat_validation,
    c.apres_achat_remise_transporteur,
    round((epoch(a.limite_expedition) - epoch(c.apres_achat_validation)) / 86400.0) AS apres_achat_delai_vendeur_jours,
    av.note_avis AS apres_achat_note_avis
FROM commandes AS c
LEFT JOIN articles AS a ON a.order_id = c.order_id
LEFT JOIN paiements AS pa ON pa.order_id = c.order_id
LEFT JOIN read_csv('olist_customers_dataset.csv', types = {'customer_zip_code_prefix': 'VARCHAR'}) AS cu
    ON cu.customer_id = c.customer_id
LEFT JOIN read_csv('olist_sellers_dataset.csv', types = {'seller_zip_code_prefix': 'VARCHAR'}) AS s
    ON s.seller_id = a.seller_id
LEFT JOIN geo AS gs ON gs.prefixe = s.seller_zip_code_prefix
LEFT JOIN geo AS gc ON gc.prefixe = cu.customer_zip_code_prefix
LEFT JOIN avis AS av ON av.order_id = c.order_id
ORDER BY c.order_purchase_timestamp
