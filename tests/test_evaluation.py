import pandas as pd
import pytest

from olist_promesse.evaluation import (
    date_promise,
    decoupage_mensuel,
    delai_promis_a_retard,
    en_retard,
    quantile_pour_retard,
)


def commande(achat, livraison):
    achat, livraison = pd.Timestamp(achat), pd.Timestamp(livraison)
    return {"order_purchase_timestamp": achat, "delai_jours": (livraison - achat) / pd.Timedelta(days=1)}


def test_entrainement_limite_aux_commandes_deja_livrees():
    commandes = pd.DataFrame([
        commande("2018-04-01 09:00", "2018-04-10 12:00"),
        commande("2018-04-25 09:00", "2018-05-03 12:00"),
        commande("2018-05-02 09:00", "2018-05-09 12:00"),
        commande("2018-06-01 09:00", "2018-06-05 12:00"),
    ])
    entrainement, evaluation = decoupage_mensuel(commandes, pd.Period("2018-05", freq="M"))
    assert entrainement.index.tolist() == [0]
    assert evaluation.index.tolist() == [2]


def test_date_promise_au_jour_pres():
    achat = pd.Series(pd.to_datetime(["2018-01-01 20:00:00", "2017-01-05 11:56:06"]))
    # Promesse Olist calculée comme dans la requête SQL : jusqu'au 1er février à minuit.
    promesse_olist = (pd.Timestamp("2017-02-01") - achat[1]).total_seconds() / 86400.0
    promesse = pd.Series([2.5, promesse_olist])
    assert date_promise(achat, promesse).tolist() == [pd.Timestamp("2018-01-04"), pd.Timestamp("2017-02-01")]


def test_livrer_le_jour_promis_est_a_l_heure():
    commandes = pd.DataFrame([
        commande("2018-01-01 10:00", "2018-01-05 15:00"),
        commande("2018-01-01 10:00", "2018-01-06 08:00"),
    ])
    assert en_retard(commandes, pd.Series([4.0, 4.0])).tolist() == [False, True]


def test_lecture_de_la_courbe_promesse():
    courbe = pd.DataFrame(
        {"taux de retard (%)": [12.0, 8.0, 4.0], "délai promis moyen (j)": [20.0, 24.0, 30.0]},
        index=pd.Index([0.94, 0.96, 0.98], name="quantile visé"),
    )
    assert quantile_pour_retard(courbe, 10.0) == pytest.approx(0.95)
    assert delai_promis_a_retard(courbe, 6.0) == pytest.approx(27.0)
