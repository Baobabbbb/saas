"""
Test simplifié du pipeline CrewAI
Focus sur la partie agents sans génération vidéo
"""

import asyncio
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.simple_animation_service import simple_animation_service

async def test_basic_crewai():
    """Test de base du pipeline CrewAI"""
    
    print("🧪 === TEST PIPELINE CRÉAWAI SIMPLIFIÉ ===")
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    # Histoire de test simple
    test_story = """
    Un petit chat orange découvre un jardin magique rempli de fleurs colorées.
    Il joue avec des papillons dorés sous le soleil.
    Puis il rentre chez lui, content de sa belle aventure.
    """
    
    # Préférences de style
    style_preferences = {
        "style": "cartoon mignon et coloré",
        "mood": "joyeux et doux",
        "target_age": "3-6 ans"
    }
    
    print(f"📖 Histoire de test: {test_story.strip()}")
    print(f"🎨 Style: {style_preferences}")
    print()
    
    try:
        # Test des agents
        print("1️⃣ Test création agents...")
        agents = simple_animation_service.create_agents()
        print(f"✅ {len(agents)} agents créés:")
        for name, agent in agents.items():
            print(f"  - {name}: {agent.role}")
        
        # Test des tâches
        print("\n2️⃣ Test création tâches...")
        tasks = simple_animation_service.create_tasks(test_story.strip(), style_preferences, agents)
        print(f"✅ {len(tasks)} tâches créées")
        
        # Test exécution complète
        print("\n3️⃣ Test exécution CrewAI...")
        result = await simple_animation_service.test_crew_execution(
            story_text=test_story.strip(),
            style_preferences=style_preferences
        )
        
        print(f"\n🎯 === RÉSULTATS FINAUX ===")
        
        if result.get('status') == 'success':
            print("✅ Test réussi !")
            print(f"⏱️  Temps total: {result.get('execution_time', 0):.1f}s")
            print(f"👥 Agents: {result.get('agents_count', 0)}")
            print(f"📋 Tâches: {result.get('tasks_count', 0)}")
            
            if result.get('results'):
                print("\n📊 Résultats par agent:")
                for agent_name, agent_result in result.get('results', {}).items():
                    print(f"  🤖 {agent_name}:")
                    print(f"     {agent_result.get('output', 'Pas de sortie')}")
        else:
            print("❌ Test échoué")
            print(f"Erreur: {result.get('error', 'Erreur inconnue')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

async def main():
    """Test principal"""
    
    print("🚀 DÉBUT TEST CRÉAWAI SIMPLIFIÉ")
    print("=" * 50)
    
    result = await test_basic_crewai()
    
    print(f"\n⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
