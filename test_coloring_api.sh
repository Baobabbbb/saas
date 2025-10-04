#!/bin/bash

echo "🧪 Test de l'API de génération de coloriages GPT-4o-mini"
echo "========================================================="
echo ""

echo "📡 Test 1: Health check"
curl -s https://herbbie.com/health | python -m json.tool
echo ""
echo ""

echo "📡 Test 2: Diagnostic des clés API"
curl -s https://herbbie.com/diagnostic | python -m json.tool
echo ""
echo ""

echo "🎨 Test 3: Génération de coloriage par thème (dinosaures)"
echo "⏳ Cela peut prendre 15-25 secondes..."
curl -X POST https://herbbie.com/generate_coloring/ \
  -H "Content-Type: application/json" \
  -d '{"theme": "dinosaures"}' \
  | python -m json.tool

echo ""
echo "✅ Tests terminés !"
