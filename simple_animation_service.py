#!/usr/bin/env python3
"""
Service d'animation CrewAI simplifié pour diagnostiquer et corriger les problèmes
"""

import os
import json
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('saas/.env')
load_dotenv('saas/.env.crewai')

class SimpleAnimationService:
    """Service d'animation simplifié pour diagnostic"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.cache_dir = Path("saas/cache/crewai_animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration CrewAI avec chemin court
        import tempfile
        short_temp_dir = tempfile.mkdtemp(prefix="crew_", dir="C:/temp" if os.path.exists("C:/temp") else None)
        os.environ["CREWAI_STORAGE_DIR"] = short_temp_dir
        
        # LLM Configuration
        self.llm = None
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                openai_api_key=self.openai_api_key,
                model="gpt-4o-mini",
                temperature=0.7
            )
            print("✅ LLM configuré: GPT-4o-mini")
        except Exception as e:
            print(f"❌ Erreur LLM: {e}")
    
    def create_simple_agent(self):
        """Créer un agent simple pour test"""
        try:
            from crewai import Agent
            
            agent = Agent(
                role="Animation Creator",
                goal="Créer une animation simple et rapide",
                backstory="Expert en création d'animations courtes et captivantes",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            )
            return agent
            
        except Exception as e:
            print(f"❌ Erreur création agent: {e}")
            return None
    
    def create_simple_task(self, story: str, agent):
        """Créer une tâche simple"""
        try:
            from crewai import Task
            
            task = Task(
                description=f"""
                Crée une animation simple basée sur cette histoire: {story}
                
                Retourne un JSON avec cette structure exacte:
                {{
                    "scenes": [
                        {{
                            "scene_number": 1,
                            "description": "Description de la scène",
                            "duration": 5,
                            "prompt": "Prompt pour génération vidéo"
                        }}
                    ],
                    "total_scenes": 1,
                    "style": "cartoon coloré"
                }}
                
                IMPORTANT: Retourne UNIQUEMENT le JSON, rien d'autre.
                """,
                agent=agent,
                expected_output="JSON valide uniquement"
            )
            return task
            
        except Exception as e:
            print(f"❌ Erreur création tâche: {e}")
            return None
    
    async def generate_simple_animation(self, story: str) -> Dict[str, Any]:
        """Génération d'animation simplifiée"""
        print(f"🎬 === GÉNÉRATION ANIMATION SIMPLE ===")
        print(f"📝 Histoire: {story}")
        
        start_time = time.time()
        
        try:
            # 1. Créer l'agent
            print("1️⃣ Création de l'agent...")
            agent = self.create_simple_agent()
            if not agent:
                return {"status": "error", "error": "Impossible de créer l'agent"}
            
            # 2. Créer la tâche
            print("2️⃣ Création de la tâche...")
            task = self.create_simple_task(story, agent)
            if not task:
                return {"status": "error", "error": "Impossible de créer la tâche"}
            
            # 3. Créer l'équipe
            print("3️⃣ Création de l'équipe...")
            from crewai import Crew, Process
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
                memory=False
            )
            
            # 4. Exécuter
            print("4️⃣ Exécution...")
            result = crew.kickoff()
            
            # 5. Parser le résultat
            print("5️⃣ Analyse du résultat...")
            print(f"   Type de résultat: {type(result)}")
            
            # Extraire le texte du résultat
            result_text = ""
            if hasattr(result, 'tasks_output') and result.tasks_output:
                result_text = result.tasks_output[0].raw
                print(f"   Résultat brut: {result_text[:200]}...")
            else:
                result_text = str(result)
                print(f"   Résultat string: {result_text[:200]}...")
            
            # Parser JSON
            animation_data = self.parse_json_safely(result_text)
            
            if not animation_data or not animation_data.get("scenes"):
                print("⚠️ Pas de données d'animation valides - création manuelle")
                animation_data = {
                    "scenes": [
                        {
                            "scene_number": 1,
                            "description": f"Animation basée sur: {story[:50]}...",
                            "duration": 5,
                            "prompt": f"Cartoon coloré animé: {story[:100]}"
                        }
                    ],
                    "total_scenes": 1,
                    "style": "cartoon coloré"
                }
            
            # 6. Générer les vidéos (mock pour test)
            print("6️⃣ Génération des vidéos...")
            scenes_processed = []
            
            for scene_data in animation_data.get("scenes", []):
                scene_num = scene_data.get("scene_number", 1)
                prompt = scene_data.get("prompt", "Animation simple")
                duration = scene_data.get("duration", 5)
                
                print(f"   🎬 Scène {scene_num}: {prompt[:50]}...")
                
                # Générer vidéo mock
                video_result = await self.generate_mock_video(prompt, duration)
                
                scene_processed = {
                    "scene_number": scene_num,
                    "description": scene_data.get("description", ""),
                    "duration": duration,
                    "prompt": prompt,
                    "video_url": video_result.get("video_url"),
                    "local_path": video_result.get("local_path"),
                    "status": "completed"
                }
                scenes_processed.append(scene_processed)
            
            # 7. Créer la vidéo finale
            print("7️⃣ Assemblage final...")
            final_video_path = await self.create_final_video(scenes_processed)
            
            # 8. Retourner le résultat
            total_time = time.time() - start_time
            
            result_final = {
                "status": "success",
                "video_path": final_video_path,
                "video_url": f"/static/cache/crewai_animations/{Path(final_video_path).name}",
                "scenes_count": len(scenes_processed),
                "total_duration": sum(s.get("duration", 5) for s in scenes_processed),
                "generation_time": round(total_time, 2),
                "pipeline_type": "simple_crewai",
                "scenes_details": scenes_processed,
                "animation_data": animation_data,
                "raw_agent_output": result_text[:500],
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Animation générée avec succès!")
            print(f"   ⏱️ Temps: {total_time:.1f}s")
            print(f"   🎬 Scènes: {len(scenes_processed)}")
            print(f"   📁 Vidéo: {final_video_path}")
            
            return result_final
            
        except Exception as e:
            print(f"❌ Erreur génération: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "error": str(e),
                "generation_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Parser JSON de façon sécurisée"""
        try:
            # Nettoyer le texte
            text = text.strip()
            
            # Chercher JSON dans des blocs de code
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                if end != -1:
                    text = text[start:end].strip()
            
            # Chercher JSON entre accolades
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end > start:
                    text = text[start:end]
            
            # Parser JSON
            data = json.loads(text)
            print(f"✅ JSON parsé avec succès: {list(data.keys())}")
            return data
            
        except Exception as e:
            print(f"⚠️ Erreur parsing JSON: {e}")
            print(f"   Texte à parser: {text[:200]}...")
            return {}
    
    async def generate_mock_video(self, prompt: str, duration: int) -> Dict[str, Any]:
        """Générer une vidéo factice"""
        print(f"🎭 Génération vidéo mock: {prompt[:30]}...")
        
        # Simuler un délai
        await asyncio.sleep(1)
        
        # Créer un fichier mock
        mock_filename = f"mock_{int(time.time())}.mp4"
        mock_path = self.cache_dir / mock_filename
        
        # Créer un fichier minimal
        try:
            with open(mock_path, 'wb') as f:
                # En-tête MP4 minimal
                f.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41\x00\x00\x00\x08free')
                f.write(b'\x00' * 1024 * 50)  # 50KB
            
            print(f"✅ Vidéo mock créée: {mock_path}")
            
        except Exception as e:
            print(f"⚠️ Erreur création mock: {e}")
            mock_path.touch()
        
        return {
            "status": "success",
            "video_url": f"https://example.com/mock/{mock_filename}",
            "local_path": str(mock_path),
            "duration": duration,
            "prompt": prompt,
            "is_mock": True
        }
    
    async def create_final_video(self, scenes: List[Dict]) -> str:
        """Créer la vidéo finale"""
        timestamp = int(time.time())
        final_filename = f"animation_{timestamp}.mp4"
        final_path = self.cache_dir / final_filename
        
        # Pour l'instant, copier la première scène comme vidéo finale
        try:
            if scenes and scenes[0].get("local_path"):
                import shutil
                shutil.copy2(scenes[0]["local_path"], final_path)
                print(f"✅ Vidéo finale créée: {final_path}")
            else:
                # Créer un fichier vide
                final_path.touch()
                print(f"⚠️ Vidéo finale vide créée: {final_path}")
                
        except Exception as e:
            print(f"❌ Erreur création vidéo finale: {e}")
            final_path.touch()
        
        return str(final_path)

# Instance globale
simple_animation_service = SimpleAnimationService()

async def test_simple_service():
    """Tester le service simplifié"""
    print("🧪 === TEST SERVICE SIMPLIFIÉ ===\n")
    
    story = "Un petit chat qui découvre un jardin magique avec des fleurs qui chantent"
    
    result = await simple_animation_service.generate_simple_animation(story)
    
    print(f"\n📊 === RÉSULTAT FINAL ===")
    print(f"Status: {result.get('status')}")
    print(f"Scènes: {result.get('scenes_count')}")
    print(f"Durée: {result.get('generation_time')}s")
    print(f"Vidéo: {result.get('video_path')}")
    
    if result.get('status') == 'success':
        print("🎉 SERVICE SIMPLIFIÉ FONCTIONNE!")
        return True
    else:
        print(f"❌ Erreur: {result.get('error')}")
        return False

if __name__ == "__main__":
    import sys
    import os
    
    # Changer le répertoire de travail
    os.chdir(Path(__file__).parent)
    sys.path.insert(0, str(Path(__file__).parent))
    
    asyncio.run(test_simple_service())
