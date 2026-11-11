import numpy as np
import pandas as pd
import pytest

from olist_promesse.prevision import VendeurInconnu, preparer_commande, prevoir
from olist_promesse.variables import COLONNES_BRUTES

COMMANDE = {
    "order_purchase_timestamp": pd.Timestamp("2018-08-15 10:30:00"),
    "seller_id": "v1",
    "customer_zip_code_prefix": "20000",
    "customer_state": "RJ",
    "prix_total": 129.9,
    "fret_total": 15.1,
    "poids_total_g": 800.0,
    "volume_total_cm3": 6000.0,
    "n_articles": 1,
    "categorie_principale": "bed_bath_table",
    "type_paiement_principal": "credit_card",
    "n_echeances": 3,
}


def test_commande_completee_avec_la_localisation(modeles_fictifs):
    ligne = preparer_commande(COMMANDE, modeles_fictifs)
    assert list(ligne.columns) == COLONNES_BRUTES
    assert ligne["seller_state"].iloc[0] == "SP"
    assert (ligne["seller_lat"].iloc[0], ligne["customer_lat"].iloc[0]) == (-23.55, -22.91)


def test_prevision_coherente(modeles_fictifs):
    prevision = prevoir(COMMANDE, modeles_fictifs)
    assert set(prevision) == {"delai_estime_jours", "date_livraison_estimee", "date_promise"}
    assert COMMANDE["order_purchase_timestamp"].date() <= prevision["date_livraison_estimee"] <= prevision["date_promise"]


def test_informations_manquantes_acceptees(modeles_fictifs):
    commande = COMMANDE | {"customer_zip_code_prefix": "99999", "poids_total_g": None, "categorie_principale": None}
    assert np.isnan(preparer_commande(commande, modeles_fictifs)["customer_lat"].iloc[0])
    assert prevoir(commande, modeles_fictifs)["delai_estime_jours"] > 0


def test_vendeur_inconnu_refuse(modeles_fictifs):
    with pytest.raises(VendeurInconnu):
        prevoir(COMMANDE | {"seller_id": "inconnu"}, modeles_fictifs)
