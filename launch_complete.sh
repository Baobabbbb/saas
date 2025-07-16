#!/bin/bash
# SEEDANCE - Lanceur Complet
# Lance automatiquement le backend et le frontend

set -e

# Configuration par défaut
BACKEND_PORT=${BACKEND_PORT:-8004}
FRONTEND_PORT=${FRONTEND_PORT:-5173}
SKIP_DEPS=${SKIP_DEPS:-false}
NO_BROWSER=${NO_BROWSER:-false}

# Variables globales
BACKEND_PID=""
FRONTEND_PID=""
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAAS_DIR="$BASE_DIR/saas"
FRONTEND_DIR="$BASE_DIR/frontend"

# Couleurs pour la sortie
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ️ $1${NC}"; }
print_step() { echo -e "${MAGENTA}🔧 $1${NC}"; }

# Fonction de nettoyage
cleanup() {
    print_step "Arrêt des services SEEDANCE..."
    
    if [[ -n "$BACKEND_PID" ]]; then
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            print_info "Arrêt du backend (PID: $BACKEND_PID)..."
            kill -TERM "$BACKEND_PID" 2>/dev/null || true
            sleep 2
            if kill -0 "$BACKEND_PID" 2>/dev/null; then
                kill -KILL "$BACKEND_PID" 2>/dev/null || true
            fi
        fi
    fi
    
    if [[ -n "$FRONTEND_PID" ]]; then
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            print_info "Arrêt du frontend (PID: $FRONTEND_PID)..."
            kill -TERM "$FRONTEND_PID" 2>/dev/null || true
            sleep 2
            if kill -0 "$FRONTEND_PID" 2>/dev/null; then
                kill -KILL "$FRONTEND_PID" 2>/dev/null || true
            fi
        fi
    fi
    
    # Tuer les processus sur les ports spécifiques
    if command -v lsof >/dev/null 2>&1; then
        local backend_proc=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)
        if [[ -n "$backend_proc" ]]; then
            print_info "Arrêt du processus sur le port $BACKEND_PORT..."
            kill -TERM "$backend_proc" 2>/dev/null || true
        fi
        
        local frontend_proc=$(lsof -ti:$FRONTEND_PORT 2>/dev/null || true)
        if [[ -n "$frontend_proc" ]]; then
            print_info "Arrêt du processus sur le port $FRONTEND_PORT..."
            kill -TERM "$frontend_proc" 2>/dev/null || true
        fi
    fi
    
    print_success "Nettoyage terminé"
}

# Gestionnaire de signaux
trap cleanup EXIT INT TERM

# Fonction d'aide
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Lance automatiquement le backend et le frontend SEEDANCE.

OPTIONS:
    --skip-deps         Ignore l'installation des dépendances
    --no-browser        N'ouvre pas le navigateur automatiquement
    --backend-port PORT Port pour le backend (défaut: 8004)
    --frontend-port PORT Port pour le frontend (défaut: 5173)
    -h, --help          Affiche cette aide

EXEMPLES:
    $0                          # Lancement standard
    $0 --skip-deps              # Sans installation des dépendances
    $0 --backend-port 8080      # Backend sur le port 8080
    $0 --no-browser             # Sans ouverture du navigateur

EOF
}

# Analyse des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --no-browser)
            NO_BROWSER=true
            shift
            ;;
        --backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Vérification des prérequis
check_prerequisites() {
    print_step "Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
        print_error "Python non trouvé. Veuillez installer Python."
        return 1
    fi
    
    local python_cmd="python3"
    if ! command -v python3 >/dev/null 2>&1; then
        python_cmd="python"
    fi
    
    local python_version=$($python_cmd --version 2>&1)
    print_success "Python trouvé: $python_version"
    
    # Vérifier Node.js
    if ! command -v node >/dev/null 2>&1; then
        print_error "Node.js non trouvé. Veuillez installer Node.js."
        return 1
    fi
    
    local node_version=$(node --version 2>&1)
    print_success "Node.js trouvé: $node_version"
    
    # Vérifier npm
    if ! command -v npm >/dev/null 2>&1; then
        print_error "npm non trouvé. Veuillez installer npm."
        return 1
    fi
    
    # Vérifier les répertoires
    if [[ ! -d "$SAAS_DIR" ]]; then
        print_error "Répertoire backend non trouvé: $SAAS_DIR"
        return 1
    fi
    
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        print_error "Répertoire frontend non trouvé: $FRONTEND_DIR"
        return 1
    fi
    
    # Vérifier les fichiers essentiels
    if [[ ! -f "$SAAS_DIR/main.py" ]]; then
        print_error "Fichier main.py non trouvé dans $SAAS_DIR"
        return 1
    fi
    
    if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
        print_error "Fichier package.json non trouvé dans $FRONTEND_DIR"
        return 1
    fi
    
    print_success "Tous les prérequis sont satisfaits"
    return 0
}

