# Churn Baseline

![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)
[![Click Here](https://img.shields.io/badge/Click%20Here-blue?style=for-the-badge)](https://churnbaseline.streamlit.app/)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571.svg?style=for-the-badge&logo=fastapi)
![NumPy](https://img.shields.io/badge/NumPy-013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white)
![Pandas](https://img.shields.io/badge/Pandas-150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![Google Drive](https://img.shields.io/badge/Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)

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
https://churn-baseline-916856991986.europe-west1.run.app
```

Pour cibler une autre API :

```bash
API_URL=http://localhost:8000 uv run streamlit run streamlit/streamlit_app.py
```

En local, tu peux aussi mettre l'URL dans `.env` :

```env
API_URL=https://churn-baseline-916856991986.europe-west1.run.app
```

Sur Streamlit Cloud, le fichier `.env` local n'est pas lu. Il faut ajouter `API_URL` dans les secrets Streamlit.

## Deploiement Streamlit Cloud

Le fichier `streamlit/requirements.txt` contient uniquement les dependances necessaires a l'interface Streamlit.

C'est volontaire : Streamlit Cloud detecte les fichiers de dependances pres du point d'entree avant ceux de la racine. Cela evite d'installer tout l'environnement ML/API, notamment TensorFlow, qui n'est pas necessaire a l'interface.

Streamlit Cloud lance uniquement l'interface Streamlit. Il ne demarre pas automatiquement l'API FastAPI du projet, meme si le code est dans le meme repository. L'API doit donc etre hebergee separement, par exemple sur Cloud Run, Azure App Service, Render ou un autre service capable d'exposer FastAPI.

Une fois l'API deployee, ajouter son URL dans les secrets Streamlit :

```toml
API_URL = "https://churn-baseline-916856991986.europe-west1.run.app"
```

L'URL de l'API est affichee dans la barre laterale, mais elle n'est pas modifiable par les visiteurs.

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
