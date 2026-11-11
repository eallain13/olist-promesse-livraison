# Promesse de livraison Olist

Au moment de l'achat, la marketplace brésilienne Olist affiche au client une date de livraison
promise. Cette promesse est très prudente : elle limite les retards, mais annonce souvent un délai
bien plus long que le délai réel, ce qui peut décourager l'achat.

Ce projet estime le délai de livraison de chaque commande à partir des seules informations connues
au moment de l'achat, puis construit une promesse plus courte (à taux de retard maîtrisé). Le
modèle est servi par une API qui traite une commande à la fois.

## English summary
<!-- À rédiger au jalon 10, une fois les résultats connus. -->

## Données

*Brazilian E-Commerce Public Dataset by Olist* (Kaggle), licence CC BY-NC-SA 4.0 : environ
100 000 commandes passées entre 2016 et 2018, réparties dans 9 tables (commandes, articles,
produits, vendeurs, clients, géolocalisation, paiements, avis).

Les données ne sont pas incluses dans ce dépôt : voir [`data/README.md`](data/README.md) pour les
obtenir.

## Structure du dépôt

```
├── data/                  données Olist, non versionnées (voir data/README.md)
├── notebooks/             démarche analytique : exploration, protocole, résultats
├── sql/                   requêtes d'extraction (DuckDB)
├── src/olist_promesse/    code du projet : données, variables, entraînement, évaluation
└── tests/                 tests automatisés (pytest)
```

La structure sera complétée au fil du projet (API, Docker, intégration continue).

## Installation

Prérequis : Python 3.12.

```bash
git clone https://github.com/eallain13/olist-promesse-livraison.git
cd olist-promesse-livraison
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

Placer ensuite les données dans `data/raw/` en suivant [`data/README.md`](data/README.md).

`requirements.txt` contient les dépendances du code, `requirements-dev.txt` y ajoute les outils de
développement (Jupyter, visualisation, tests).
`pip install -e .` installe le code du projet en mode éditable : les modifications de `src/` sont prises en compte sans réinstallation.

## Avancement

- [x] Mise en place du dépôt et de l'environnement
- [x] Extraction des données (SQL)
- [x] Analyse exploratoire
- [ ] Protocole de validation et bases de comparaison
- [ ] Variables et modèles
- [ ] Promesse de livraison (régression quantile)
- [ ] Interprétation et analyse des erreurs
- [ ] API, tests et Docker
- [ ] Intégration continue et publication

## Licence

Code sous licence MIT (voir [`LICENSE`](LICENSE)). Données sous licence
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), propriété d'Olist.
