"""Extraction des données Olist : une ligne par commande livrée."""

from pathlib import Path

import duckdb
import pandas as pd

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_DONNEES = RACINE / "data" / "raw"
REQUETE_COMMANDES = RACINE / "sql" / "commandes.sql"
REQUETE_GEOLOCALISATION = RACINE / "sql" / "geolocalisation.sql"


def connecter(dossier: Path = DOSSIER_DONNEES) -> duckdb.DuckDBPyConnection:
    """Connexion DuckDB qui lit les CSV du dossier et connaît la vue « geolocalisation »."""
    con = duckdb.connect()
    con.execute(f"SET file_search_path = '{Path(dossier).resolve()}'")
    con.execute(f"CREATE VIEW geolocalisation AS {REQUETE_GEOLOCALISATION.read_text()}")
    return con


def charger_commandes(dossier: Path = DOSSIER_DONNEES) -> pd.DataFrame:
    """Exécute la requête d'extraction et renvoie une ligne par commande livrée.

    :param dossier: dossier contenant les 9 CSV Olist
    :return: DataFrame d'une ligne par commande, triée par date d'achat
    """
    with connecter(dossier) as con:
        return con.sql(REQUETE_COMMANDES.read_text()).df()


def charger_tables(dossier: Path = DOSSIER_DONNEES) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tables de correspondance de l'API : vendeur → code postal et État, code postal → coordonnées.

    :param dossier: dossier contenant les 9 CSV Olist
    :return: vendeurs indexés par identifiant, coordonnées indexées par préfixe de code postal
    """
    with connecter(dossier) as con:
        vendeurs = con.sql("""
            SELECT seller_id, seller_zip_code_prefix, seller_state
            FROM read_csv('olist_sellers_dataset.csv', types = {'seller_zip_code_prefix': 'VARCHAR'})
        """).df()
        geolocalisation = con.sql("SELECT * FROM geolocalisation").df()
    return vendeurs.set_index("seller_id"), geolocalisation.set_index("prefixe")


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
