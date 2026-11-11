import pandas as pd

from olist_promesse.donnees import selectionner_commandes


def commandes_fictives():
    return pd.DataFrame({
        "order_id": ["a", "b", "c", "d", "e"],
        "order_purchase_timestamp": pd.to_datetime(
            ["2016-10-05 14:00", "2017-03-01 09:30", "2018-07-31 23:59", "2018-08-01 00:00", "2018-02-10 18:15"]
        ),
        "n_vendeurs": [1, 1, 1, 1, 2],
    })


def test_regles_appliquees():
    retenues, _ = selectionner_commandes(commandes_fictives())
    assert list(retenues["order_id"]) == ["b", "c"]


def test_entonnoir_coherent():
    commandes = commandes_fictives()
    retenues, entonnoir = selectionner_commandes(commandes)
    assert entonnoir["restantes"].iloc[0] == len(commandes)
    assert entonnoir["restantes"].iloc[-1] == len(retenues)
    assert entonnoir["retirees"].sum() == len(commandes) - len(retenues)
    assert entonnoir["restantes"].is_monotonic_decreasing
