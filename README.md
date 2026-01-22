# 🚀 SaaS Directory Submission Agent

[![Demo Mode](https://img.shields.io/badge/Demo-Ready-green)](.)
[![Docker](https://img.shields.io/badge/Docker-Required-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://reactjs.org/)

> **Agent intelligent d'automatisation pour la soumission de produits SaaS vers des annuaires en ligne**

---

## 📋 Table des matières

- [Aperçu du projet](#-aperçu-du-projet)
- [Démarrage rapide (2 minutes)](#-démarrage-rapide-2-minutes)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture technique](#-architecture-technique)
- [Stack technologique](#-stack-technologique)
- [Structure du projet](#-structure-du-projet)
- [API Documentation](#-api-documentation)

---

## 🎯 Aperçu du projet

Ce projet est un **agent d'automatisation intelligent** qui permet de soumettre automatiquement des produits SaaS à des centaines d'annuaires en ligne. Il utilise :

- **IA (LLM)** pour détecter et mapper les champs de formulaires automatiquement
- **Playwright** pour l'automatisation du navigateur
- **Système de queue** pour le traitement en arrière-plan avec retry automatique

### Cas d'utilisation

1. Un utilisateur ajoute son produit SaaS (nom, description, URL, logo)
2. L'agent détecte automatiquement les formulaires sur les sites d'annuaires
3. L'agent remplit et soumet les formulaires automatiquement
4. L'utilisateur peut suivre le statut de chaque soumission en temps réel

---

## ⚡ Démarrage rapide (2 minutes)

### Prérequis

- **Docker Desktop** installé et lancé : [Télécharger Docker](https://www.docker.com/products/docker-desktop/)
- **Git** installé

### Étapes

```bash
# 1. Cloner le repository
git clone https://github.com/eyabenhouria/saas-directory-agent.git
cd saas-directory-agent

# 2. Lancer l'application (tout est configuré, DEMO_MODE activé)
docker-compose up -d

# 3. Initialiser la base de données
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_data.py

# 4. Ouvrir dans le navigateur
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### ✅ C'est tout ! L'application est prête.

> **Note** : Le mode DEMO est activé par défaut. Toutes les fonctionnalités sont disponibles sans avoir besoin de clés API.

---

## 🌟 Fonctionnalités

| Fonctionnalité | Description | Status |
|----------------|-------------|--------|
| **Dashboard** | Vue d'ensemble avec statistiques en temps réel | ✅ |
| **Gestion des produits** | CRUD complet pour les produits SaaS | ✅ |
| **Annuaires** | Base de 20+ annuaires pré-configurés | ✅ |
| **Détection IA** | Analyse automatique des formulaires avec LLM | ✅ |
| **Soumission auto** | Remplissage et soumission automatiques | ✅ |
| **Suivi en temps réel** | Statuts: pending, running, success, failed | ✅ |
| **Retry automatique** | Réessai des soumissions échouées | ✅ |
| **Screenshots** | Capture après chaque soumission | ✅ |
| **API REST** | Documentation Swagger interactive | ✅ |

---

## 🏗️ Architecture technique

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + TypeScript)               │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────────┐  │
│  │Dashboard │ │ Products │ │Directories│ │   Submissions    │  │
│  └──────────┘ └──────────┘ └───────────┘ └──────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API (HTTP)
┌─────────────────────────────▼───────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      API Layer                            │  │
│  │  /products  /directories  /submissions  /analytics        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Services Layer                          │  │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐    │  │
│  │  │  Form Detector  │  │   Submission Worker          │    │  │
│  │  │  (LLM: Gemini)  │  │   (Background Queue)         │    │  │
│  │  └─────────────────┘  └─────────────────────────────┘    │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │        Browser Automation (Playwright)               │ │  │
│  │  │   - Page navigation, form filling, screenshot        │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  PostgreSQL  │     │    Redis     │     │  Playwright  │
│   Database   │     │    Cache     │     │   Browser    │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 🛠️ Stack technologique

### Frontend
| Technologie | Usage |
|-------------|-------|
| **React 18** | Framework UI |
| **TypeScript** | Typage statique |
| **Vite** | Build tool (ultra-rapide) |
| **TailwindCSS** | Styling utility-first |
| **React Query** | Data fetching & caching |
| **React Router v6** | Navigation SPA |
| **Recharts** | Graphiques et visualisations |
| **Axios** | Client HTTP |

### Backend
| Technologie | Usage |
|-------------|-------|
| **FastAPI** | Framework API (async) |
| **Python 3.11** | Langage backend |
| **SQLAlchemy 2.0** | ORM (async support) |
| **Alembic** | Migrations DB |
| **Pydantic v2** | Validation des données |
| **Playwright** | Automatisation navigateur |
| **Google Gemini** | LLM pour détection de formulaires |
| **Uvicorn** | Serveur ASGI |

### Infrastructure
| Technologie | Usage |
|-------------|-------|
| **Docker** | Containerisation |
| **Docker Compose** | Orchestration locale |
| **PostgreSQL 17** | Base de données |
| **Redis 7** | Cache & file d'attente |

---

## 📁 Structure du projet

```
saas-directory-agent/
├── frontend/                    # Application React
│   ├── src/
│   │   ├── components/          # Composants réutilisables
│   │   ├── pages/               # Pages de l'application
│   │   ├── services/            # Services API
│   │   ├── hooks/               # Custom React hooks
│   │   └── types/               # Types TypeScript
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # API FastAPI
│   ├── app/
│   │   ├── api/                 # Routes API
│   │   │   └── endpoints/       # Endpoints REST
│   │   ├── models/              # Modèles SQLAlchemy
│   │   ├── schemas/             # Schémas Pydantic
│   │   ├── services/            # Logique métier
│   │   │   ├── form_detector.py # Détection IA des formulaires
│   │   │   ├── submission_worker.py
│   │   │   └── browser_automation.py
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Connexion DB
│   │   └── main.py              # Point d'entrée
│   ├── alembic/                 # Migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml           # Orchestration Docker
├── .env.example                 # Variables d'environnement
└── README.md
```

---

## 📚 API Documentation

Une fois l'application lancée, accédez à la documentation interactive :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/products` | Liste des produits |
| `POST` | `/api/products` | Créer un produit |
| `GET` | `/api/directories` | Liste des annuaires |
| `POST` | `/api/submissions` | Lancer une soumission |
| `GET` | `/api/submissions` | Historique des soumissions |
| `GET` | `/api/analytics` | Statistiques |

---

## 🔧 Configuration avancée

### Variables d'environnement

Le fichier `.env` contient toutes les configurations. Les valeurs par défaut permettent de lancer l'application en mode DEMO :

```env
# Mode démo (pas besoin de clé API)
DEMO_MODE=true

# Ou avec une vraie clé API Gemini (gratuite)
DEMO_MODE=false
LLM_PROVIDER=gemini
GOOGLE_API_KEY=votre_clé_ici
```

### Obtenir une clé API Gemini (gratuit)

1. Aller sur https://makersuite.google.com/app/apikey
2. Se connecter avec un compte Google
3. Cliquer "Create API Key"
4. Copier la clé dans `.env`

---

## 🧪 Tests

```bash
# Tests backend
docker-compose exec backend pytest

# Tests frontend
cd frontend && npm test
```

---

## 📝 Points techniques clés

### 1. Détection intelligente des formulaires
Le service `form_detector.py` utilise un LLM (Gemini) pour :
- Analyser le HTML d'une page
- Identifier les champs de formulaire
- Mapper automatiquement les données du produit aux champs

### 2. Automatisation robuste
Le service `browser_automation.py` avec Playwright :
- Navigation headless
- Gestion des popups et modales
- Retry automatique en cas d'erreur
- Capture de screenshots

### 3. Architecture async
- FastAPI avec support async/await
- SQLAlchemy 2.0 avec asyncpg
- Traitement en arrière-plan non-bloquant

---

## 👤 Auteur

**Eya Benhouria**

- GitHub: [@eyabenhouria](https://github.com/eyabenhouria)

---

## 📄 Licence

MIT License
