"""
Test simple du service SEEDANCE
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'saas'))

from services.seedance_service import SeedanceService

async def test_seedance_simple():
    """Test simple du service SEEDANCE"""
    service = SeedanceService()
    
    print("🚀 Test simple du service SEEDANCE")
    print("=" * 50)
    
    # Test avec histoire courte
    result = await service.generate_seedance_animation(
        story="Un petit panda apprend à compter",
        theme="education",
        age_target="3-5",
        duration=30
    )
    
    print(f"✅ Résultat: {result}")
    
    if result.get("status") == "success":
        print("🎉 Service fonctionne !")
    else:
        print("❌ Service ne fonctionne pas")
        print(f"Erreur: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_seedance_simple())
