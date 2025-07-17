#!/bin/bash
# LANCEMENT COMPLET FRIDAY SEEDANCE - VERSION FONCTIONNELLE
# Ce script lance le backend sur 8004 et le frontend sur 5173

echo "🚀 FRIDAY SEEDANCE - LANCEMENT COMPLET"
echo "======================================"

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   ✅ Backend arrêté (PID: $BACKEND_PID)"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   ✅ Frontend arrêté (PID: $FRONTEND_PID)"
    fi
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Variables
BASE_DIR="$(pwd)"
BACKEND_DIR="$BASE_DIR/saas"
FRONTEND_DIR="$BASE_DIR/frontend"

echo "📁 Répertoires:"
echo "   Base: $BASE_DIR"
echo "   Backend: $BACKEND_DIR"
echo "   Frontend: $FRONTEND_DIR"

# 1. VÉRIFICATIONS RAPIDES
echo ""
echo "🔍 Vérifications rapides..."

# Vérifier Python
if ! command -v python >/dev/null 2>&1; then
    echo "❌ Python non trouvé. Installez Python d'abord."
    exit 1
fi
echo "   ✅ Python: $(python --version 2>&1 | head -1)"

# Vérifier Node.js et npm
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js non trouvé. Installez Node.js d'abord."
    exit 1
fi
echo "   ✅ Node.js: $(node --version)"

if ! command -v npm >/dev/null 2>&1; then
    echo "❌ npm non trouvé. Installez npm d'abord."
    exit 1
fi
echo "   ✅ npm: $(npm --version)"

# Vérifier les répertoires
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Répertoire backend '$BACKEND_DIR' non trouvé"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Répertoire frontend '$FRONTEND_DIR' non trouvé"
    exit 1
fi

if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "❌ Fichier .env non trouvé dans $BACKEND_DIR"
    echo "   Créez le fichier $BACKEND_DIR/.env avec vos clés API"
    exit 1
fi

if [ ! -f "$BACKEND_DIR/main.py" ]; then
    echo "❌ Fichier main.py non trouvé dans $BACKEND_DIR"
    exit 1
fi

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo "❌ Fichier package.json non trouvé dans $FRONTEND_DIR"
    exit 1
fi

echo "   ✅ Structure des fichiers OK"

# 2. INSTALLATION DES DÉPENDANCES
echo ""
echo "📦 Installation des dépendances..."

# Backend Python
echo "   🐍 Dépendances Python..."
cd "$BACKEND_DIR"
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt --quiet --disable-pip-version-check
    if [ $? -eq 0 ]; then
        echo "   ✅ Dépendances Python installées"
    else
        echo "   ⚠️ Erreur installation Python (continuons quand même)"
    fi
else
    echo "   ⚠️ requirements.txt non trouvé"
fi

# Frontend Node.js
cd "$FRONTEND_DIR"
echo "   📦 Dépendances Node.js..."
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    npm install --silent
    if [ $? -eq 0 ]; then
        echo "   ✅ Dépendances Node.js installées"
    else
        echo "   ❌ Erreur installation Node.js"
        exit 1
    fi
else
    echo "   ✅ Dépendances Node.js déjà installées"
fi

cd "$BASE_DIR"

# 3. NETTOYAGE DES PROCESSUS EXISTANTS
echo ""
echo "🧹 Nettoyage des processus existants..."

# Tuer les processus sur les ports 8004 et 5173
if command -v lsof >/dev/null 2>&1; then
    # Sur macOS/Linux avec lsof
    lsof -ti:8004 | xargs -r kill -9 2>/dev/null
    lsof -ti:5173 | xargs -r kill -9 2>/dev/null
elif command -v netstat >/dev/null 2>&1; then
    # Sur certains systèmes Linux
    netstat -tlpn | grep :8004 | awk '{print $7}' | cut -d'/' -f1 | xargs -r kill -9 2>/dev/null
    netstat -tlpn | grep :5173 | awk '{print $7}' | cut -d'/' -f1 | xargs -r kill -9 2>/dev/null
fi

echo "   ✅ Ports nettoyés"

# 4. DÉMARRAGE DU BACKEND
echo ""
echo "🖥️ Démarrage du backend..."
cd "$BACKEND_DIR"

