#!/bin/bash
# ===========================================
# Script de déploiement automatique
# SaaS Directory Submission Agent
# ===========================================

set -e

echo "🚀 Déploiement SaaS Directory Agent"
echo "===================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier Git
check_git() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        echo -e "${RED}❌ Ce dossier n'est pas un repo Git${NC}"
        echo "Exécutez: git init"
        exit 1
    fi
    echo -e "${GREEN}✅ Git initialisé${NC}"
}

# Vérifier les outils
check_tools() {
    echo ""
    echo "📦 Vérification des outils..."
    
    # Node.js
    if command -v node &> /dev/null; then
        echo -e "${GREEN}✅ Node.js $(node -v)${NC}"
    else
        echo -e "${RED}❌ Node.js non installé${NC}"
    fi
    
    # Python
    if command -v python &> /dev/null; then
        echo -e "${GREEN}✅ Python $(python --version)${NC}"
    else
        echo -e "${RED}❌ Python non installé${NC}"
    fi
    
    # Vercel CLI
    if command -v vercel &> /dev/null; then
        echo -e "${GREEN}✅ Vercel CLI installé${NC}"
    else
        echo -e "${YELLOW}⚠️ Vercel CLI non installé. Installation...${NC}"
        npm i -g vercel
    fi
    
    # Railway CLI (optionnel)
    if command -v railway &> /dev/null; then
        echo -e "${GREEN}✅ Railway CLI installé${NC}"
    else
        echo -e "${YELLOW}⚠️ Railway CLI non installé (optionnel)${NC}"
        echo "   Pour installer: npm i -g @railway/cli"
    fi
}

# Initialiser Git et pousser vers GitHub
setup_github() {
    echo ""
    echo "📤 Configuration GitHub..."
    
    # Vérifier si remote origin existe
    if git remote get-url origin > /dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        echo -e "${GREEN}✅ Remote origin configuré: $REMOTE_URL${NC}"
    else
        echo -e "${YELLOW}⚠️ Pas de remote origin configuré${NC}"
        echo ""
        read -p "Entrez l'URL de votre repo GitHub: " GITHUB_URL
        git remote add origin "$GITHUB_URL"
        echo -e "${GREEN}✅ Remote ajouté${NC}"
    fi
    
    # Commit si nécessaire
    if [[ -n $(git status --porcelain) ]]; then
        echo "📝 Commit des changements..."
        git add .
        git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # Push
    echo "🚀 Push vers GitHub..."
    git push -u origin main || git push -u origin master
    echo -e "${GREEN}✅ Code poussé sur GitHub${NC}"
}

# Déployer le Frontend sur Vercel
deploy_frontend() {
    echo ""
    echo "🎨 Déploiement Frontend sur Vercel..."
    
    cd frontend
    
    # Vérifier si le projet est lié à Vercel
    if [ -d ".vercel" ]; then
        echo "Projet déjà lié à Vercel"
    else
        echo "Liaison avec Vercel..."
        vercel link
    fi
    
    # Déployer
    echo "Déploiement en production..."
    vercel --prod
    
    cd ..
    echo -e "${GREEN}✅ Frontend déployé sur Vercel${NC}"
}

# Déployer le Backend sur Railway
deploy_backend_railway() {
    echo ""
    echo "🚂 Déploiement Backend sur Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo -e "${YELLOW}Railway CLI non installé. Installation...${NC}"
        npm i -g @railway/cli
    fi
    
    cd backend
    
    # Login si nécessaire
    railway whoami || railway login
    
    # Link au projet
    railway link || echo "Projet déjà lié ou création nécessaire"
    
    # Déployer
    railway up
    
    cd ..
    echo -e "${GREEN}✅ Backend déployé sur Railway${NC}"
}

# Menu principal
show_menu() {
    echo ""
    echo "Que voulez-vous déployer?"
    echo "1) Tout (GitHub + Vercel + Railway)"
    echo "2) GitHub seulement"
    echo "3) Frontend (Vercel) seulement"
    echo "4) Backend (Railway) seulement"
    echo "5) Vérifier les outils"
    echo "6) Quitter"
    echo ""
    read -p "Choix [1-6]: " choice
    
    case $choice in
        1)
            check_git
            check_tools
            setup_github
            deploy_frontend
            deploy_backend_railway
            ;;
        2)
            check_git
            setup_github
            ;;
        3)
            deploy_frontend
            ;;
        4)
            deploy_backend_railway
            ;;
        5)
            check_tools
            ;;
        6)
            echo "👋 Au revoir!"
            exit 0
            ;;
        *)
            echo -e "${RED}Choix invalide${NC}"
            show_menu
            ;;
    esac
}

# Résumé final
show_summary() {
    echo ""
    echo "===================================="
    echo "🎉 Déploiement terminé!"
    echo "===================================="
    echo ""
    echo "📱 Vos URLs:"
    echo "   Frontend: https://votre-projet.vercel.app"
    echo "   Backend:  https://votre-projet.up.railway.app"
    echo "   API Docs: https://votre-projet.up.railway.app/docs"
    echo ""
    echo "📝 Prochaines étapes:"
    echo "   1. Configurez VITE_API_URL sur Vercel"
    echo "   2. Ajoutez CORS_ORIGINS sur Railway"
    echo "   3. Vérifiez que tout fonctionne!"
    echo ""
}

# Exécution principale
main() {
    echo ""
    check_git
    show_menu
    show_summary
}

main
