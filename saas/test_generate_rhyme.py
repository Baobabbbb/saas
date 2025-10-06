#!/usr/bin/env python3
"""
Script de test pour diagnostiquer l'erreur /generate_rhyme/
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("=" * 60)
print("🔍 TEST DIAGNOSTIC /generate_rhyme/")
print("=" * 60)

# Test 1: Imports
print("\n1️⃣ Test des imports...")
try:
    from services.suno_service import suno_service
    print("✅ suno_service importé avec succès")
    print(f"   API Key: {'Configurée' if suno_service.api_key else 'NON configurée'}")
    print(f"   Base URL: {suno_service.base_url}")
except Exception as e:
    print(f"❌ Erreur import suno_service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from openai import AsyncOpenAI
    print("✅ AsyncOpenAI importé avec succès")
except Exception as e:
    print(f"❌ Erreur import AsyncOpenAI: {e}")
    sys.exit(1)

# Test 2: Variables d'environnement
print("\n2️⃣ Test des variables d'environnement...")
suno_key = os.getenv("SUNO_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
print(f"SUNO_API_KEY: {'✅ Configurée' if suno_key else '❌ NON configurée'}")
print(f"OPENAI_API_KEY: {'✅ Configurée' if openai_key else '❌ NON configurée'}")

# Test 3: Test logique de détection de personnalisation
print("\n3️⃣ Test de la logique de détection...")
import re

def test_personalization_detection(custom_request):
    needs_customization = False
    personalization_indicators = [
        r'\b[A-Z][a-zéèêàâûôîïü]+\b',
        'prénom', 'nom', 's\'appelle', "s'appelle", 'appelé', 'appelée',
        'mon', 'ma', 'mes', 'notre', 'nos',
        'ans', 'année', 'anniversaire', 'ville', 'maison'
    ]
    
    for indicator in personalization_indicators:
        if isinstance(indicator, str):
            if indicator.lower() in custom_request.lower():
                needs_customization = True
                break
        else:
            if re.search(indicator, custom_request):
                needs_customization = True
                break
    
    if len(custom_request) > 30:
        needs_customization = True
    
    return needs_customization

test_cases = [
    ("", False),
    ("Avec le prénom Axel", True),
    ("Une comptine simple", False),
    ("Mon petit frère qui s'appelle Lucas aime les animaux", True)
]

for test_input, expected in test_cases:
    result = test_personalization_detection(test_input)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{test_input[:50]}' → {result} (attendu: {expected})")

# Test 4: Test génération GPT
print("\n4️⃣ Test génération GPT-4o-mini...")
async def test_gpt():
    if not openai_key:
        print("⚠️ Skipping GPT test (no API key)")
        return
    
    try:
        client = AsyncOpenAI(api_key=openai_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Dis juste 'test ok'"}
            ],
            max_tokens=10
        )
        content = response.choices[0].message.content
        print(f"✅ GPT réponse: {content}")
    except Exception as e:
        print(f"❌ Erreur GPT: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_gpt())

# Test 5: Test Suno Service (sans vraie génération)
print("\n5️⃣ Test Suno Service...")
try:
    print(f"Service initialisé: {suno_service is not None}")
    print(f"API Key présente: {bool(suno_service.api_key)}")
    print(f"Base URL: {suno_service.base_url}")
    print("✅ Suno service opérationnel")
except Exception as e:
    print(f"❌ Erreur Suno service: {e}")

print("\n" + "=" * 60)
print("✅ TESTS TERMINÉS")
print("=" * 60)

