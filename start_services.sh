#!/bin/bash

# 🎵 Script de démarrage rapide - Comptines Musicales
# Ce script démarre automatiquement le backend et le frontend

echo "🚀 Démarrage des services - Comptines Musicales"
echo "================================================"

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

# Vérifier Python
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

# Vérifier npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé"
    exit 1
fi

echo "✅ Prérequis validés"

# Configuration
BACKEND_DIR="saas"
FRONTEND_DIR="frontend"
BACKEND_PORT=8000
FRONTEND_PORT=5174

# Fonction pour tuer les processus en arrière-plan
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "✅ Services arrêtés"
    exit 0
}

# Trap pour nettoyer en cas d'interruption
trap cleanup SIGINT SIGTERM

# Démarrage du backend
echo ""
echo "🔧 Démarrage du backend..."
cd "$BACKEND_DIR"

# Vérifier les dépendances Python
if [ ! -f "requirements_new.txt" ]; then
    echo "❌ Fichier requirements_new.txt non trouvé"
    exit 1
fi

# Installer/mettre à jour les dépendances (optionnel)
# echo "📦 Installation des dépendances Python..."
# pip install -r requirements_new.txt

# Démarrer le backend en arrière-plan
echo "🚀 Lancement du serveur backend sur le port $BACKEND_PORT..."
python main_new.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du démarrage du backend..."
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null 2>&1; then
        echo "✅ Backend prêt!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout: le backend n'a pas démarré"
        cleanup
        exit 1
    fi
    sleep 1
done

# Démarrage du frontend
echo ""
echo "🎨 Démarrage du frontend..."
cd "../$FRONTEND_DIR"

# Vérifier package.json
if [ ! -f "package.json" ]; then
    echo "❌ Fichier package.json non trouvé"
    cleanup
    exit 1
fi

# Installer/mettre à jour les dépendances (optionnel)
# echo "📦 Installation des dépendances Node.js..."
# npm install

# Démarrer le frontend en arrière-plan
echo "🚀 Lancement du serveur frontend..."
npm run dev &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
echo "⏳ Attente du démarrage du frontend..."
for i in {1..60}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "✅ Frontend prêt!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "❌ Timeout: le frontend n'a pas démarré"
        cleanup
        exit 1
    fi
    sleep 1
done

# Services prêts
echo ""
echo "🎉 SERVICES DÉMARRÉS AVEC SUCCÈS!"
echo "=================================="
echo "🔧 Backend:    http://localhost:$BACKEND_PORT"
echo "📚 API Docs:   http://localhost:$BACKEND_PORT/docs"
echo "🎨 Frontend:   http://localhost:$FRONTEND_PORT"
echo ""
echo "🎵 La fonctionnalité Comptines Musicales est prête!"
echo ""
echo "💡 Pour tester:"
echo "   1. Ouvrez http://localhost:$FRONTEND_PORT"
echo "   2. Sélectionnez 'Comptine musicale'"
echo "   3. Choisissez un style et faites votre demande"
echo ""
echo "🛑 Appuyez sur Ctrl+C pour arrêter les services"

# Attendre l'interruption
wait
