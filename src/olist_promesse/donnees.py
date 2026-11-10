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
