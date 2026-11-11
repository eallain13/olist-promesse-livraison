"""Variables calculées à partir des attributs d'une commande."""

import numpy as np

RAYON_TERRE_KM = 6371.0


def distance_km(lat1, lng1, lat2, lng2):
    """Distance à vol d'oiseau entre deux points (formule de haversine).

    Accepte des nombres ou des colonnes (une coordonnée manquante donne une distance manquante).

    :param lat1: latitude du premier point, en degrés
    :param lng1: longitude du premier point, en degrés
    :param lat2: latitude du second point, en degrés
    :param lng2: longitude du second point, en degrés
    :return: distance en kilomètres
    """
    lat1, lng1, lat2, lng2 = (np.radians(x) for x in (lat1, lng1, lat2, lng2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2
    return 2 * RAYON_TERRE_KM * np.arcsin(np.sqrt(a))
