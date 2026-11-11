import numpy as np
import pandas as pd
import pytest

from olist_promesse.variables import distance_km

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
