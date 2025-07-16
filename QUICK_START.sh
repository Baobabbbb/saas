#!/bin/bash
# SEEDANCE - Lancement Express Bash
# Script de démarrage rapide sans vérifications poussées

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   🚀 SEEDANCE - LANCEMENT EXPRESS${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Démarrage rapide sans vérifications poussées
echo -e "${CYAN}🎬 Démarrage des services SEEDANCE...${NC}"
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

# Backend
echo -e "${GREEN}🔥 Lancement du backend...${NC}"
if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="SEEDANCE Backend" -- bash -c "cd '$SAAS_DIR' && $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload; exec bash"
elif command -v xterm >/dev/null 2>&1; then
    xterm -title "SEEDANCE Backend" -e "cd '$SAAS_DIR' && $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload; exec bash" &
else
    # Fallback - lancer en arrière-plan
    cd "$SAAS_DIR"
    $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload > /tmp/seedance_backend.log 2>&1 &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend démarré en arrière-plan (PID: $BACKEND_PID)${NC}"
    cd "$BASE_DIR"
fi

# Attendre un peu
sleep 3

# Frontend
echo -e "${MAGENTA}🎨 Lancement du frontend...${NC}"
if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="SEEDANCE Frontend" -- bash -c "cd '$FRONTEND_DIR' && npm run dev; exec bash"
elif command -v xterm >/dev/null 2>&1; then
    xterm -title "SEEDANCE Frontend" -e "cd '$FRONTEND_DIR' && npm run dev; exec bash" &
else
    # Fallback - lancer en arrière-plan
    cd "$FRONTEND_DIR"
    npm run dev > /tmp/seedance_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo -e "${GREEN}Frontend démarré en arrière-plan (PID: $FRONTEND_PID)${NC}"
    cd "$BASE_DIR"
fi

echo ""
echo -e "${GREEN}✅ Services lancés!${NC}"
echo ""
echo -e "${CYAN}🌐 Backend: http://localhost:8004${NC}"
echo -e "${CYAN}🎨 Frontend: http://localhost:5173${NC}"
echo ""

# Ouvrir le navigateur après 10 secondes
echo -e "${YELLOW}⏳ Ouverture du navigateur dans 10 secondes...${NC}"
sleep 10

# Déterminer la commande pour ouvrir le navigateur
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5173" 2>/dev/null &
    echo -e "${GREEN}🌐 Navigateur ouvert sur l'interface principale${NC}"
elif command -v open >/dev/null 2>&1; then
    open "http://localhost:5173" 2>/dev/null &
    echo -e "${GREEN}🌐 Navigateur ouvert sur l'interface principale${NC}"
else
    echo -e "${YELLOW}⚠️ Impossible d'ouvrir le navigateur automatiquement${NC}"
    echo -e "${CYAN}Ouvrez manuellement: http://localhost:5173${NC}"
fi

echo ""
echo -e "${YELLOW}💡 Fermez cette fenêtre ou les fenêtres des services pour arrêter${NC}"
echo ""

# Si on a des PIDs en arrière-plan, attendre
if [[ -n "$BACKEND_PID" ]] || [[ -n "$FRONTEND_PID" ]]; then
    echo -e "${YELLOW}Services en cours d'exécution en arrière-plan...${NC}"
    echo -e "${YELLOW}Logs disponibles dans /tmp/seedance_*.log${NC}"
    echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter${NC}"
    
    # Fonction de nettoyage
    cleanup() {
        echo ""
        echo -e "${YELLOW}🛑 Arrêt des services...${NC}"
        [[ -n "$BACKEND_PID" ]] && kill "$BACKEND_PID" 2>/dev/null
        [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null
        exit 0
    }
    
    trap cleanup INT TERM
    
    # Attendre indéfiniment
    while true; do
        sleep 1
    done
else
    read -p "Appuyez sur Entrée pour fermer cette fenêtre..."
fi
