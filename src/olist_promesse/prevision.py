"""Prévision pour une commande : délai estimé et date promise."""

import os
from pathlib import Path

import joblib
import pandas as pd

from olist_promesse.evaluation import date_promise
from olist_promesse.variables import COLONNES_BRUTES

# Fichier produit par le script d'entraînement
CHEMIN_MODELES = Path(
    os.environ.get("OLIST_MODELES", Path(__file__).resolve().parents[2] / "artifacts" / "modeles.joblib")
)


class VendeurInconnu(ValueError):
    """Le vendeur n'existe pas dans la table des vendeurs."""


def charger_modeles(chemin: Path = CHEMIN_MODELES) -> dict:
    """Charge les modèles et les tables de correspondance enregistrés par l'entraînement."""
    return joblib.load(chemin)


def preparer_commande(commande: dict, modeles: dict) -> pd.DataFrame:
    """Complète une commande avec la localisation du vendeur et du client, au format des colonnes brutes.

    :param commande: informations connues du site à l'achat (vendeur, code postal et État du client,
        montants, poids, volume, nombre d'articles, catégorie, paiement, date d'achat)
    :param modeles: modèles et tables de correspondance (voir charger_modeles)
    :return: une ligne avec les colonnes de COLONNES_BRUTES
    """
    vendeurs, geolocalisation = modeles["vendeurs"], modeles["geolocalisation"]
    if commande["seller_id"] not in vendeurs.index:
        raise VendeurInconnu(commande["seller_id"])
    vendeur = vendeurs.loc[commande["seller_id"]]
    # Un code postal absent de la table donne des coordonnées manquantes
    coordonnees_vendeur = geolocalisation.reindex([vendeur["seller_zip_code_prefix"]]).iloc[0]
    coordonnees_client = geolocalisation.reindex([commande["customer_zip_code_prefix"]]).iloc[0]
    ligne = {
        **commande,
        "seller_state": vendeur["seller_state"],
        "seller_lat": coordonnees_vendeur["lat"],
        "seller_lng": coordonnees_vendeur["lng"],
        "customer_lat": coordonnees_client["lat"],
        "customer_lng": coordonnees_client["lng"],
    }
    return pd.DataFrame([ligne])[COLONNES_BRUTES]


def prevoir(commande: dict, modeles: dict) -> dict:
    """Estime le délai de livraison d'une commande et calcule la date promise au client.

    :param commande: voir preparer_commande
    :param modeles: modèles et tables de correspondance (voir charger_modeles)
    :return: délai estimé en jours, date de livraison estimée et date promise
    """
    X = preparer_commande(commande, modeles)
    estimation = float(modeles["estimation"].predict(X)[0])
    # Deux modèles distincts pourraient théoriquement se croiser même si la promesse observée ne descend jamais sous l'estimation.
    promesse = max(float(modeles["promesse"].predict(X)[0]), estimation)
    achat = X["order_purchase_timestamp"]
    return {
        "delai_estime_jours": round(estimation, 1),
        "date_livraison_estimee": date_promise(achat, pd.Series([estimation])).iloc[0].date(),
        "date_promise": date_promise(achat, pd.Series([promesse])).iloc[0].date(),
    }
