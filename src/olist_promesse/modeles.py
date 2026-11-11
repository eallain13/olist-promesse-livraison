"""Modèles de délai de livraison."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OrdinalEncoder, TargetEncoder
from sklearn.ensemble import HistGradientBoostingRegressor

from olist_promesse.variables import (
    VARIABLE_VENDEUR,
    VARIABLES_CATEGORIELLES,
    VARIABLES_NUMERIQUES,
    construire_variables,
)


class QuantileParGroupe(RegressorMixin, BaseEstimator):
    """Prédit un quantile du délai observé dans le groupe de la commande.

    Les groupes sont essayés du plus précis au plus large (un groupe trop petit ou inconnu passe la
    main au niveau suivant, puis au quantile de toutes les commandes).

    :param niveaux: listes de colonnes définissant les groupes, du plus précis au plus large
    :param quantile: quantile prédit (0,5 pour la médiane)
    :param effectif_min: nombre minimal de commandes d'entraînement pour utiliser un groupe
    """

    def __init__(self, niveaux=(), quantile=0.5, effectif_min=30):
        self.niveaux = niveaux
        self.quantile = quantile
        self.effectif_min = effectif_min

    def fit(self, X, y):
        y = pd.Series(np.asarray(y, dtype=float), index=X.index)
        self.global_ = y.quantile(self.quantile)
        self.tables_ = []
        for colonnes in self.niveaux:
            groupes = y.groupby([X[c] for c in colonnes])
            table = groupes.quantile(self.quantile)[groupes.size() >= self.effectif_min]
            self.tables_.append((list(colonnes), table))
        return self

    def predict(self, X):
        prediction = pd.Series(np.nan, index=X.index)
        for colonnes, table in self.tables_:
            cles = pd.MultiIndex.from_frame(X[colonnes]) if len(colonnes) > 1 else X[colonnes[0]]
            prediction = prediction.fillna(pd.Series(table.reindex(cles).to_numpy(), index=X.index))
        return prediction.fillna(self.global_).to_numpy()


def preparation() -> Pipeline:
    """Transforme les colonnes brutes d'une commande en variables numériques pour le modèle.

    Les catégories deviennent des codes entiers (une catégorie inconnue à l'entraînement devient une
    valeur manquante). Le vendeur est remplacé par son délai moyen lissé, appris sur l'entraînement :
    pour les commandes d'entraînement, ce délai est calculé hors pli, sans la commande elle-même.
    """
    encodage = ColumnTransformer(
        [
            ("numeriques", "passthrough", VARIABLES_NUMERIQUES),
            (
                "categorielles",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan),
                VARIABLES_CATEGORIELLES,
            ),
            (
                "vendeur",
                TargetEncoder(target_type="continuous", cv=KFold(n_splits=5, shuffle=True, random_state=0)),
                [VARIABLE_VENDEUR],
            ),
        ],
        verbose_feature_names_out=False,
    )
    return Pipeline([
        ("variables", FunctionTransformer(construire_variables)),
        ("encodage", encodage),
    ]).set_output(transform="pandas")


def modele_gradient_boosting(**parametres) -> Pipeline:
    """Pipeline complet : préparation des colonnes brutes, puis gradient boosting.

    Par défaut, le modèle minimise l'erreur absolue et prédit donc le délai médian. Les paramètres
    donnés remplacent les réglages par défaut (par exemple loss="quantile" et quantile=0.9 pour
    promettre une date).
    """
    reglages = {"loss": "absolute_error", "categorical_features": VARIABLES_CATEGORIELLES, "random_state": 0}
    return Pipeline([
        ("preparation", preparation()),
        ("modele", HistGradientBoostingRegressor(**(reglages | parametres))),
    ])
