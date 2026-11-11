"""Modèles de délai de livraison."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin


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
