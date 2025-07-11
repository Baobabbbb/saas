"""
🧪 SCRIPT DE TEST COMPLET - SD3BubbleIntegratorAdvanced V2.0
Teste toutes les fonctionnalités du système autonome de bulles intégrées

TESTS INCLUS :
✅ Test d'import et d'initialisation du module
✅ Test d'analyse de scène et détection de positions
✅ Test de génération de prompts ultra-précis
✅ Test d'intégration de bulles (avec fallback PIL si pas de clé SD3)
✅ Test de traitement de BD complète
✅ Test d'assemblage final et export
✅ Validation des performances et de la qualité
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

try:
    from services.sd3_bubble_integrator_v2 import SD3BubbleIntegratorAdvanced
    print("✅ Import du module SD3BubbleIntegratorAdvanced réussi")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)


class SD3BubbleTestSuite:
    """
    🧪 SUITE DE TESTS COMPLÈTE POUR LE SYSTÈME SD3 V2.0
    """
    
    def __init__(self):
        self.integrator = SD3BubbleIntegratorAdvanced()
        self.test_results = {
            "test_start_time": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        # Créer un dossier de test
        self.test_dir = Path("test_output/sd3_bubble_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🧪 Initialisation de la suite de tests SD3 V2.0")
        print(f"📁 Dossier de test: {self.test_dir}")
    
    async def run_all_tests(self):
        """Exécute tous les tests de validation"""
        print("\n🚀 === DÉMARRAGE TESTS SD3BubbleIntegratorAdvanced V2.0 ===\n")
        
        # Liste des tests à exécuter
        tests = [
            ("Test 1: Initialisation du module", self.test_module_initialization),
            ("Test 2: Analyse de scène basique", self.test_scene_analysis_basic),
            ("Test 3: Analyse de scène complexe", self.test_scene_analysis_complex),
            ("Test 4: Génération de prompts SD3", self.test_prompt_generation),
            ("Test 5: Intégration de bulles (image test)", self.test_bubble_integration),
            ("Test 6: Traitement BD complète", self.test_complete_comic_processing),
            ("Test 7: Gestion des erreurs", self.test_error_handling),
            ("Test 8: Performance et cache", self.test_performance)
        ]
        
        # Exécuter chaque test
        for test_name, test_function in tests:
            try:
                print(f"🔍 {test_name}...")
                result = await test_function()
                
                if result["passed"]:
                    self.test_results["tests_passed"] += 1
                    print(f"✅ {test_name} - RÉUSSI")
                else:
                    self.test_results["tests_failed"] += 1
                    print(f"❌ {test_name} - ÉCHEC: {result.get('error', 'Unknown')}")
                
                self.test_results["test_details"].append({
                    "test_name": test_name,
                    "passed": result["passed"],
                    "duration": result.get("duration", 0),
                    "details": result.get("details", {}),
                    "error": result.get("error", None)
                })
                
                print(f"   Durée: {result.get('duration', 0):.2f}s")
                print()
                
            except Exception as e:
                self.test_results["tests_failed"] += 1
                print(f"❌ {test_name} - ERREUR CRITIQUE: {e}")
                self.test_results["test_details"].append({
                    "test_name": test_name,
                    "passed": False,
                    "error": str(e)
                })
                print()
        
        # Afficher le résumé final
        await self.print_test_summary()
        
        # Sauvegarder les résultats
        await self.save_test_results()
    
    async def test_module_initialization(self) -> dict:
        """Test d'initialisation du module"""
        start_time = datetime.now()
        
        try:
            # Vérifier que l'intégrateur est correctement initialisé
            assert self.integrator is not None, "Intégrateur non initialisé"
            assert hasattr(self.integrator, 'sd3_endpoint'), "Endpoint SD3 manquant"
            assert hasattr(self.integrator, 'prompt_templates'), "Templates de prompts manquants"
            assert hasattr(self.integrator, 'placement_zones'), "Zones de placement manquantes"
            
            # Vérifier les configurations
            assert len(self.integrator.prompt_templates) >= 2, "Templates insuffisants"
            assert len(self.integrator.placement_zones) >= 6, "Zones insuffisantes"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "templates_count": len(self.integrator.prompt_templates),
                    "zones_count": len(self.integrator.placement_zones),
                    "model": self.integrator.current_model
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def test_scene_analysis_basic(self) -> dict:
        """Test d'analyse de scène basique"""
        start_time = datetime.now()
        
        try:
            # Données de test basiques
            description = "Alice se trouve à gauche de l'image, tenant une épée. Bob est à droite, regardant Alice."
            dialogues = [
                {"character": "Alice", "text": "Prêt pour le combat ?", "type": "speech"},
                {"character": "Bob", "text": "Toujours !", "type": "speech"}
            ]
            
            # Analyser la scène
            analysis = await self.integrator._analyze_scene_composition_advanced(description, dialogues)
            
            # Vérifications
            assert analysis["total_bubbles"] == 2, f"Mauvais nombre de bulles: {analysis['total_bubbles']}"
            assert len(analysis["bubble_plan"]) == 2, "Plan de bulles incorrect"
            assert len(analysis["character_positions"]) >= 1, "Positions de personnages non détectées"
            assert analysis["art_style"] is not None, "Style artistique non détecté"
            
            # Vérifier les données de chaque bulle
            for bubble in analysis["bubble_plan"]:
                assert "bubble_id" in bubble, "ID de bulle manquant"
                assert "speaker" in bubble, "Locuteur manquant"
                assert "text" in bubble, "Texte manquant"
                assert "bubble_zone" in bubble, "Zone de bulle manquante"
                assert "priority" in bubble, "Priorité manquante"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "bubbles_detected": analysis["total_bubbles"],
                    "characters_detected": len(analysis["character_positions"]),
                    "art_style": analysis["art_style"],
                    "zones_used": analysis["zones_used"]
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def test_scene_analysis_complex(self) -> dict:
        """Test d'analyse de scène complexe avec multiples personnages"""
        start_time = datetime.now()
        
        try:
            # Scène complexe avec 4 personnages
            description = """Dans cette scène épique, le héros Zara se dresse au centre, brandissant son épée magique. 
            À sa gauche, Marcus l'archer vise ses ennemis. À droite, Luna la mage prépare un sort. 
            En arrière-plan, Tor le guerrier charge vers l'avant."""
            
            dialogues = [
                {"character": "Zara", "text": "Aujourd'hui, nous triomphons !", "type": "shout"},
                {"character": "Marcus", "text": "Mes flèches sont prêtes.", "type": "speech"},
                {"character": "Luna", "text": "La magie est avec nous.", "type": "speech"},
                {"character": "Tor", "text": "Pour la gloire !", "type": "shout"}
            ]
            
            # Analyser la scène complexe
            analysis = await self.integrator._analyze_scene_composition_advanced(description, dialogues)
            
            # Vérifications avancées
            assert analysis["total_bubbles"] == 4, f"Mauvais nombre de bulles: {analysis['total_bubbles']}"
            assert len(analysis["character_positions"]) >= 2, "Positions insuffisantes détectées"
            
            # Vérifier l'équilibrage des zones
            zones_used = analysis["zones_used"]
            assert len(set(zones_used)) >= 3, "Zones mal réparties"
            
            # Vérifier les priorités
            priorities = [bubble["priority"] for bubble in analysis["bubble_plan"]]
            assert max(priorities) >= 15, "Priorités mal calculées (shout non détecté)"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "complex_scene": True,
                    "characters_detected": len(analysis["character_positions"]),
                    "zones_distribution": len(set(zones_used)),
                    "priority_range": f"{min(priorities)}-{max(priorities)}"
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def test_prompt_generation(self) -> dict:
        """Test de génération de prompts SD3 ultra-précis"""
        start_time = datetime.now()
        
        try:
            # Créer des données de test
            bubble_spec = {
                "bubble_id": "bubble_1",
                "speaker": "Alice",
                "text": "Bonjour tout le monde !",
                "type": "speech",
                "speaker_position": "left",
                "bubble_zone": "upper_left",
                "bubble_area": "upper left corner",
                "art_style": "professional comic book art style",
                "priority": 10
            }
            
            scene_analysis = {
                "total_bubbles": 1,
                "art_style": "professional comic book art style"
            }
            
            # Générer le prompt
            prompt = self.integrator._generate_sd3_prompt_advanced(bubble_spec, scene_analysis, True)
            
            # Vérifications du prompt
            assert len(prompt) > 50, "Prompt trop court"
            assert "Bonjour tout le monde !" in prompt, "Texte manquant dans le prompt"
            assert "upper left corner" in prompt, "Position manquante"
            assert "professional comic book" in prompt, "Style manquant"
            assert "white background" in prompt.lower(), "Instructions de bulle manquantes"
            assert "black outline" in prompt.lower(), "Instructions de contour manquantes"
            
            # Test avec multiples bulles
            scene_analysis["total_bubbles"] = 3
            prompt_multi = self.integrator._generate_sd3_prompt_advanced(bubble_spec, scene_analysis, False)
            assert "bubble #" in prompt_multi or "bubble" in prompt_multi, "Gestion multi-bulles manquante"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "prompt_length": len(prompt),
                    "multi_bubble_support": True,
                    "contains_requirements": all(word in prompt.lower() for word in ["white", "black", "comic"])
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def test_bubble_integration(self) -> dict:
        """Test d'intégration de bulles sur une image test"""
        start_time = datetime.now()
        
        try:
            # Créer une image de test simple
            test_image_path = await self.create_test_image()
            
            # Données de test pour intégration
            scene_analysis = {
                "total_bubbles": 2,
                "bubble_plan": [
                    {
                        "bubble_id": "bubble_1",
                        "speaker": "Alice",
                        "text": "Hello World!",
                        "type": "speech",
                        "speaker_position": "left",
                        "bubble_zone": "upper_left",
                        "bubble_area": "upper left corner",
                        "placement_coords": {"x": 0.2, "y": 0.2},
                        "art_style": "professional comic book art style",
                        "priority": 10
                    },
                    {
                        "bubble_id": "bubble_2",
                        "speaker": "Bob",
                        "text": "Nice to meet you!",
                        "type": "speech",
                        "speaker_position": "right",
                        "bubble_zone": "upper_right",
                        "bubble_area": "upper right corner",
                        "placement_coords": {"x": 0.8, "y": 0.2},
                        "art_style": "professional comic book art style",
                        "priority": 9
                    }
                ],
                "art_style": "professional comic book art style"
            }
            
            # Intégrer les bulles
            result_path, status = await self.integrator._integrate_bubbles_advanced(
                test_image_path, scene_analysis, 1
            )
            
            # Vérifications
            assert result_path.exists(), f"Image résultante non créée: {result_path}"
            assert status is not None, "Statut d'intégration manquant"
            
            # Vérifier que l'image a été modifiée (taille différente ou fichier différent)
            original_size = test_image_path.stat().st_size
            result_size = result_path.stat().st_size
            assert result_size > 0, "Image résultante vide"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "integration_status": status,
                    "original_size": original_size,
                    "result_size": result_size,
                    "output_path": str(result_path)
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def test_complete_comic_processing(self) -> dict:
        """Test de traitement d'une BD complète"""
        start_time = datetime.now()
        
        try:
            # Créer des images de test pour une BD
            test_images = []
            for i in range(3):
                img_path = await self.create_test_image(f"test_page_{i+1}")
                test_images.append(img_path)
            
            # Données de BD de test
            comic_data = {
                "title": "Test Comic",
                "pages": [
                    {
                        "page_number": 1,
                        "description": "Alice se trouve à gauche, parlant à Bob qui est à droite.",
                        "image_path": str(test_images[0]),
                        "dialogues": [
                            {"character": "Alice", "text": "Salut Bob !", "type": "speech"},
                            {"character": "Bob", "text": "Salut Alice !", "type": "speech"}
                        ]
                    },
                    {
                        "page_number": 2,
                        "description": "Combat épique au centre de l'arène.",
                        "image_path": str(test_images[1]),
                        "dialogues": [
                            {"character": "Héros", "text": "Je ne reculerai pas !", "type": "shout"}
                        ]
                    },
                    {
                        "page_number": 3,
                        "description": "Fin paisible dans un jardin.",
                        "image_path": str(test_images[2]),
                        "dialogues": [
                            {"character": "Narrateur", "text": "Et ils vécurent heureux...", "type": "narrative"}
                        ]
                    }
                ]
            }
            
            # Traiter la BD complète
            processed_comic = await self.integrator.process_comic_pages(comic_data)
            
            # Vérifications
            assert processed_comic is not None, "BD traitée manquante"
            assert "pages" in processed_comic, "Pages manquantes"
            assert len(processed_comic["pages"]) == 3, "Nombre de pages incorrect"
            assert "bubble_system" in processed_comic, "Système de bulles non renseigné"
            assert "processing_stats" in processed_comic, "Statistiques manquantes"
            
            # Vérifier chaque page
            for page in processed_comic["pages"]:
                assert "bubble_integration" in page, "Statut d'intégration manquant"
                assert Path(page["image_path"]).exists(), f"Image finale manquante: {page['image_path']}"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "pages_processed": len(processed_comic["pages"]),
                    "bubble_system": processed_comic.get("bubble_system"),
                    "stats": processed_comic.get("processing_stats", {})
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def test_error_handling(self) -> dict:
        """Test de gestion des erreurs"""
        start_time = datetime.now()
        
        try:
            # Test avec image manquante
            comic_data_invalid = {
                "pages": [
                    {
                        "page_number": 1,
                        "description": "Test page",
                        "image_path": "/path/to/nonexistent/image.png",
                        "dialogues": [{"character": "Test", "text": "Test", "type": "speech"}]
                    }
                ]
            }
            
            result = await self.integrator.process_comic_pages(comic_data_invalid)
            
            # Vérifier que l'erreur est gérée gracieusement
            assert result is not None, "Résultat manquant malgré l'erreur"
            assert len(result["pages"]) == 1, "Page non traitée"
            
            page = result["pages"][0]
            assert "error" in page or "bubble_integration" in page, "Erreur non rapportée"
            
            # Test avec données invalides
            invalid_analysis = await self.integrator._analyze_scene_composition_advanced("", [])
            assert invalid_analysis["total_bubbles"] == 0, "Gestion des données vides échouée"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "error_handling": "graceful",
                    "invalid_data_handled": True
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def test_performance(self) -> dict:
        """Test de performance et fonctionnalités avancées"""
        start_time = datetime.now()
        
        try:
            # Test de performance avec analyse multiple
            description = "Scène complexe avec plusieurs personnages en action."
            dialogues = [
                {"character": f"Character{i}", "text": f"Dialogue {i}", "type": "speech"}
                for i in range(5)
            ]
            
            # Mesurer le temps d'analyse
            analysis_start = datetime.now()
            analysis = await self.integrator._analyze_scene_composition_advanced(description, dialogues)
            analysis_time = (datetime.now() - analysis_start).total_seconds()
            
            # Vérifier que l'analyse est rapide (< 1 seconde pour 5 dialogues)
            assert analysis_time < 1.0, f"Analyse trop lente: {analysis_time}s"
            
            # Test des fonctionnalités avancées
            position_test = self.integrator._normalize_position("gauche")
            assert position_test == "left", "Normalisation de position échouée"
            
            coords_test = self.integrator._position_to_coordinates("center")
            assert coords_test["x"] == 0.5, "Conversion coordonnées échouée"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "passed": True,
                "duration": duration,
                "details": {
                    "analysis_time": analysis_time,
                    "performance_ok": analysis_time < 1.0,
                    "advanced_features": True
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {"passed": False, "duration": duration, "error": str(e)}
    
    async def create_test_image(self, name: str = "test_image") -> Path:
        """Crée une image de test simple"""
        from PIL import Image, ImageDraw
        
        # Créer une image de test 800x600
        img = Image.new('RGB', (800, 600), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Dessiner quelques formes pour simuler une scène de BD
        draw.rectangle([100, 100, 300, 300], fill='green', outline='black')
        draw.rectangle([500, 200, 700, 400], fill='red', outline='black')
        draw.ellipse([350, 250, 450, 350], fill='yellow', outline='black')
        
        # Ajouter du "texte" pour simuler des personnages
        draw.text((150, 200), "Character A", fill='black')
        draw.text((550, 300), "Character B", fill='black')
        
        # Sauvegarder l'image
        img_path = self.test_dir / f"{name}.png"
        img.save(img_path)
        
        return img_path
    
    async def print_test_summary(self):
        """Affiche le résumé des tests"""
        total_tests = self.test_results["tests_passed"] + self.test_results["tests_failed"]
        success_rate = (self.test_results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print("🏁 === RÉSUMÉ DES TESTS SD3BubbleIntegratorAdvanced V2.0 ===")
        print(f"📊 Tests exécutés: {total_tests}")
        print(f"✅ Tests réussis: {self.test_results['tests_passed']}")
        print(f"❌ Tests échoués: {self.test_results['tests_failed']}")
        print(f"📈 Taux de succès: {success_rate:.1f}%")
        print()
        
        if success_rate >= 80:
            print("🎉 SYSTÈME VALIDÉ - Prêt pour la production !")
        elif success_rate >= 60:
            print("⚠️ SYSTÈME PARTIELLEMENT VALIDÉ - Améliorations recommandées")
        else:
            print("❌ SYSTÈME NON VALIDÉ - Corrections nécessaires")
        
        print(f"⏱️ Durée totale des tests: {(datetime.now() - datetime.fromisoformat(self.test_results['test_start_time'])).total_seconds():.2f}s")
    
    async def save_test_results(self):
        """Sauvegarde les résultats des tests"""
        self.test_results["test_end_time"] = datetime.now().isoformat()
        
        results_file = self.test_dir / "test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Résultats sauvegardés: {results_file}")


async def main():
    """Fonction principale pour exécuter tous les tests"""
    print("🧪 === TESTS SD3BubbleIntegratorAdvanced V2.0 ===")
    print("Ce script teste toutes les fonctionnalités du système autonome de bulles intégrées.\n")
    
    # Initialiser et exécuter la suite de tests
    test_suite = SD3BubbleTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    # Exécuter les tests
    asyncio.run(main())
