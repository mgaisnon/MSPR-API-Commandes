# MSPR - API Commandes

![Build](https://img.shields.io/github/actions/workflow/status/mgaisnon/MSPR-API-Commandes/ci.yml?branch=main)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Docker Image](https://img.shields.io/docker/image-size/mgaisnon/mspr-api-commandes/latest)

API REST pour la gestion des commandes de l'application PayeTonKawa.

## 🚀 Stack technique
- Langage : Python 3.11
- Framework : FastAPI
- Base de données : MySQL
- ORM : SQLAlchemy + Pydantic
- Conteneurisation : Docker

## 🔧 Installation locale
```bash
docker compose up --build
````

API accessible sur : [http://localhost:8003/docs](http://localhost:8003/docs)

## 🔍 Endpoints principaux

* `GET /commandes` : Liste des commandes
* `POST /commandes` : Création d'une commande
* `GET /commandes/{id}` : Détails d'une commande
* `PUT /commandes/{id}` : Mise à jour d'une commande
* `DELETE /commandes/{id}` : Suppression d'une commande

## ⚙️ Variables d'environnement

```env
DATABASE_URL=mysql+pymysql://user:password@db-commandes:3306/commandes_db
```

## 📉 Tests

```bash
pytest --cov=app
```
