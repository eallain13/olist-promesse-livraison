# Image de l'API : le code et ses dépendances, sans les données ni les modèles.
# Les modèles sont entraînés hors de l'image, puis montés au lancement (voir le README)
FROM python:3.12.16-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    OLIST_MODELES=/app/artifacts/modeles.joblib

WORKDIR /app

# Les dépendances sont installées dans une couche à part, elles restent en cache
# quand seul le code change
COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-deps . && rm -rf build

# L'API ne tourne pas en administrateur
RUN useradd --create-home api
USER api

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/sante')"]
CMD ["uvicorn", "olist_promesse.api:app", "--host", "0.0.0.0", "--port", "8000"]
