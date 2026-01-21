# 🚀 Guide de Déploiement - GitHub & Vercel

Ce guide vous explique comment déployer le SaaS Directory Submission Agent sur GitHub et Vercel.

## 📋 Architecture de Déploiement

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                        │
│                    github.com/votre-user/saas-directory-agent   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌─────────────────────┐       ┌─────────────────────────┐
│   Vercel (Frontend) │       │   Railway/Render/Fly.io │
│   React + Vite      │       │   FastAPI + PostgreSQL  │
│   vercel.com        │       │   (Backend)             │
└─────────────────────┘       └─────────────────────────┘
```

> ⚠️ **Note**: Vercel est optimisé pour les frontends. Pour le backend FastAPI, nous utiliserons **Railway**, **Render**, ou **Fly.io**.

---

## 🔧 Partie 1: Préparation du Code

### 1.1 Initialiser Git

```bash
cd saas-directory-agent
git init
git add .
git commit -m "Initial commit - SaaS Directory Submission Agent"
```

### 1.2 Créer le Repository GitHub

1. Allez sur [github.com/new](https://github.com/new)
2. Nom du repo: `saas-directory-agent`
3. Description: "Automated SaaS directory submission agent with AI-powered form detection"
4. Visibilité: Public ou Private
5. Ne pas initialiser avec README (on en a déjà un)

### 1.3 Pousser vers GitHub

```bash
git remote add origin https://github.com/VOTRE_USERNAME/saas-directory-agent.git
git branch -M main
git push -u origin main
```

---

## 🎨 Partie 2: Déploiement Frontend sur Vercel

### 2.1 Configuration Vercel

Le fichier `vercel.json` à la racine du frontend configure le déploiement:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://votre-backend.railway.app/api/$1" }
  ]
}
```

### 2.2 Déployer sur Vercel

**Option A: Via l'interface web**

