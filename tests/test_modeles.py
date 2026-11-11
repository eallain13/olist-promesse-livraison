import numpy as np
import pandas as pd
import pytest

from olist_promesse.modeles import (
    QUANTILE_PROMESSE,
    QuantileParGroupe,
    modele_gradient_boosting,
    modele_promesse,
    preparation,
)
from olist_promesse.variables import COLONNES_BRUTES, VARIABLES


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


def test_preparation_accepte_un_vendeur_et_un_etat_inconnus(commandes_brutes):
    entrainement = pd.concat([commandes_brutes] * 4, ignore_index=True)
    prep = preparation().fit(entrainement, entrainement["delai_jours"])
    sortie = prep.transform(commandes_brutes.iloc[[0]].assign(seller_id="inconnu", customer_state="XX"))
    assert list(sortie.columns) == VARIABLES
    assert np.isnan(sortie["customer_state"].iloc[0])
    vendeur = prep.named_steps["encodage"].named_transformers_["vendeur"]
    assert sortie["seller_id"].iloc[0] == pytest.approx(vendeur.target_mean_)


def test_modele_predit_une_commande_a_partir_des_colonnes_brutes(commandes_brutes):
    entrainement = pd.concat([commandes_brutes] * 4, ignore_index=True)
    modele = modele_gradient_boosting().fit(entrainement[COLONNES_BRUTES], entrainement["delai_jours"])
    prediction = modele.predict(commandes_brutes[COLONNES_BRUTES].iloc[[0]].assign(seller_id="inconnu"))
    assert prediction.shape == (1,)
    assert np.isfinite(prediction[0])


def test_parametres_remplacent_les_reglages_par_defaut():
    assert modele_gradient_boosting().get_params()["modele__loss"] == "absolute_error"
    promesse = modele_gradient_boosting(loss="quantile", quantile=0.9).get_params()
    assert (promesse["modele__loss"], promesse["modele__quantile"]) == ("quantile", 0.9)


def test_modele_promesse_vise_le_quantile_retenu():
    parametres = modele_promesse().get_params()
    assert (parametres["modele__loss"], parametres["modele__quantile"]) == ("quantile", QUANTILE_PROMESSE)
