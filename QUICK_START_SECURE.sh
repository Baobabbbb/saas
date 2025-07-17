#!/bin/bash
# SEEDANCE - Lancement avec vérifications et diagnostics
# Version améliorée avec tests de connectivité

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   🚀 SEEDANCE - LANCEMENT SÉCURISÉ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Variables
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAAS_DIR="$BASE_DIR/saas"
FRONTEND_DIR="$BASE_DIR/frontend"

# Déterminer la commande Python
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo -e "${CYAN}🔍 Vérifications préalables...${NC}"

# Vérification 1: Fichier .env
if [ ! -f "$SAAS_DIR/.env" ]; then
    echo -e "${RED}❌ Fichier .env manquant dans $SAAS_DIR${NC}"
    echo -e "${YELLOW}   Créez le fichier .env avec vos clés API${NC}"
    exit 1
fi

# Vérification 2: Clés API essentielles
echo -e "${CYAN}🔑 Vérification des clés API...${NC}"
source "$SAAS_DIR/.env" 2>/dev/null || true

if [[ -z "$OPENAI_API_KEY" || "$OPENAI_API_KEY" == "sk-votre"* ]]; then
    echo -e "${RED}❌ Clé OpenAI manquante ou invalide${NC}"
    exit 1
fi

if [[ -z "$WAVESPEED_API_KEY" || "$WAVESPEED_API_KEY" == "votre_"* ]]; then
    echo -e "${RED}❌ Clé Wavespeed manquante ou invalide${NC}"
    exit 1
fi

if [[ -z "$FAL_API_KEY" || "$FAL_API_KEY" == "votre_"* ]]; then
    echo -e "${RED}❌ Clé Fal AI manquante ou invalide${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Toutes les clés API sont configurées${NC}"

# Vérification 3: Dependencies Python
echo -e "${CYAN}📦 Vérification des dépendances Python...${NC}"
cd "$SAAS_DIR"
if ! $PYTHON_CMD -c "import fastapi, uvicorn, aiohttp" 2>/dev/null; then
    echo -e "${YELLOW}⚠️ Installation des dépendances Python...${NC}"
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Vérification 4: Node.js pour le frontend
echo -e "${CYAN}🎨 Vérification du frontend...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️ Installation des dépendances Node.js...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Toutes les vérifications passées!${NC}"
echo ""

# Lancement du backend
echo -e "${GREEN}🔥 Lancement du backend SEEDANCE...${NC}"
cd "$SAAS_DIR"

if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="SEEDANCE Backend" -- bash -c "
        echo '🚀 Démarrage du backend SEEDANCE...';
        $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload;
        echo 'Backend arrêté. Appuyez sur Entrée pour fermer.';
        read
    "
elif command -v xterm >/dev/null 2>&1; then
    xterm -title "SEEDANCE Backend" -e "
        echo '🚀 Démarrage du backend SEEDANCE...';
        $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload;
        echo 'Backend arrêté. Appuyez sur Entrée pour fermer.';
        read
    " &
else
    # Fallback - lancer en arrière-plan
    echo -e "${YELLOW}Lancement en arrière-plan...${NC}"
    $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload > /tmp/seedance_backend.log 2>&1 &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend démarré (PID: $BACKEND_PID)${NC}"
fi

# Attendre que le backend soit prêt
echo -e "${CYAN}⏳ Attente du démarrage backend...${NC}"
sleep 5

# Test de connectivité
echo -e "${CYAN}🔍 Test de connectivité backend...${NC}"
cd "$BASE_DIR"
if command -v curl >/dev/null 2>&1; then
    if curl -s "http://localhost:8004/diagnostic" >/dev/null; then
        echo -e "${GREEN}✅ Backend accessible${NC}"
    else
        echo -e "${RED}❌ Backend non accessible${NC}"
        echo -e "${YELLOW}   Vérifiez les logs dans /tmp/seedance_backend.log${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ curl non disponible, impossible de tester la connectivité${NC}"
fi

# Lancement du frontend
echo -e "${MAGENTA}🎨 Lancement du frontend...${NC}"
cd "$FRONTEND_DIR"

if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="SEEDANCE Frontend" -- bash -c "
        echo '🎨 Démarrage du frontend SEEDANCE...';
        npm run dev;
        echo 'Frontend arrêté. Appuyez sur Entrée pour fermer.';
        read
    "
elif command -v xterm >/dev/null 2>&1; then
    xterm -title "SEEDANCE Frontend" -e "
        echo '🎨 Démarrage du frontend SEEDANCE...';
        npm run dev;
        echo 'Frontend arrêté. Appuyez sur Entrée pour fermer.';
        read
    " &
else
    # Fallback - lancer en arrière-plan
    echo -e "${YELLOW}Lancement en arrière-plan...${NC}"
    npm run dev > /tmp/seedance_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo -e "${GREEN}Frontend démarré (PID: $FRONTEND_PID)${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Services SEEDANCE démarrés avec succès!${NC}"
echo ""
echo -e "${CYAN}🌐 Backend: http://localhost:8004${NC}"
echo -e "${CYAN}🎨 Frontend: http://localhost:5173${NC}"
echo ""

# Ouverture automatique du navigateur
echo -e "${YELLOW}⏳ Ouverture du navigateur dans 8 secondes...${NC}"
sleep 8

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5173" 2>/dev/null &
    echo -e "${GREEN}🌐 Navigateur ouvert sur l'interface SEEDANCE${NC}"
elif command -v open >/dev/null 2>&1; then
    open "http://localhost:5173" 2>/dev/null &
    echo -e "${GREEN}🌐 Navigateur ouvert sur l'interface SEEDANCE${NC}"
else
    echo -e "${YELLOW}⚠️ Impossible d'ouvrir le navigateur automatiquement${NC}"
    echo -e "${CYAN}Ouvrez manuellement: http://localhost:5173${NC}"
fi

echo ""
echo -e "${YELLOW}💡 Conseils d'utilisation:${NC}"
echo -e "${YELLOW}   • Laissez les terminaux backend/frontend ouverts${NC}"
echo -e "${YELLOW}   • En cas d'erreur, vérifiez les logs${NC}"
echo -e "${YELLOW}   • Utilisez le diagnostic dans l'interface web${NC}"
echo ""

# Si on a des PIDs en arrière-plan, attendre
if [[ -n "$BACKEND_PID" ]] || [[ -n "$FRONTEND_PID" ]]; then
    echo -e "${YELLOW}Services en cours d'exécution en arrière-plan...${NC}"
    echo -e "${YELLOW}Logs disponibles dans /tmp/seedance_*.log${NC}"
    echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter tous les services${NC}"
    
    # Fonction de nettoyage
    cleanup() {
        echo ""
        echo -e "${YELLOW}🛑 Arrêt des services SEEDANCE...${NC}"
        [[ -n "$BACKEND_PID" ]] && kill "$BACKEND_PID" 2>/dev/null
        [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null
        echo -e "${GREEN}✅ Services arrêtés${NC}"
        exit 0
    }
    
    trap cleanup INT TERM
    
    # Attendre indéfiniment
    while true; do
        sleep 1
    done
else
    echo -e "${GREEN}Services lancés dans des terminaux séparés${NC}"
    echo -e "${YELLOW}Fermez les fenêtres des terminaux pour arrêter les services${NC}"
    read -p "Appuyez sur Entrée pour fermer cette fenêtre..."
fi
