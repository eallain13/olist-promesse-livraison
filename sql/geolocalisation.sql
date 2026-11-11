-- Coordonnées de chaque préfixe de code postal : médiane des points GPS situés au Brésil.
-- Utilisée par l'extraction des commandes et par l'API, pour que les deux calculent la même distance.
SELECT
    geolocation_zip_code_prefix AS prefixe,
    median(geolocation_lat) AS lat,
    median(geolocation_lng) AS lng
FROM read_csv('olist_geolocation_dataset.csv', types = {'geolocation_zip_code_prefix': 'VARCHAR'})
WHERE geolocation_lat BETWEEN -34 AND 5.5
  AND geolocation_lng BETWEEN -74 AND -32
GROUP BY geolocation_zip_code_prefix
