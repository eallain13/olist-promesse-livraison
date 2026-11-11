import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def commandes_brutes():
    """Trois commandes fictives avec les colonnes de l'extraction, y compris postérieures à l'achat."""
    return pd.DataFrame({
        "order_id": ["a", "b", "c"],
        "order_purchase_timestamp": pd.to_datetime(
            ["2018-03-05 10:00:00", "2018-03-09 22:30:00", "2018-03-10 08:15:00"]
        ),
        "seller_id": ["v1", "v2", "v1"],
        "seller_state": ["SP", "SP", "SP"],
        "seller_lat": [-23.55, -23.55, -23.55],
        "seller_lng": [-46.63, -46.63, -46.63],
        "customer_state": ["RJ", "SP", "RJ"],
        "customer_lat": [-22.91, -23.55, np.nan],
        "customer_lng": [-43.17, -46.63, np.nan],
        "prix_total": [100.0, 35.5, 250.0],
        "fret_total": [15.2, 8.0, 30.1],
        "poids_total_g": [500.0, 200.0, np.nan],
        "volume_total_cm3": [8000.0, 1500.0, np.nan],
        "n_articles": [1, 1, 3],
        "type_paiement_principal": ["credit_card", "boleto", "credit_card"],
        "n_echeances": pd.array([3, 1, 10], dtype="Int64"),
        "categorie_principale": ["bed_bath_table", "toys", None],
        "delai_jours": [7.5, 3.2, 12.0],
        "promesse_jours": [20.0, 15.0, 25.0],
        "apres_achat_validation": pd.to_datetime(["2018-03-05 10:30:00", "2018-03-11 09:00:00", "2018-03-10 09:00:00"]),
        "apres_achat_note_avis": [5.0, 4.0, 1.0],
    })
