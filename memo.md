# Training de modèles de machine learning, AI et NLP

| Projet | Ce qu'il teste |
| --- | --- |
| 1 — Churn client | Classification, recall/precision, business impact |
| 2 — Prix immobilier | Régression, RMSE/MAE, outliers |
| 3 — Détection de fraude | Imbalance sévère, threshold tuning |
| 4 — Vectorisation de textes | NLP, embeddings, vector search, chunks |
| 5 — Analyse de logs | Pandas, SQL/PostgreSQL, anomaly detection |
| 4 bis — Classification NLP | TF-IDF, sklearn pipeline, métriques NLP |

## Structure exercices

Pour chaque projet l'exercice est le même:

### ML

- charger les données
- nettoyer les valeurs manquantes
- faire 2-3 visualisations
- encoder les variables
- entraîner un modèle baseline
- évaluer avec les bonnes métriques
- expliquer ce que tu ferais ensuite

### API

5 endpoints sur le modèle churn que tu viens d'entraîner :

- GET  /health          → est-ce que l'API tourne ?
- POST /predict         → prédiction pour un client
- POST /predict-batch   → prédiction pour plusieurs clients
- POST /upload          → upload d'un CSV pour prédiction en masse
- GET  /model-info      → infos sur le modèle chargé

## Briefing Projet 1 — Churn Client

### Le contexte business

Imagine que tu es ML engineer dans une telco (Orange, SFR...). Le directeur commercial te dit :

"On perd 200 clients par mois. Chaque client vaut 400€/an. Trouve-moi ceux qui vont partir avant qu'ils partent."

C'est ça le churn. **Prédire qui va partir pour agir avant**. Pas après.
Ce que ça implique pour toi en tant que ML engineer :

Ce n'est pas un problème de précision maximale. C'est un problème de recall
Rater un churner (faux négatif) = perdre 400€. Alerter un client fidèle (faux positif) = lui envoyer une promo inutile. Le coût n'est pas symétrique.
Le recruteur va te poser cette question. Tu dois avoir la réponse sans hésiter.

### Le dataset

- **Telco Customer Churn — IBM Dataset**

```bash
uv run kaggle datasets download -d blastchar/telco-customer-churn -p 1_churn/data --unzip
```

- **Ce que tu vas trouver dedans** :
  - 7 043 clients, 21 colonnes
  - Cible : Churn (Yes/No)
  - Variables : tenure, contrat, services souscrits, montant mensuel...
  - Imbalance légère : ~26% de churners
