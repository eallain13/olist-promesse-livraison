import numpy as np
import pytest

from olist_promesse.donnees import DOSSIER_DONNEES, charger_commandes, charger_tables

pytestmark = pytest.mark.skipif(
    not (DOSSIER_DONNEES / "olist_orders_dataset.csv").exists(),
    reason="données Olist absentes (voir data/README.md)",
)


@pytest.fixture(scope="module")
def commandes():
    return charger_commandes()


def test_une_ligne_par_commande(commandes):
    assert commandes["order_id"].is_unique


def test_cible_renseignee_et_positive(commandes):
    assert commandes["delai_jours"].notna().all()
    assert (commandes["delai_jours"] > 0).all()


def test_nombre_de_commandes_coherent(commandes):
    assert len(commandes) > 95_000


def test_extraction_reproductible(commandes):
    assert commandes["order_id"].tolist() == charger_commandes()["order_id"].tolist()


def test_tables_de_l_api_coherentes_avec_l_extraction(commandes):
    vendeurs, geolocalisation = charger_tables()
    assert commandes["seller_id"].isin(vendeurs.index).all()
    attendues = geolocalisation.reindex(commandes["customer_zip_code_prefix"])["lat"].to_numpy()
    np.testing.assert_array_equal(commandes["customer_lat"].to_numpy(), attendues)