# Installation des dépendances
install_dependencies() {
    if [[ "$SKIP_DEPS" == "true" ]]; then
        print_info "Installation des dépendances ignorée (--skip-deps)"
        return 0
    fi
    
    print_step "Installation des dépendances..."
    
    # Déterminer la commande Python
    local python_cmd="python3"
    if ! command -v python3 >/dev/null 2>&1; then
        python_cmd="python"
    fi
    
    # Backend Python
    if [[ -f "$SAAS_DIR/requirements.txt" ]]; then
        print_info "Installation des dépendances Python..."
        (cd "$SAAS_DIR" && $python_cmd -m pip install -r requirements.txt) || {
            print_warning "Erreur lors de l'installation des dépendances Python"
        }
        print_success "Dépendances Python installées"
    fi
    
    # Frontend Node.js
    print_info "Installation des dépendances Node.js..."
    (cd "$FRONTEND_DIR" && npm install) || {
        print_warning "Erreur lors de l'installation des dépendances Node.js"
    }
    print_success "Dépendances Node.js installées"
}

# Démarrage du backend
start_backend() {
    print_step "Démarrage du backend..."
    
    local python_cmd="python3"
    if ! command -v python3 >/dev/null 2>&1; then
        python_cmd="python"
    fi
    
    cd "$SAAS_DIR"
    
    # Démarrer le backend en arrière-plan
    $python_cmd -m uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload > /tmp/seedance_backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Attendre un peu pour voir si le processus démarre
    sleep 3
    
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        print_success "Backend démarré (PID: $BACKEND_PID)"
        print_info "🌐 API disponible sur: http://localhost:$BACKEND_PORT"
        print_info "📚 Documentation: http://localhost:$BACKEND_PORT/docs"
        return 0
    else
        print_error "Erreur lors du démarrage du backend"
        if [[ -f /tmp/seedance_backend.log ]]; then
            print_error "Log d'erreur:"
            tail -n 10 /tmp/seedance_backend.log
        fi
        return 1
    fi
}

# Démarrage du frontend
start_frontend() {
    print_step "Démarrage du frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Démarrer le frontend en arrière-plan
    npm run dev > /tmp/seedance_frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Attendre un peu pour voir si le processus démarre
    sleep 5
    
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        print_success "Frontend démarré (PID: $FRONTEND_PID)"
        print_info "🎨 Interface disponible sur: http://localhost:$FRONTEND_PORT"
        return 0
    else
        print_error "Erreur lors du démarrage du frontend"
        if [[ -f /tmp/seedance_frontend.log ]]; then
            print_error "Log d'erreur:"
            tail -n 10 /tmp/seedance_frontend.log
        fi
        return 1
    fi
}

# Ouverture du navigateur
open_browser() {
    if [[ "$NO_BROWSER" == "true" ]]; then
        print_info "Ouverture du navigateur ignorée (--no-browser)"
        return 0
    fi
    
    print_step "Ouverture du navigateur..."
    sleep 5
    
    # Déterminer la commande pour ouvrir le navigateur
    local open_cmd=""
    if command -v xdg-open >/dev/null 2>&1; then
        open_cmd="xdg-open"
    elif command -v open >/dev/null 2>&1; then
        open_cmd="open"
    elif command -v start >/dev/null 2>&1; then
        open_cmd="start"
    fi
    
    if [[ -n "$open_cmd" ]]; then
        $open_cmd "http://localhost:$FRONTEND_PORT" 2>/dev/null &
        $open_cmd "http://localhost:$BACKEND_PORT/docs" 2>/dev/null &
        print_success "Navigateur ouvert"
    else
        print_warning "Impossible d'ouvrir le navigateur automatiquement"
        print_info "Ouvrez manuellement: http://localhost:$FRONTEND_PORT"
    fi
}

# Surveillance des services
wait_for_services() {
    print_step "Surveillance des services (Ctrl+C pour arrêter)..."
    
    while true; do
        if [[ -n "$BACKEND_PID" ]] && ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            print_error "Le backend s'est arrêté de manière inattendue"
            break
        fi
        
        if [[ -n "$FRONTEND_PID" ]] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
            print_error "Le frontend s'est arrêté de manière inattendue"
            break
        fi
        
        sleep 5
    done
}

# Script principal
main() {
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}   🎬 SEEDANCE - LANCEUR COMPLET BASH${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    
    print_info "📁 Répertoire de base: $BASE_DIR"
    print_info "📁 Backend: $SAAS_DIR"
    print_info "📁 Frontend: $FRONTEND_DIR"
    print_info "🌐 Ports: Backend=$BACKEND_PORT, Frontend=$FRONTEND_PORT"
    echo ""
    
    # Vérifications
    if ! check_prerequisites; then
        return 1
    fi
    
    # Installation des dépendances
    install_dependencies
    
    # Démarrage du backend
    if ! start_backend; then
        print_error "Impossible de démarrer le backend"
        return 1
    fi
    
    # Démarrage du frontend
    if ! start_frontend; then
        print_error "Impossible de démarrer le frontend"
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}   🎉 SEEDANCE LANCÉ AVEC SUCCÈS!${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    echo -e "${CYAN}🌐 Backend API: http://localhost:$BACKEND_PORT${NC}"
    echo -e "${CYAN}📚 Documentation: http://localhost:$BACKEND_PORT/docs${NC}"
    echo -e "${CYAN}🎨 Frontend: http://localhost:$FRONTEND_PORT${NC}"
    echo ""
    echo -e "${YELLOW}💡 Appuyez sur Ctrl+C pour arrêter tous les services${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    
    # Ouvrir le navigateur
    open_browser
    
    # Attendre
    wait_for_services
    
    return 0
}

# Exécution
if main; then
    exit 0
else
    exit 1
fi
