"""Extraction des données Olist : une ligne par commande livrée."""

from pathlib import Path

import duckdb
import pandas as pd

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_DONNEES = RACINE / "data" / "raw"
REQUETE_COMMANDES = RACINE / "sql" / "commandes.sql"


def charger_commandes(dossier: Path = DOSSIER_DONNEES) -> pd.DataFrame:
    """Exécute la requête d'extraction et renvoie une ligne par commande livrée.

    :param dossier: dossier contenant les 9 CSV Olist
    :return: DataFrame d'une ligne par commande, triée par date d'achat
    """
    with duckdb.connect() as con:
        con.execute(f"SET file_search_path = '{Path(dossier).resolve()}'")
        return con.sql(REQUETE_COMMANDES.read_text()).df()


# Les achats de 2016 correspondent au lancement de la plateforme (peu de volume, aucun en novembre)
# Les données s'arrêtent début septembre 2018 et les commandes d'août n'y figurent que si elles ont
# été livrées vite : on s'arrête donc à fin juillet
DEBUT_PERIODE = pd.Timestamp("2017-01-01")
FIN_PERIODE = pd.Timestamp("2018-08-01")


def selectionner_commandes(commandes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Applique les règles d'inclusion et renvoie les commandes retenues avec l'entonnoir.

    :param commandes: une ligne par commande livrée (sortie de charger_commandes)
    :return: commandes retenues, et nombre de commandes restantes après chaque règle
    """
    achat = commandes["order_purchase_timestamp"]
    regles = {
        "Achat à partir de 2017": achat >= DEBUT_PERIODE,
        "Achat avant août 2018": achat < FIN_PERIODE,
        # Chaque vendeur envoie son colis, mais la commande n'a qu'une date de livraison (celle de quel colis ?)
        "Un seul vendeur": commandes["n_vendeurs"] == 1,
    }

    garde = pd.Series(True, index=commandes.index)
    etapes = [{"etape": "Commandes livrées (extraction SQL)", "restantes": len(commandes)}]
    for regle, condition in regles.items():
        garde &= condition # On garde ce qui était déjà gardé ET qui respecte la nouvelle règle 
        etapes.append({"etape": regle, "restantes": int(garde.sum())})

    entonnoir = pd.DataFrame(etapes)
    # Retirées = restantes à l'étape précédente - restantes à cette étape
    entonnoir["retirees"] = entonnoir["restantes"].shift(fill_value=len(commandes)) - entonnoir["restantes"]
    return commandes[garde].reset_index(drop=True), entonnoir