1. Allez sur [vercel.com](https://vercel.com) et connectez-vous avec GitHub
2. Cliquez sur **"Add New Project"**
3. Importez le repo `saas-directory-agent`
4. Configurez:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Ajoutez les variables d'environnement:
   - `VITE_API_URL`: URL de votre backend (à ajouter après déploiement backend)
6. Cliquez sur **"Deploy"**

**Option B: Via CLI**

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer depuis le dossier frontend
cd frontend
vercel

# Pour la production
vercel --prod
```

### 2.3 Domaine Personnalisé (Optionnel)

1. Dans le dashboard Vercel, allez dans **Settings > Domains**
2. Ajoutez votre domaine: `app.genie-ops.com`
3. Configurez les DNS chez votre registrar

---

## 🖥️ Partie 3: Déploiement Backend

### Option A: Railway (Recommandé) 🚂

**Railway** offre PostgreSQL gratuit et supporte Python/FastAPI.

#### 3.1 Créer un compte Railway

1. Allez sur [railway.app](https://railway.app)
2. Connectez-vous avec GitHub

#### 3.2 Créer le projet

1. Cliquez sur **"New Project"**
2. Sélectionnez **"Deploy from GitHub repo"**
3. Choisissez `saas-directory-agent`
4. Railway détectera automatiquement le Dockerfile

#### 3.3 Ajouter PostgreSQL

1. Dans votre projet, cliquez sur **"+ New"**
2. Sélectionnez **"Database" > "PostgreSQL"**
3. Railway crée automatiquement la variable `DATABASE_URL`

#### 3.4 Configurer les variables d'environnement

Dans **Settings > Variables**, ajoutez:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
OPENAI_API_KEY=sk-your-openai-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
BROWSER_HEADLESS=true
MAX_CONCURRENT_SUBMISSIONS=3
CORS_ORIGINS=https://votre-app.vercel.app
```

#### 3.5 Configurer le service

Créez `railway.json` dans le dossier backend:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && python seed_data.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### 3.6 Déployer

```bash
# Railway déploie automatiquement à chaque push
git push origin main
```

Votre backend sera accessible à: `https://saas-directory-agent-production.up.railway.app`

---

### Option B: Render 🎨

#### 3.1 Configuration

Créez `render.yaml` à la racine:

```yaml
services:
  - type: web
    name: saas-directory-api
    env: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: saas-directory-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: LLM_PROVIDER
        value: openai
      - key: BROWSER_HEADLESS
        value: "true"

databases:
  - name: saas-directory-db
    plan: free
    databaseName: saas_directory
```

#### 3.2 Déployer sur Render

1. Allez sur [render.com](https://render.com)
2. Connectez-vous avec GitHub
3. **New > Blueprint**
4. Sélectionnez votre repo
5. Render déploiera automatiquement

---

### Option C: Fly.io 🪰

#### 3.1 Installer Fly CLI

```bash
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Ou avec npm
npm install -g flyctl
```

#### 3.2 Créer l'app

```bash
cd backend
fly auth login
fly launch --name saas-directory-api
```

#### 3.3 Ajouter PostgreSQL

```bash
fly postgres create --name saas-directory-db
fly postgres attach saas-directory-db
```

#### 3.4 Configurer les secrets

```bash
fly secrets set OPENAI_API_KEY=sk-your-key
fly secrets set LLM_PROVIDER=openai
fly secrets set LLM_MODEL=gpt-4o
fly secrets set BROWSER_HEADLESS=true
```

#### 3.5 Déployer

```bash
fly deploy
```

---

## 🔗 Partie 4: Connecter Frontend et Backend

### 4.1 Mettre à jour Vercel

Après le déploiement du backend, retournez sur Vercel:

1. **Settings > Environment Variables**
2. Ajoutez/Modifiez:
   ```
   VITE_API_URL=https://votre-backend.railway.app
   ```
3. **Redéployez** le frontend

### 4.2 Configurer CORS sur le Backend

Assurez-vous que le backend accepte les requêtes du frontend. Dans les variables Railway/Render:

```
CORS_ORIGINS=https://saas-directory-agent.vercel.app
```

---

## 📊 Partie 5: Vérification du Déploiement

### 5.1 Tester le Backend

```bash
# Vérifier que l'API répond
curl https://votre-backend.railway.app/health

# Vérifier la documentation
# Ouvrez: https://votre-backend.railway.app/docs
```

### 5.2 Tester le Frontend

1. Ouvrez votre URL Vercel: `https://saas-directory-agent.vercel.app`
2. Vérifiez que le Dashboard charge
3. Testez l'ajout d'un produit SaaS

---

## 🔄 Partie 6: CI/CD Automatique

### GitHub Actions

Créez `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: saas-directory-api
```

### Configurer les Secrets GitHub

1. Allez dans votre repo GitHub > **Settings > Secrets and variables > Actions**
2. Ajoutez:
   - `VERCEL_TOKEN`: Depuis [vercel.com/account/tokens](https://vercel.com/account/tokens)
   - `VERCEL_ORG_ID`: Dans `.vercel/project.json` après `vercel link`
   - `VERCEL_PROJECT_ID`: Dans `.vercel/project.json`
   - `RAILWAY_TOKEN`: Depuis Railway > Account Settings > Tokens

---

## 💰 Coûts Estimés

| Service | Plan Gratuit | Plan Pro |
|---------|--------------|----------|
| **Vercel** | 100GB bandwidth/mois | $20/mois |
| **Railway** | $5 crédit/mois | Pay-as-you-go |
| **Render** | 750h/mois | $7/mois |
| **PostgreSQL** | 1GB (Railway/Render) | Variable |
| **OpenAI API** | Pay-per-use | ~$0.01/requête |

---

## 🛠️ Dépannage

### Erreur CORS
```
Access to fetch has been blocked by CORS policy
```
**Solution**: Vérifiez `CORS_ORIGINS` dans les variables du backend.

### Erreur de connexion DB
```
Connection refused to PostgreSQL
```
**Solution**: Vérifiez que `DATABASE_URL` est correctement configurée.

### Build Frontend échoue
```
Module not found
```
**Solution**: Vérifiez que `npm install` s'exécute avant le build.

### Playwright ne fonctionne pas
```
Browser not found
```
**Solution**: Sur les hébergeurs serverless, utilisez une image Docker avec Playwright pré-installé.

---

## 📱 URLs Finales

Après déploiement, vous aurez:

| Service | URL |
|---------|-----|
| **Frontend** | `https://saas-directory-agent.vercel.app` |
| **Backend API** | `https://saas-directory-api.railway.app` |
| **API Docs** | `https://saas-directory-api.railway.app/docs` |
| **GitHub Repo** | `https://github.com/VOTRE_USER/saas-directory-agent` |

---

## ✅ Checklist de Déploiement

- [ ] Code poussé sur GitHub
- [ ] Backend déployé (Railway/Render/Fly.io)
- [ ] PostgreSQL configuré
- [ ] Variables d'environnement définies (OPENAI_API_KEY, etc.)
- [ ] Migrations exécutées (`alembic upgrade head`)
- [ ] Données initiales chargées (`python seed_data.py`)
- [ ] Frontend déployé sur Vercel
- [ ] VITE_API_URL configuré sur Vercel
- [ ] CORS configuré sur le backend
- [ ] Tests de bout en bout réussis

---

🎉 **Félicitations!** Votre SaaS Directory Submission Agent est maintenant en production!
