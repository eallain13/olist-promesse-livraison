"""API de prévision : délai de livraison estimé et date promise pour une commande.

Lancement depuis la racine du dépôt : uvicorn olist_promesse.api:app
"""

from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from olist_promesse.prevision import VendeurInconnu, charger_modeles, prevoir


class Commande(BaseModel):
    """Commande telle que le site la connaît quand le client valide son panier."""

    vendeur: str = Field(min_length=1, description="identifiant du vendeur")
    code_postal_client: str = Field(pattern=r"^\d{5}$", description="cinq premiers chiffres du code postal")
    etat_client: str = Field(pattern=r"^[A-Z]{2}$", description="sigle de l'État, par exemple SP")
    prix_total: float = Field(ge=0, description="en réaux")
    fret_total: float = Field(ge=0, description="frais de port, en réaux")
    poids_total_g: float | None = Field(default=None, ge=0)
    volume_total_cm3: float | None = Field(default=None, ge=0)
    n_articles: int = Field(ge=1)
    categorie: str | None = Field(default=None, description="catégorie de l'article le plus cher")
    type_paiement: Literal["credit_card", "boleto", "voucher", "debit_card"]
    n_echeances: int = Field(ge=0)
    date_achat: datetime | None = Field(default=None, description="heure locale du Brésil, par défaut maintenant")


class Prevision(BaseModel):
    """Réponse de l'API."""

    delai_estime_jours: float
    date_livraison_estimee: date
    date_promise: date


def creer_application(modeles: dict | None = None) -> FastAPI:
    """Crée l'API. Sans modèles fournis (pour les tests), ils sont chargés depuis le disque au démarrage."""

    @asynccontextmanager
    async def cycle_de_vie(application: FastAPI):
        application.state.modeles = modeles if modeles is not None else charger_modeles()
        yield

    application = FastAPI(title="Promesse de livraison Olist", lifespan=cycle_de_vie)

    @application.get("/sante")
    def sante(request: Request) -> dict:
        modeles_charges = request.app.state.modeles
        return {
            "statut": "ok",
            "date_entrainement": modeles_charges["date_entrainement"].date(),
            "quantile_promesse": modeles_charges["quantile_promesse"],
        }

    @application.post("/prevision", response_model=Prevision)
    def prevision(commande: Commande, request: Request) -> dict:
        brute = {
            "order_purchase_timestamp": pd.Timestamp(commande.date_achat or datetime.now()).tz_localize(None),
            "seller_id": commande.vendeur,
            "customer_zip_code_prefix": commande.code_postal_client,
            "customer_state": commande.etat_client,
            "prix_total": commande.prix_total,
            "fret_total": commande.fret_total,
            "poids_total_g": commande.poids_total_g,
            "volume_total_cm3": commande.volume_total_cm3,
            "n_articles": commande.n_articles,
            "categorie_principale": commande.categorie,
            "type_paiement_principal": commande.type_paiement,
            "n_echeances": commande.n_echeances,
        }
        try:
            return prevoir(brute, request.app.state.modeles)
        except VendeurInconnu:
            raise HTTPException(status_code=422, detail=f"vendeur inconnu : {commande.vendeur}")

    return application


app = creer_application()
