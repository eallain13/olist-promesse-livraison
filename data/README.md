# Données

## Source et licence

*Brazilian E-Commerce Public Dataset by Olist*, publié sur Kaggle :
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Ces données sont distribuées sous licence
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (attribution, pas d'usage
commercial, partage dans les mêmes conditions). Elles ne sont pas incluses dans ce dépôt (à télécharger depuis la source).

## Obtenir les données

**Manuellement** : télécharger l'archive depuis la page Kaggle, puis extraire les 9 fichiers CSV
dans `data/raw/`.

**Avec l'outil en ligne de commande de Kaggle** (un jeton d'API doit être configuré dans
`~/.kaggle/kaggle.json`), depuis la racine du dépôt :

```bash
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

## Fichiers attendus dans `data/raw/`

| Fichier | Contenu |
|---|---|
| `olist_orders_dataset.csv` | Commandes : statut et dates (achat, validation, remise au transporteur, livraison, date promise) |
| `olist_order_items_dataset.csv` | Articles de chaque commande : produit, vendeur, prix, frais de port, date limite d'expédition |
| `olist_products_dataset.csv` | Produits : catégorie, poids, dimensions |
| `olist_sellers_dataset.csv` | Vendeurs : code postal, ville, État |
| `olist_customers_dataset.csv` | Clients : code postal, ville, État |
| `olist_geolocation_dataset.csv` | Coordonnées GPS par préfixe de code postal |
| `olist_order_payments_dataset.csv` | Paiements : moyen, nombre d'échéances, montant |
| `olist_order_reviews_dataset.csv` | Avis clients : note et commentaire |
| `product_category_name_translation.csv` | Traduction des catégories de produits en anglais |
