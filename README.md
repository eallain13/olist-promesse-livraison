# Promesse de livraison Olist

[![Intégration continue](https://github.com/eallain13/olist-promesse-livraison/actions/workflows/integration-continue.yml/badge.svg)](https://github.com/eallain13/olist-promesse-livraison/actions/workflows/integration-continue.yml)

Estimer le délai de livraison d'une commande au moment de l'achat, et promettre au client une date plus
proche que celle d'Olist, sans plus de retards.

## English summary

Olist, a Brazilian marketplace, shows each customer a delivery date at checkout. Its promise is
cautious: orders arrive in 12.9 days on average, while 24.2 days are promised. This project estimates
the delivery time from information available at purchase time only, and builds a shorter promise
with quantile regression (gradient boosting), served by a FastAPI API in a Docker container.

- **Result**: on the held-out test months (May–July 2018), at the same late-delivery rate as Olist
  (3.9 %), the promised lead time is **12 % shorter** (20.6 vs 23.4 days). The delivery-time MAE is
  4.1 days, 10 % below a per-route median baseline.
- **Method**: monthly retraining simulated on already-delivered orders only (a naive split
  understates the late rate), leakage-proof features enforced by tests, promises compared at equal
  late rate, and test months opened only once.
- **Limits**: during unpredictable shocks (e.g., Black Friday), the model barely
  matches Olist, and the promise quantile chosen on difficult validation months proved too cautious
  on the calmer test months.

Code, notebooks and documentation are in French.

## Le problème

Au moment de l'achat, Olist affiche une date de livraison promise. Elle est très prudente : 24,2 jours
promis en moyenne pour 12,9 jours réels. Cette prudence a une raison, car un retard coûte cher : la
note moyenne des clients tombe de 4,3 à 2,2 étoiles. Mais une promesse trop longue peut aussi
décourager l'achat.

L'objectif est donc double :
- estimer le délai de chaque commande, à partir des seules informations connues quand le client
  valide son panier
- promettre une date plus proche que celle d'Olist, à taux de retard égal.

## Résultats

Sur les mois de test (mai à juillet 2018), ouverts une seule fois après toutes les décisions :

| | Promesse Olist | Règle par trajet | Modèle |
|---|---|---|---|
| **Délai promis** au taux de retard d'Olist (3,86 %) | 23,4 j | 21,6 j | **20,6 j** |
| **MAE** de l'estimation du délai | – | 4,57 j | **4,13 j** |

La règle par trajet promet le quantile du délai observé entre l'État du vendeur et celui du client :
c'est la référence sans machine learning. À fiabilité égale, la promesse du modèle est 12 % plus
courte que celle d'Olist, et un jour plus courte que celle de la règle simple.

Ce résultat a des limites, détaillées dans les notebooks :
- le gain dépend de la période : sur les mois de validation, plus difficiles (Black Friday,
  février-mars 2018), le modèle égale à peine Olist (23,9 contre 24,3 jours promis). Olist anticipe le
  pic des fêtes quand le modèle, qui n'en a jamais vu, ne le peut pas
- le niveau de la promesse est délicat à choisir à l'avance : le quantile retenu sur la validation
  (0,963) s'est révélé trop prudent sur les mois de test, plus calmes (1,5 % de retard pour
  26,7 jours). Recalibrer chaque mois sur le passé fait pire, car le taux de retard dépend de chocs
  imprévisibles, qui le sont pour Olist aussi (de 1,2 % à 19,2 % selon les mois).

## Démarche

| Notebook | Question | Ce qu'il établit |
|---|---|---|
| [exploration](notebooks/exploration.ipynb) | Quelles commandes garder ? | 88 692 commandes retenues. Les données d'août 2018 ne contiennent que les livraisons rapides : la période s'arrête fin juillet. Le retard se compte au jour près. |
| [protocole](notebooks/protocole.ipynb) | Comment évaluer honnêtement ? | Un réentraînement simulé chaque mois, sur les seules commandes déjà livrées. Une variante naïve annonce 9,1 % de retard au lieu de 11,5 %. Une règle par trajet égale déjà Olist. |
| [variables](notebooks/variables.ipynb) | Que peut voir le modèle ? | 16 colonnes connues à l'achat, une colonne suspecte vérifiée puis exclue, un encodage du vendeur hors pli, sans fuite. |
| [modeles](notebooks/modeles.ipynb) | Quel modèle d'estimation ? | Gradient boosting à perte absolue : MAE de 6,12 contre 6,44 jours sur la validation. La dérive coûte 2 jours de MAE, qu'une validation croisée classique aurait masqués. |
| [promesse](notebooks/promesse.ipynb) | Quelle promesse, à quel niveau ? | Régression quantile, comparée à taux de retard égal, choix du quantile, évaluation finale sur le test. |
| [interpretation](notebooks/interpretation.ipynb) | Qu'a appris le modèle, et où échoue-t-il ? | La géographie domine. L'erreur vient des incidents. Les retards se concentrent dans le temps, et la fiabilité varie selon les régions. |

Quatre choix de méthode traversent le projet :
- une règle anti-fuite vérifiée par des tests : modifier une information postérieure à l'achat,
  la cible comprise, ne doit changer aucune variable
- une évaluation qui simule la production : chaque mois est prédit par un modèle qui ne connaît
  que le passé déjà observé
- des promesses comparées à taux de retard égal, jamais sur un seul point car sinon, on peut toujours
  promettre plus court en acceptant plus de retards
- des mois de test ouverts une seule fois, après le choix du modèle et du quantile.

## Structure du dépôt

```
├── .github/workflows/     intégration continue : tests et image Docker à chaque envoi
├── data/                  données Olist, non versionnées (voir data/README.md)
├── notebooks/             démarche analytique, de l'exploration à l'interprétation
├── sql/                   requêtes d'extraction (DuckDB)
├── src/olist_promesse/    code du projet
├── tests/                 tests automatisés (pytest)
├── Dockerfile             image de l'API
└── requirements*.txt      dépendances de l'API, de l'entraînement et du développement
```

| Module | Rôle |
|---|---|
| `donnees.py` | extraction SQL et sélection des commandes |
| `variables.py` | colonnes autorisées et variables calculées commande par commande |
| `modeles.py` | préparation des variables, gradient boosting, promesse, référence par groupe |
| `evaluation.py` | découpage mensuel, métriques, courbes délai promis – taux de retard |
| `entrainement.py` | entraînement des modèles finaux et tables de correspondance de l'API |
| `prevision.py`, `api.py` | prévision pour une commande, API FastAPI |

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

## Utilisation

```bash
python -m olist_promesse.entrainement   # entraîne les modèles finaux (artifacts/modeles.joblib)
uvicorn olist_promesse.api:app          # lance l'API sur http://127.0.0.1:8000
```

L'API reçoit une commande telle que le site la connaît au moment de l'achat, et renvoie le délai
estimé, la date de livraison estimée et la date promise. Sa documentation interactive est disponible
sur http://127.0.0.1:8000/docs.

```bash
curl -X POST http://127.0.0.1:8000/prevision -H "Content-Type: application/json" -d '{
  "vendeur": "de0c78824586e9a5f5f04fd84e25df39", "code_postal_client": "22793", "etat_client": "RJ",
  "prix_total": 101.9, "fret_total": 15.81, "poids_total_g": 400, "volume_total_cm3": 12000,
  "n_articles": 1, "categorie": "pet_shop", "type_paiement": "credit_card", "n_echeances": 2,
  "date_achat": "2018-07-31T23:54:20"
}'
```

```json
{"delai_estime_jours": 8.3, "date_livraison_estimee": "2018-08-09", "date_promise": "2018-08-29"}
```

### Avec Docker

```bash
python -m olist_promesse.entrainement   # les modèles sont entraînés hors de l'image
docker build -t olist-promesse .
docker run --rm -p 8000:8000 -v "$(pwd)/artifacts:/app/artifacts:ro" olist-promesse
```

L'image ne contient ni les données ni les modèles : le fichier `artifacts/modeles.joblib` est monté
en lecture seule au lancement.

## Tests

```bash
pytest -q
```

35 tests vérifient la sélection des commandes, la règle anti-fuite, la cohérence entre une commande
seule (API) et un historique (entraînement), le protocole d'évaluation et l'API. Sans les données,
30 d'entre eux s'exécutent sur des commandes fictives : c'est ce que fait l'intégration continue à
chaque envoi.

## Limites et pistes

- Le calendrier : intégrer les fêtes et le Black Friday demande plusieurs années d'historique, ici
  les données n'en couvrent qu'une.
- Le niveau de la promesse : en production, suivre le taux de retard réel sur les commandes
  livrées, et l'ajuster avec les équipes métier, éventuellement par région (le Nord subit 22 % de
  retard avec un quantile unique).
- La période de test ne couvre que trois mois calmes : il faudrait une année complète pour
  conclure sur toutes les saisons.
- Cinq variables n'apportent rien (prix, poids, volume, nombre d'articles et d'échéances) : elles
  seraient à retirer dans une prochaine version, après validation sur de nouvelles données.

## Données et licence

*Brazilian E-Commerce Public Dataset by Olist* (Kaggle) : environ 100 000 commandes passées entre
2016 et 2018, réparties dans 9 tables. Les données, sous licence
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) et propriété d'Olist, ne sont
pas incluses dans ce dépôt : voir [`data/README.md`](data/README.md) pour les obtenir.

Code sous licence MIT (voir [`LICENSE`](LICENSE)).
