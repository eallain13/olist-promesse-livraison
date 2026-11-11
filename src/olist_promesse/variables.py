"""Variables calculées à partir des attributs d'une commande."""

import numpy as np
import pandas as pd

RAYON_TERRE_KM = 6371.0

# Colonnes brutes connues quand le client valide son
# panier. Ce sont les seules que le modèle lit, et les informations que l'API recevra pour chaque commande.
COLONNES_BRUTES = [
    "order_purchase_timestamp",
    "seller_id",
    "seller_state",
    "seller_lat",
    "seller_lng",
    "customer_state",
    "customer_lat",
    "customer_lng",
    "prix_total",
    "fret_total",
    "poids_total_g",
    "volume_total_cm3",
    "n_articles",
    "type_paiement_principal",
    "n_echeances",
    "categorie_principale",
]

VARIABLES_NUMERIQUES = [
    "distance_km",
    "meme_etat",
    "jour_semaine_achat",
    "prix_total",
    "fret_total",
    "poids_total_g",
    "volume_total_cm3",
    "n_articles",
    "n_echeances",
]
VARIABLES_CATEGORIELLES = ["customer_state", "seller_state", "type_paiement_principal", "categorie_principale"]
VARIABLE_VENDEUR = "seller_id"
VARIABLES = VARIABLES_NUMERIQUES + VARIABLES_CATEGORIELLES + [VARIABLE_VENDEUR]


def distance_km(lat1, lng1, lat2, lng2):
    """Distance à vol d'oiseau entre deux points (formule de haversine).

    Accepte des nombres ou des colonnes (une coordonnée manquante donne une distance manquante).

    :param lat1: latitude du premier point, en degrés
    :param lng1: longitude du premier point, en degrés
    :param lat2: latitude du second point, en degrés
    :param lng2: longitude du second point, en degrés
    :return: distance en kilomètres
    """
    lat1, lng1, lat2, lng2 = (np.radians(x) for x in (lat1, lng1, lat2, lng2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2
    return 2 * RAYON_TERRE_KM * np.arcsin(np.sqrt(a))


def construire_variables(commandes: pd.DataFrame) -> pd.DataFrame:
    """Calcule les variables du modèle à partir des seules colonnes brutes autorisées.

    Le calcul se fait commande par commande : le résultat est le même pour une commande seule (API)
    que pour tout un historique (entraînement).

    :param commandes: commandes contenant au moins les colonnes de COLONNES_BRUTES
    :return: une ligne par commande, avec les colonnes de VARIABLES
    """
    brutes = commandes[COLONNES_BRUTES]
    variables = brutes.assign(
        distance_km=distance_km(brutes["seller_lat"], brutes["seller_lng"], brutes["customer_lat"], brutes["customer_lng"]),
        meme_etat=(brutes["seller_state"] == brutes["customer_state"]).astype(int),
        jour_semaine_achat=brutes["order_purchase_timestamp"].dt.day_of_week,
        n_echeances=brutes["n_echeances"].astype(float),
    )
    return variables[VARIABLES]
