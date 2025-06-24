#!/usr/bin/env python3
"""
Script pour vérifier l'état des crédits Runway
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.runway_gen4_new import runway_gen4_service

async def check_runway_status():
    """Vérifier l'état de l'API Runway et des crédits"""
    
    print("🔍 Vérification de l'état Runway Gen-4...")
    print("=" * 50)
    
    try:
        # Vérifier les crédits
        status = await runway_gen4_service.check_credits_status()
        
        print("📊 État du service Runway:")
        print(f"   Statut: {status['status']}")
        print(f"   Crédits disponibles: {'✅ Oui' if status['credits_available'] else '❌ Non'}")
        
        if status['status'] == 'simulation':
            print(f"   Raison: {status.get('reason', 'N/A')}")
        elif status['status'] == 'no_credits':
            print(f"   Problème: {status.get('reason', 'Crédits insuffisants')}")
            if status.get('error_details'):
                print(f"   Détails: {status['error_details']}")
        elif status['status'] == 'api_error':
            print(f"   Erreur API: {status.get('error', 'Erreur inconnue')}")
        elif status['status'] == 'http_error':
            print(f"   Erreur HTTP: {status.get('error', 'Erreur inconnue')}")
        elif status['status'] == 'connection_error':
            print(f"   Erreur de connexion: {status.get('error', 'Erreur inconnue')}")
        elif status['status'] == 'active':
            print("   ✅ Service actif et prêt !")
            print(f"   Message: {status.get('message', 'API fonctionnelle')}")
            if status.get('test_task_id'):
                print(f"   🆔 ID de tâche test: {status['test_task_id']}")
        else:
            print(f"   ❓ Statut inconnu: {status['status']}")
                
        print()
        print("💡 Informations:")
        if not status['credits_available']:
            print("   - Pour utiliser la vraie API Runway, ajoutez des crédits à votre compte")
            print("   - Le mode simulation reste disponible pour les tests")
        else:
            print("   - La génération réelle via Runway est disponible!")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(check_runway_status())
