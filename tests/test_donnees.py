import pytest

from olist_promesse.donnees import DOSSIER_DONNEES, charger_commandes

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
