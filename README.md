# Churn Baseline

Application de prediction du churn client telecom, basee sur un modele scikit-learn sauvegarde avec `joblib`.

Le projet contient :

- une API FastAPI pour l'authentification, la prediction unitaire et la prediction batch ;
- une interface Streamlit qui consomme l'API ;
- un notebook d'entrainement ;
- les artefacts de modele dans `models/`.

## Structure

```text
.
├── api/                         # Routes FastAPI, auth, schemas et utilitaires
├── core/                        # Configuration applicative
├── data/                        # Dataset Telco Customer Churn
├── models/                      # Modeles joblib
├── notebooks/                   # Notebook d'analyse et d'entrainement
├── streamlit/                   # Interface Streamlit
├── tests/                       # Tests API
├── main.py                      # Lancement local de l'API
├── pyproject.toml               # Dependances Python du projet complet
└── uv.lock                      # Lockfile uv
```

## Prerequis

- Python 3.11 ou plus recent
- `uv` pour installer les dependances du projet complet

Installation de `uv` si besoin :

```bash
pip install uv
```

## Installation locale

Depuis la racine du projet :

```bash
uv sync
```

Le modele charge par l'API est :

```text
models/baseline_model_bis.joblib
```

## Configuration

L'application lit les variables depuis un fichier `.env` a la racine ou depuis l'environnement.

Exemple minimal :

```env
SECRET_KEY=tutochurn
USERNAME=admin
DEMO_MODE=false
```

Variables utiles :

- `SECRET_KEY` : mot de passe utilise par `/login`.
- `USERNAME` : identifiant utilisateur, `admin` par defaut.
- `DEMO_MODE` : si `true`, l'API accepte les predictions sans token.
- `ACCESS_TOKEN_EXPIRE_DAYS` : duree de vie du token d'acces.
- `REFRESH_TOKEN_EXPIRE_DAYS` : duree de vie du refresh token.

## Lancer l'API

```bash
uv run python main.py
```

Ou directement :

```bash
uv run uvicorn api.app:app --host 127.0.0.1 --port 8000 --reload
```

Documentation interactive :

```text
http://127.0.0.1:8000/docs
```

Health check :

```bash
curl http://127.0.0.1:8000/health
```

## Authentification

Login :

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=tutochurn"
```

La reponse contient :

- `access_token`
- `refresh_token`
- `token_type`

Les routes de prediction attendent ensuite :

```text
Authorization: Bearer <access_token>
```

## Prediction unitaire

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Male",
    "SeniorCitizen": 1,
    "Partner": "No",
    "Dependents": "Yes",
    "tenure": 1,
    "PhoneService": "No",
    "MultipleLines": "No phone service",
    "InternetService": "DSL",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "No",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 18.54
  }'
```

## Routes API

| Methode | Route | Description |
| --- | --- | --- |
| `GET` | `/health` | Statut de l'API |
| `POST` | `/login` | Connexion et creation des tokens |
| `POST` | `/refresh` | Renouvellement des tokens |
| `POST` | `/predict` | Prediction pour un client |
| `POST` | `/predict-batch` | Prediction pour plusieurs clients |
| `POST` | `/upload-csv` | Lecture d'un CSV envoye |
| `GET` | `/model-info` | Informations et metriques du modele |

## Lancer Streamlit

Dans un premier terminal, lancer l'API.

Dans un second terminal :

```bash
uv run streamlit run streamlit/streamlit_app.py
```

Par defaut, l'interface appelle :

```text
http://localhost:8000
```

Pour cibler une autre API :

```bash
API_URL=https://mon-api.example.com uv run streamlit run streamlit/streamlit_app.py
```

Sur Streamlit Cloud, ajouter `API_URL` dans les secrets si l'API est hebergee ailleurs.

## Deploiement Streamlit Cloud

Le fichier `streamlit/requirements.txt` contient uniquement les dependances necessaires a l'interface Streamlit.

C'est volontaire : Streamlit Cloud detecte les fichiers de dependances pres du point d'entree avant ceux de la racine. Cela evite d'installer tout l'environnement ML/API, notamment TensorFlow, qui n'est pas necessaire a l'interface.

Configuration de deploiement :

- Repository : `GeeksterLab/Churn_baseline`
- Branch : `main`
- Main file path : `streamlit/streamlit_app.py`

## Tests

```bash
uv run pytest
```

Les tests couvrent notamment :

- le health check ;
- le login ;
- le refus d'une prediction sans token ;
- une prediction avec token.

## Notes

- Le modele est un pipeline scikit-learn charge depuis `models/baseline_model_bis.joblib`.
- Les colonnes attendues par l'API sont definies dans `api/schemas.py`.
- Le notebook `notebooks/notebook_churn.ipynb` contient le travail d'analyse et d'entrainement.
