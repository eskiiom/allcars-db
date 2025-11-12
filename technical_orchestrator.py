#!/usr/bin/env python3
"""
Orchestrateur Technique Auto-Data - Extension du système automobile
Gestion complète du scraping et analyse des spécifications techniques
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import argparse

class TechnicalOrchestrator:
    """Orchestrateur pour le système technique Auto-Data."""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
    
    def display_banner(self):
        """Affiche la bannière du système technique."""
        print("🚗" * 20)
        print("🔧 AUTODATA TECHNICAL SYSTEM v1.0")
        print("🏗️ Spécifications Techniques pour Site de Suivi")
        print("📊 Base de Données Véhicule Complète")
        print("🚗" * 20)
        print()
    
    def display_menu(self):
        """Affiche le menu principal."""
        print("📋 OPTIONS DISPONIBLES:")
        print("   0. [DÉFAUT] 🔄 Scraper marques populaires + Analyser")
        print("   1. 🎯 Scraper une marque spécifique (ex: BMW)")
        print("   2. 🧪 Test rapide du scraper (BMW - 5 modèles)")
        print("   3. 📊 Analyser données existantes")
        print("   4. 🌐 Générer données web-ready")
        print("   5. 📚 Créer guide d'intégration")
        print("   6. 🔍 Scraping complet (toutes marques)")
        print("   7. 📈 Analyse complète avec rapports")
        print("   8. 🚗 Demo intégration site (données d'exemple)")
        print("   9. 📊 Statistiques techniques + Quit")
        print()
    
    def run_technical_scraper(self, mode="popular"):
        """Lance le scraper technique."""
        if mode == "popular":
            print("🚀 Lancement scraping marques populaires...")
            cmd = [sys.executable, "autodata_technical_scraper.py", "--popular-brands"]
        elif mode == "full":
            print("🌍 Lancement scraping complet...")
            cmd = [sys.executable, "autodata_technical_scraper.py"]
        else:
            return {"success": False, "error": "Mode de scraping invalide"}
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                print(f"✅ Scraping technique réussi")
                return {
                    'success': True,
                    'output': result.stdout,
                    'mode': mode
                }
            else:
                print(f"❌ Échec scraping technique: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'mode': mode
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout du scraping (1 heure)")
            return {
                'success': False,
                'error': 'Timeout after 1 hour',
                'mode': mode
            }
        except Exception as e:
            print(f"💥 Erreur scraping: {e}")
            return {
                'success': False,
                'error': str(e),
                'mode': mode
            }
    
    def run_specific_brand_scraping(self, brand_name):
        """Lance le scraping d'une marque spécifique."""
        print(f"🎯 Lancement scraping pour {brand_name}...")
        
        try:
            cmd = [sys.executable, "autodata_technical_scraper.py", "--brand", brand_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                print(f"✅ Scraping {brand_name} réussi")
                return {
                    'success': True,
                    'brand': brand_name,
                    'output': result.stdout
                }
            else:
                print(f"❌ Échec scraping {brand_name}: {result.stderr}")
                return {
                    'success': False,
                    'brand': brand_name,
                    'error': result.stderr
                }
                
        except Exception as e:
            print(f"💥 Erreur scraping {brand_name}: {e}")
            return {
                'success': False,
                'brand': brand_name,
                'error': str(e)
            }
    
    def run_technical_test(self):
        """Lance le test du scraper technique."""
        print("🧪 Lancement test technique...")
        
        try:
            cmd = [sys.executable, "test_autodata_technical.py"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            if result.returncode == 0:
                print("✅ Test technique réussi")
                return {
                    'success': True,
                    'output': result.stdout
                }
            else:
                print(f"❌ Échec test: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            print(f"💥 Erreur test: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_data_analysis(self, specific_file=None):
        """Lance l'analyse des données techniques."""
        print("📊 Lancement analyse des données...")
        
        try:
            if specific_file:
                cmd = [sys.executable, "analyze_technical_data.py", specific_file]
            else:
                cmd = [sys.executable, "analyze_technical_data.py"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Analyse des données réussie")
                return {
                    'success': True,
                    'output': result.stdout
                }
            else:
                print(f"❌ Échec analyse: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            print(f"💥 Erreur analyse: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_web_ready_data(self):
        """Génère les données prêtes pour le web."""
        print("🌐 Génération données web-ready...")
        
        # Chercher le fichier de données techniques le plus récent
        data_dir = Path("data")
        tech_files = list(data_dir.glob("autodata_technical_specs_*.json"))
        
        if not tech_files:
            print("❌ Aucun fichier de données techniques trouvé")
            print("💡 Lancez d'abord: option 0 ou 6")
            return {"success": False, "error": "No technical data files found"}
        
        latest_file = max(tech_files, key=lambda x: x.stat().st_mtime)
        print(f"📁 Fichier détecté: {latest_file.name}")
        
        # Lancer l'analyse
        analysis_result = self.run_data_analysis(str(latest_file))
        
        if analysis_result['success']:
            # Vérifier les fichiers générés
            web_files = [
                data_dir / "autodata_web_ready.json",
                data_dir / "autodata_web_ready.csv",
                Path("docs/autodata_web_integration_guide.md")
            ]
            
            generated_files = [str(f) for f in web_files if f.exists()]
            
            print(f"✅ Données web générées:")
            for file_path in generated_files:
                print(f"   📄 {file_path}")
            
            return {
                'success': True,
                'generated_files': generated_files,
                'source_file': str(latest_file)
            }
        else:
            return analysis_result
    
    def create_integration_guide(self):
        """Crée le guide d'intégration."""
        print("📚 Génération guide d'intégration...")
        
        # Utiliser l'analyseur pour créer le guide
        data_dir = Path("data")
        tech_files = list(data_dir.glob("autodata_technical_specs_*.json"))
        
        if tech_files:
            latest_file = max(tech_files, key=lambda x: x.stat().st_mtime)
            
            try:
                # Import dynamique pour éviter les erreurs si les modules ne sont pas disponibles
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from analyze_technical_data import TechnicalDataAnalyzer
                
                analyzer = TechnicalDataAnalyzer(str(latest_file))
                if analyzer.data:
                    analyzer.generate_website_integration_guide()
                    return {"success": True, "guide_created": True}
                else:
                    return {"success": False, "error": "No data loaded"}
                    
            except Exception as e:
                print(f"❌ Erreur génération guide: {e}")
                return {"success": False, "error": str(e)}
        else:
            print("❌ Aucun fichier de données trouvé")
            return {"success": False, "error": "No data files"}
    
    def run_full_pipeline(self):
        """Lance le pipeline complet: scraping + analyse."""
        print("🔄 LANCEMENT PIPELINE COMPLET")
        print("=" * 40)
        
        # Étape 1: Scraping marques populaires
        scraping_result = self.run_technical_scraper("popular")
        
        if not scraping_result['success']:
            print("❌ Échec du scraping - Arrêt du pipeline")
            return False
        
        # Étape 2: Analyse des données
        analysis_result = self.run_data_analysis()
        
        if not analysis_result['success']:
            print("⚠️ Échec de l'analyse mais scraping réussi")
        
        # Étape 3: Génération données web
        web_result = self.generate_web_ready_data()
        
        # Étape 4: Guide d'intégration
        guide_result = self.create_integration_guide()
        
        # Résumé
        print("\n🏆 PIPELINE COMPLET TERMINÉ")
        print("=" * 35)
        
        results = {
            'scraping': scraping_result,
            'analysis': analysis_result,
            'web_generation': web_result,
            'guide': guide_result
        }
        
        if all(r['success'] for r in [scraping_result, web_result, guide_result]):
            print("✅ Pipeline complet réussi!")
            print("🌐 Données prêtes pour votre site de suivi!")
        else:
            print("⚠️ Pipeline terminé avec quelques erreurs")
        
        return results
    
    def show_technical_statistics(self):
        """Affiche les statistiques du système technique."""
        print("📊 STATISTIQUES SYSTÈME TECHNIQUE")
        print("=" * 45)
        
        data_dir = Path("data")
        
        # Fichiers techniques
        tech_files = list(data_dir.glob("autodata_technical_specs_*.json"))
        web_files = list(data_dir.glob("autodata_web_ready.*"))
        test_files = list(data_dir.glob("autodata_technical_test_*.json"))
        
        print(f"📁 Fichiers de données techniques: {len(tech_files)}")
        print(f"🌐 Fichiers web-ready: {len(web_files)}")
        print(f"🧪 Fichiers de test: {len(test_files)}")
        
        # Dernier fichier technique
        if tech_files:
            latest_tech = max(tech_files, key=lambda x: x.stat().st_mtime)
            print(f"📄 Dernière donnée technique: {latest_tech.name}")
            
            try:
                with open(latest_tech, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                brands_count = len(data.get('brands_technical_data', {}))
                models_count = sum(
                    brand.get('scraped_models', 0) 
                    for brand in data.get('brands_technical_data', {}).values()
                )
                
                print(f"🏷️ Marques avec données: {brands_count}")
                print(f"🚗 Modèles avec specs: {models_count}")
                
            except Exception as e:
                print(f"⚠️ Erreur lecture statistiques: {e}")
        
        # Documentation
        guide_file = Path("docs/autodata_web_integration_guide.md")
        print(f"📚 Guide d'intégration: {'✅' if guide_file.exists() else '❌'}")
        
        # Scripts disponibles
        scripts = [
            ("autodata_technical_scraper.py", "Scraper technique principal"),
            ("test_autodata_technical.py", "Tests de validation"),
            ("analyze_technical_data.py", "Analyseur de données"),
            ("technical_orchestrator.py", "Ce script")
        ]
        
        print(f"\n🔧 Scripts du système technique:")
        for script, description in scripts:
            exists = Path(script).exists()
            print(f"   {'✅' if exists else '❌'} {script:<30} - {description}")
        
        print("=" * 45)
    
    def run(self):
        """Boucle principale de l'orchestrateur."""
        self.display_banner()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("💡 Sélectionnez une option (0-9): ").strip()
                
                if not choice:
                    choice = "0"  # Default option
                
                if choice == "0":
                    print("\n🔄 Lancement pipeline complet (populaire + analyse)...")
                    self.start_time = datetime.now()
                    results = self.run_full_pipeline()
                    if results:
                        self.results['full_pipeline'] = results
                
                elif choice == "1":
                    print("\n🎯 Scraping marque spécifique...")
                    brand = input("Nom de la marque (ex: BMW, Toyota): ").strip()
                    if brand:
                        self.start_time = datetime.now()
                        result = self.run_specific_brand_scraping(brand)
                        self.results[f'specific_brand_{brand}'] = result
                
                elif choice == "2":
                    print("\n🧪 Test rapide du scraper...")
                    self.start_time = datetime.now()
                    result = self.run_technical_test()
                    self.results['technical_test'] = result
                
                elif choice == "3":
                    print("\n📊 Analyse des données...")
                    self.start_time = datetime.now()
                    result = self.run_data_analysis()
                    self.results['data_analysis'] = result
                
                elif choice == "4":
                    print("\n🌐 Génération données web-ready...")
                    self.start_time = datetime.now()
                    result = self.generate_web_ready_data()
                    self.results['web_generation'] = result
                
                elif choice == "5":
                    print("\n📚 Création guide d'intégration...")
                    self.start_time = datetime.now()
                    result = self.create_integration_guide()
                    self.results['integration_guide'] = result
                
                elif choice == "6":
                    print("\n🔍 Scraping complet (toutes marques)...")
                    self.start_time = datetime.now()
                    result = self.run_technical_scraper("full")
                    self.results['full_scraping'] = result
                
                elif choice == "7":
                    print("\n📈 Analyse complète avec rapports...")
                    print("   🔍 Scraping marques populaires + Analyse + Web-ready")
                    self.start_time = datetime.now()
                    results = self.run_full_pipeline()
                    if results:
                        self.results['complete_analysis'] = results
                
                elif choice == "8":
                    print("\n🚗 Demo intégration site...")
                    print("💡 Cette option montrerait comment intégrer les données dans un site web")
                    print("📋 Voir: docs/autodata_web_integration_guide.md")
                
                elif choice == "9":
                    print("\n👋 Affichage des statistiques et sortie...")
                    self.show_technical_statistics()
                    return
                
                else:
                    print("❌ Option invalide! Choisissez 0-9.")
                    continue
                
                # Demander si continuer
                print()
                continue_choice = input("🔄 Continuer avec une autre opération? (y/n): ").strip().lower()
                if continue_choice in ['n', 'no', 'non']:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n⏹️ Opération annulée par l'utilisateur.")
                break
            except Exception as e:
                print(f"\n💥 Erreur inattendue: {e}")
                continue
        
        print("\n👋 Merci d'avoir utilisé le Système Technique Auto-Data!")

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Orchestrateur Système Technique Auto-Data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python technical_orchestrator.py           # Mode interactif
  python technical_orchestrator.py --quick   # Pipeline rapide
  python technical_orchestrator.py --analyze # Analyse seulement
        """
    )
    
    parser.add_argument('--quick', action='store_true',
                       help='Lance le pipeline rapide (populaire + analyse)')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyse seulement les données existantes')
    
    args = parser.parse_args()
    
    orchestrator = TechnicalOrchestrator()
    
    if args.quick:
        print("🚀 Mode rapide: pipeline populaire + analyse")
        orchestrator.run_full_pipeline()
    elif args.analyze:
        print("📊 Mode analyse: seulement l'analyse des données")
        orchestrator.run_data_analysis()
    else:
        # Mode interactif
        orchestrator.run()

if __name__ == "__main__":
    main()