# Lancer le backend avec uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload &
BACKEND_PID=$!

echo "   📍 Backend PID: $BACKEND_PID"
echo "   🌐 URL Backend: http://localhost:8004"

# Attendre que le backend soit prêt
echo "   ⏳ Attente du backend..."
for i in {1..20}; do
    if curl -s http://localhost:8004/docs >/dev/null 2>&1; then
        echo "   ✅ Backend opérationnel!"
        break
    fi
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   ❌ Le backend s'est arrêté de manière inattendue"
        exit 1
    fi
    sleep 2
    if [ $i -eq 20 ]; then
        echo "   ⚠️ Backend lent à démarrer mais on continue..."
    fi
done

cd "$BASE_DIR"

# 5. DÉMARRAGE DU FRONTEND
echo ""
echo "🌐 Démarrage du frontend..."
cd "$FRONTEND_DIR"

# Lancer le frontend avec Vite
npm run dev &
FRONTEND_PID=$!

echo "   📍 Frontend PID: $FRONTEND_PID"
echo "   🌐 URL Frontend: http://localhost:5173"

# Attendre que le frontend soit prêt
echo "   ⏳ Attente du frontend..."
for i in {1..15}; do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo "   ✅ Frontend opérationnel!"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "   ❌ Le frontend s'est arrêté de manière inattendue"
        cleanup
        exit 1
    fi
    sleep 2
    if [ $i -eq 15 ]; then
        echo "   ⚠️ Frontend lent à démarrer mais on continue..."
    fi
done

cd "$BASE_DIR"

# 6. TEST DE CONNECTIVITÉ
echo ""
echo "🔗 Test de connectivité..."

# Test backend
if curl -s http://localhost:8004/docs >/dev/null 2>&1; then
    echo "   ✅ Backend accessible sur http://localhost:8004"
else
    echo "   ⚠️ Backend non accessible (démarrage en cours...)"
fi

# Test frontend
if curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo "   ✅ Frontend accessible sur http://localhost:5173"
else
    echo "   ⚠️ Frontend non accessible (démarrage en cours...)"
fi

# 7. SUCCÈS - AFFICHAGE DES INFOS
echo ""
echo "🎉 LANCEMENT RÉUSSI!"
echo "=================="
echo ""
echo "🌐 URLS D'ACCÈS:"
echo "   Frontend:     http://localhost:5173"
echo "   Backend API:  http://localhost:8004"
echo "   API Docs:     http://localhost:8004/docs"
echo "   Diagnostic:   http://localhost:8004/diagnostic"
echo ""
echo "📊 SERVICES ACTIFS:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "💡 CONSEILS:"
echo "   • L'interface est maintenant accessible"
echo "   • Laissez ce terminal ouvert"
echo "   • Appuyez sur Ctrl+C pour tout arrêter"
echo "   • En cas de problème, relancez ce script"
echo ""

# Ouvrir le navigateur automatiquement après 5 secondes
echo "🌐 Ouverture automatique du navigateur dans 5 secondes..."
sleep 5

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5173" >/dev/null 2>&1 &
    echo "   ✅ Navigateur ouvert"
elif command -v open >/dev/null 2>&1; then
    open "http://localhost:5173" >/dev/null 2>&1 &
    echo "   ✅ Navigateur ouvert"
else
    echo "   ⚠️ Ouvrez manuellement: http://localhost:5173"
fi

echo ""
echo "🔄 Services en cours d'exécution..."
echo "   Appuyez sur Ctrl+C pour arrêter"

# Monitoring des processus
monitor_processes() {
    while true; do
        sleep 5
        
        # Vérifier que les processus sont toujours actifs
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo ""
            echo "❌ Backend arrêté de manière inattendue"
            cleanup
            exit 1
        fi
        
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo ""
            echo "❌ Frontend arrêté de manière inattendue"
            cleanup
            exit 1
        fi
    done
}

# Lancer le monitoring en arrière-plan
monitor_processes &
MONITOR_PID=$!

# Attendre indéfiniment (jusqu'à Ctrl+C)
while true; do
    read -t 1 -n 1 && break
    sleep 1
done 2>/dev/null

cleanup
