import numpy as np
import pandas as pd
import pytest

from olist_promesse.variables import COLONNES_BRUTES, VARIABLES, construire_variables, distance_km

SAO_PAULO = (-23.5505, -46.6333)
RIO = (-22.9068, -43.1729)


def test_distance_connue():
    assert distance_km(*SAO_PAULO, *RIO) == pytest.approx(361, abs=5)


def test_distance_nulle_et_symetrique():
    assert distance_km(*SAO_PAULO, *SAO_PAULO) == pytest.approx(0)
    assert distance_km(*SAO_PAULO, *RIO) == pytest.approx(distance_km(*RIO, *SAO_PAULO))


def test_coordonnee_manquante():
    lat = pd.Series([SAO_PAULO[0], np.nan])
    lng = pd.Series([SAO_PAULO[1], SAO_PAULO[1]])
    distances = distance_km(lat, lng, RIO[0], RIO[1])
    assert distances.notna().tolist() == [True, False]


def test_aucune_colonne_posterieure_a_l_achat():
    for colonne in COLONNES_BRUTES:
        assert not colonne.startswith("apres_achat_")
        assert colonne not in {"delai_jours", "promesse_jours"}


def test_variables_insensibles_aux_informations_posterieures(commandes_brutes):
    modifiees = commandes_brutes.assign(
        delai_jours=99.0,
        promesse_jours=1.0,
        apres_achat_validation=pd.Timestamp("2020-01-01"),
        apres_achat_note_avis=1.0,
    )
    pd.testing.assert_frame_equal(construire_variables(commandes_brutes), construire_variables(modifiees))


def test_meme_resultat_commande_par_commande(commandes_brutes):
    une_par_une = pd.concat([construire_variables(commandes_brutes.iloc[[i]]) for i in range(len(commandes_brutes))])
    pd.testing.assert_frame_equal(construire_variables(commandes_brutes), une_par_une)


def test_variables_calculees(commandes_brutes):
    variables = construire_variables(commandes_brutes)
    assert list(variables.columns) == VARIABLES
    assert variables["meme_etat"].tolist() == [0, 1, 0]
    assert variables["jour_semaine_achat"].tolist() == [0, 4, 5]
    assert variables["distance_km"].isna().tolist() == [False, False, True]
