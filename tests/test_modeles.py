import pandas as pd

from olist_promesse.modeles import QuantileParGroupe


def test_repli_sur_le_quantile_global():
    X = pd.DataFrame({"etat": ["SP", "SP", "SP", "RJ"]})
    modele = QuantileParGroupe(niveaux=[["etat"]], effectif_min=2).fit(X, [2.0, 4.0, 6.0, 30.0])
    prediction = modele.predict(pd.DataFrame({"etat": ["SP", "RJ", "AM"]}))
    assert prediction.tolist() == [4.0, 5.0, 5.0]


def test_niveaux_du_plus_precis_au_plus_large():
    X = pd.DataFrame({"vendeur": ["SP", "SP", "MG", "MG"], "client": ["RJ", "RJ", "RJ", "RJ"]})
    modele = QuantileParGroupe(niveaux=[["vendeur", "client"], ["client"]], effectif_min=2)
    modele.fit(X, [2.0, 4.0, 10.0, 12.0])
    prediction = modele.predict(pd.DataFrame({"vendeur": ["SP", "PR"], "client": ["RJ", "RJ"]}))
    assert prediction.tolist() == [3.0, 7.0]
