"""Protocole d'évaluation : découpage temporel glissant et métriques."""

import numpy as np
import pandas as pd
from sklearn.base import clone

CIBLE = "delai_jours"

# Mois servant à comparer les modèles (validation), puis mois réservés à l'évaluation finale (test)
MOIS_VALIDATION = pd.period_range("2017-11", "2018-04", freq="M")
MOIS_TEST = pd.period_range("2018-05", "2018-07", freq="M")


def date_livraison(commandes: pd.DataFrame) -> pd.Series:
    """Date et heure de livraison, reconstituées à partir de la date d'achat et du délai."""
    return commandes["order_purchase_timestamp"] + pd.to_timedelta(commandes[CIBLE], unit="D")


def decoupage_mensuel(commandes: pd.DataFrame, mois: pd.Period) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare les commandes comme si le modèle était réentraîné le 1er du mois évalué.

    :param commandes: commandes retenues
    :param mois: mois dont on évalue les commandes
    :return: commandes d'entraînement (déjà livrées le 1er du mois) et commandes achetées pendant le mois
    """
    debut, fin = mois.start_time, (mois + 1).start_time
    achat = commandes["order_purchase_timestamp"]
    entrainement = commandes[date_livraison(commandes) < debut]
    evaluation = commandes[(achat >= debut) & (achat < fin)]
    return entrainement, evaluation


def predire_par_mois(modele, commandes: pd.DataFrame, mois, variables: list[str]) -> pd.Series:
    """Prédit chaque mois avec un modèle entraîné sur les seules commandes livrées avant ce mois.

    :param modele: estimateur scikit-learn (il est cloné, puis entraîné une fois par mois)
    :param commandes: commandes retenues
    :param mois: mois à prédire
    :param variables: colonnes données au modèle
    :return: prédictions hors échantillon, indexées comme les commandes évaluées
    """
    predictions = []
    for m in mois:
        entrainement, evaluation = decoupage_mensuel(commandes, m)
        ajuste = clone(modele).fit(entrainement[variables], entrainement[CIBLE])
        predictions.append(pd.Series(ajuste.predict(evaluation[variables]), index=evaluation.index))
    return pd.concat(predictions)


def date_promise(achat: pd.Series, promesse_jours: pd.Series) -> pd.Series:
    """Jour promis au client"""
    return (achat + pd.to_timedelta(promesse_jours, unit="D")).dt.round("s").dt.normalize()


def en_retard(commandes: pd.DataFrame, promesse_jours: pd.Series) -> pd.Series:
    """Vrai si la commande est livrée après le jour promis."""
    commandes = commandes.loc[promesse_jours.index]
    jour_livraison = date_livraison(commandes).dt.round("s").dt.normalize()
    return jour_livraison > date_promise(commandes["order_purchase_timestamp"], promesse_jours)


def resumer_estimation(commandes: pd.DataFrame, prediction: pd.Series) -> pd.Series:
    """MAE et erreur médiane, en jours (erreur positive : le modèle surestime le délai)."""
    erreur = prediction - commandes.loc[prediction.index, CIBLE]
    return pd.Series({"MAE (j)": erreur.abs().mean(), "erreur médiane (j)": erreur.median()})


def resumer_promesse(commandes: pd.DataFrame, promesse_jours: pd.Series) -> pd.Series:
    """Taux de retard et délai promis moyen, mesuré entre l'achat et le début du jour promis."""
    achat = commandes.loc[promesse_jours.index, "order_purchase_timestamp"]
    delai_promis = (date_promise(achat, promesse_jours) - achat).dt.total_seconds() / 86400
    return pd.Series({
        "taux de retard (%)": 100 * en_retard(commandes, promesse_jours).mean(),
        "délai promis moyen (j)": delai_promis.mean(),
    })


def par_mois(commandes: pd.DataFrame, prediction: pd.Series, resumer) -> pd.DataFrame:
    """Applique une fonction de résumé à chaque mois évalué, puis à l'ensemble de ces mois."""
    mois = commandes.loc[prediction.index, "order_purchase_timestamp"].dt.to_period("M")
    lignes = {str(m): resumer(commandes, prediction[mois == m]) for m in sorted(mois.unique())}
    lignes["ensemble"] = resumer(commandes, prediction)
    return pd.DataFrame(lignes).T


def courbe_promesse(modele, commandes: pd.DataFrame, mois, variables: list[str], quantiles,
                    parametre: str = "quantile") -> pd.DataFrame:
    """Taux de retard et délai promis moyen obtenus en visant chacun des quantiles donnés.

    :param modele: estimateur dont un paramètre fixe le quantile prédit
    :param quantiles: quantiles visés
    :param parametre: nom de ce paramètre dans le modèle
    :return: une ligne par quantile visé
    """
    lignes = {}
    for q in quantiles:
        promesse = predire_par_mois(clone(modele).set_params(**{parametre: q}), commandes, mois, variables)
        lignes[q] = resumer_promesse(commandes, promesse)
    return pd.DataFrame(lignes).T.rename_axis("quantile visé")


def delai_promis_a_retard(courbe: pd.DataFrame, taux_de_retard: float) -> float:
    """Délai promis moyen lu sur la courbe pour un taux de retard donné (interpolation linéaire)."""
    courbe = courbe.sort_values("taux de retard (%)")
    return float(np.interp(taux_de_retard, courbe["taux de retard (%)"], courbe["délai promis moyen (j)"]))
