"""Entraîne les modèles finaux et les enregistre avec les tables dont l'API a besoin.

Lancement depuis la racine du dépôt : python -m olist_promesse.entrainement
"""

import joblib
import pandas as pd

from olist_promesse.donnees import FIN_PERIODE, charger_commandes, charger_tables, selectionner_commandes
from olist_promesse.evaluation import CIBLE, decoupage_mensuel
from olist_promesse.modeles import QUANTILE_PROMESSE, modele_gradient_boosting, modele_promesse
from olist_promesse.prevision import CHEMIN_MODELES
from olist_promesse.variables import COLONNES_BRUTES


def entrainer(commandes: pd.DataFrame) -> dict:
    """Entraîne les deux modèles comme on l'aurait fait le 1er août 2018, sur les commandes déjà livrées.

    :param commandes: commandes retenues
    :return: modèle d'estimation, modèle de promesse et informations sur l'entraînement
    """
    entrainement, _ = decoupage_mensuel(commandes, pd.Period(FIN_PERIODE, freq="M"))
    X, y = entrainement[COLONNES_BRUTES], entrainement[CIBLE]
    return {
        "estimation": modele_gradient_boosting().fit(X, y),
        "promesse": modele_promesse().fit(X, y),
        "quantile_promesse": QUANTILE_PROMESSE,
        "date_entrainement": FIN_PERIODE,
        "commandes_entrainement": len(entrainement),
    }


def main():
    commandes, _ = selectionner_commandes(charger_commandes())
    modeles = entrainer(commandes)
    modeles["vendeurs"], modeles["geolocalisation"] = charger_tables()
    CHEMIN_MODELES.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modeles, CHEMIN_MODELES)
    print(f"{modeles['commandes_entrainement']} commandes d'entraînement ; modèles enregistrés dans {CHEMIN_MODELES}")


if __name__ == "__main__":
    main()
