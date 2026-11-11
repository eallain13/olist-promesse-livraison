import pytest
from fastapi.testclient import TestClient

from olist_promesse.api import creer_application

CORPS = {
    "vendeur": "v1",
    "code_postal_client": "20000",
    "etat_client": "RJ",
    "prix_total": 129.9,
    "fret_total": 15.1,
    "poids_total_g": 800,
    "volume_total_cm3": 6000,
    "n_articles": 1,
    "categorie": "bed_bath_table",
    "type_paiement": "credit_card",
    "n_echeances": 3,
    "date_achat": "2018-08-15T10:30:00",
}


@pytest.fixture
def client(modeles_fictifs):
    with TestClient(creer_application(modeles_fictifs)) as client:
        yield client


def test_sante(client):
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"


def test_prevision(client):
    reponse = client.post("/prevision", json=CORPS)
    assert reponse.status_code == 200
    prevision = reponse.json()
    assert prevision["date_livraison_estimee"] <= prevision["date_promise"]


def test_date_d_achat_facultative(client):
    corps = {cle: valeur for cle, valeur in CORPS.items() if cle != "date_achat"}
    assert client.post("/prevision", json=corps).status_code == 200


@pytest.mark.parametrize("champ, valeur", [("prix_total", -5), ("code_postal_client", "2000"), ("type_paiement", "cheque")])
def test_donnees_invalides_refusees(client, champ, valeur):
    assert client.post("/prevision", json=CORPS | {champ: valeur}).status_code == 422


def test_vendeur_inconnu_refuse(client):
    reponse = client.post("/prevision", json=CORPS | {"vendeur": "inconnu"})
    assert reponse.status_code == 422
    assert "vendeur inconnu" in reponse.json()["detail"]
