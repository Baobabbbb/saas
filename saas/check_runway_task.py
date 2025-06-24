#!/usr/bin/env python3
"""
Script pour vérifier le statut d'une tâche Runway spécifique
"""

import asyncio
import sys
import os
import httpx
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.runway_gen4_new import runway_gen4_service

async def check_task_status(task_id: str):
    """Vérifier le statut d'une tâche Runway spécifique"""
    
    print(f"🔍 Vérification de la tâche: {task_id}")
    print("=" * 50)
    
    try:
        api_key = os.getenv("RUNWAY_API_KEY")
        base_url = os.getenv("RUNWAY_BASE_URL", "https://api.dev.runwayml.com/v1")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{base_url}/tasks/{task_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                task_data = response.json()
                
                print("📊 Informations de la tâche:")
                print(f"   ID: {task_data.get('id', 'N/A')}")
                print(f"   Statut: {task_data.get('status', 'N/A')}")
                print(f"   Créée: {task_data.get('createdAt', 'N/A')}")
                print(f"   Progression: {task_data.get('progress', 0)}%")
                
                if task_data.get('status') in ['completed', 'SUCCEEDED']:
                    output = task_data.get('output', [])
                    if output:
                        print(f"   ✅ Résultat: {output[0]}")
                    else:
                        print("   ❌ Aucun résultat disponible")
                        
                elif task_data.get('status') in ['failed', 'FAILED']:
                    error = task_data.get('error', 'Erreur inconnue')
                    print(f"   ❌ Erreur: {error}")
                    
                elif task_data.get('status') in ['pending', 'running', 'PENDING', 'RUNNING']:
                    print("   ⏳ Tâche en cours d'exécution...")
                    
                return task_data
                
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                print(f"   Détails: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

async def main():
    """Fonction principale"""
    
    # ID de la tâche qui a eu un timeout
    task_id = "7ac061d0-cd43-4a4f-a05f-0d4c5ef129a3"
    
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
    
    result = await check_task_status(task_id)
    
    if result:
        print(f"\n💡 Recommandations:")
        if result.get('status') in ['completed', 'SUCCEEDED']:
            print("   - La tâche s'est finalement terminée avec succès!")
            print("   - Vous pouvez utiliser le résultat maintenant")
        elif result.get('status') in ['pending', 'running', 'PENDING', 'RUNNING']:
            print("   - La tâche est toujours en cours")
            print("   - Runway peut prendre jusqu'à 20-30 minutes pour les générations complexes")
            print("   - Relancez ce script dans quelques minutes")
        elif result.get('status') in ['failed', 'FAILED']:
            print("   - La tâche a échoué côté Runway")
            print("   - Essayez de régénérer l'animation")
        else:
            print("   - Statut inattendu, contactez le support Runway si le problème persiste")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(main())
    else:
        print("Usage: python check_runway_task.py <task_id>")
        print(f"Exemple: python check_runway_task.py 7ac061d0-cd43-4a4f-a05f-0d4c5ef129a3")
