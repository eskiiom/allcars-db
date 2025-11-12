#!/usr/bin/env python3
"""
Test du scraper technique Auto-Data - Validation rapide
Teste le scraper sur une marque populaire avec quelques modèles
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autodata_technical_scraper import AutoDataTechnicalScraper

def test_popular_brand():
    """Test sur une marque populaire (BMW)."""
    print("🧪 TEST DU SCRAPER TECHNIQUE AUTO-DATA")
    print("=" * 50)
    print("🎯 Test sur BMW (marque populaire)")
    print("📄 Limitation : 5 modèles maximum")
    print()
    
    try:
        # Initialiser le scraper
        scraper = AutoDataTechnicalScraper(headless=True)
        
        # Rechercher BMW dans la liste des marques
        brand_info = None
        for brand in scraper.brands_list:
            if "BMW" in brand['name']:
                brand_info = brand
                break
        
        if not brand_info:
            print("❌ BMW non trouvée dans la liste des marques")
            return False
        
        print(f"✅ Marque trouvée: {brand_info['name']} (ID: {brand_info['id']})")
        
        # Tester avec seulement 5 modèles
        brand_data = scraper.scrape_brand_technical_data(
            brand_info['name'], 
            brand_info['id'],
            limit_models=5
        )
        
        if brand_data:
            print(f"✅ Scraping réussi!")
            print(f"   📊 Modèles traités: {brand_data['scraped_models']}/{brand_data['total_models']}")
            
            # Analyser les données extraites
            analyze_technical_data(brand_data)
            
            # Sauvegarder les données de test
            test_data = {
                'metadata': {
                    'test_date': brand_data['scraped_at'],
                    'scraper_version': 'v1.0_technical_specs',
                    'test_purpose': 'validation_scraper_functionality',
                    'brand_tested': brand_info['name']
                },
                'technical_data': {brand_info['name']: brand_data}
            }
            
            output_file = scraper.save_technical_data(test_data, "data/autodata_technical_test_bmw.json")
            
            if output_file:
                print(f"💾 Données de test sauvegardées: {output_file}")
                return True
            else:
                print("❌ Échec sauvegarde des données de test")
                return False
        else:
            print("❌ Échec du scraping")
            return False
            
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        return False
    
    finally:
        if 'scraper' in locals():
            scraper.close()

def analyze_technical_data(brand_data):
    """Analyse les données techniques extraites."""
    print("\n📊 ANALYSE DES DONNÉES EXTRAITES:")
    print("-" * 40)
    
    models = brand_data['models']
    
    for model_name, model_data in models.items():
        print(f"\n🚗 {model_name}:")
        specs = model_data['specifications']
        
        # Compter les specs par catégorie
        categories = {
            'basic': len(specs.get('basic', {})),
            'performance': len(specs.get('performance', {})),
            'dimensions': len(specs.get('dimensions', {})),
            'engine': len(specs.get('engine', {})),
            'transmission': len(specs.get('transmission', {})),
            'equipment': len(specs.get('equipment', []))
        }
        
        print(f"   📋 Specs de base: {categories['basic']}")
        print(f"   ⚡ Performance: {categories['performance']}")
        print(f"   📏 Dimensions: {categories['dimensions']}")
        print(f"   🔧 Moteur: {categories['engine']}")
        print(f"   ⚙️ Transmission: {categories['transmission']}")
        print(f"   🎯 Équipements: {categories['equipment']}")
        
        # Afficher quelques exemples de specs importantes
        if specs.get('performance', {}).get('power_hp'):
            power = specs['performance']['power_hp']
            print(f"   💪 Puissance: {power}")
        
        if specs.get('performance', {}).get('acceleration_0_100'):
            accel = specs['performance']['acceleration_0_100']
            print(f"   🏁 0-100 km/h: {accel}")
        
        if specs.get('dimensions', {}).get('weight'):
            weight = specs['dimensions']['weight']
            print(f"   ⚖️ Poids: {weight}")

def test_multiple_brands():
    """Test sur plusieurs marques populaires."""
    print("\n🧪 TEST MULTI-MARQUES")
    print("=" * 50)
    
    # Liste des marques de test
    test_brands = ["Toyota", "BMW", "Audi"]
    
    try:
        scraper = AutoDataTechnicalScraper(headless=True)
        
        test_results = {}
        
        for brand_name in test_brands:
            print(f"\n🎯 Test {brand_name}...")
            
            # Rechercher la marque
            brand_info = None
            for brand in scraper.brands_list:
                if brand_name.lower() in brand['name'].lower():
                    brand_info = brand
                    break
            
            if brand_info:
                brand_data = scraper.scrape_brand_technical_data(
                    brand_info['name'], 
                    brand_info['id'],
                    limit_models=3  # Seulement 3 modèles par marque
                )
                
                if brand_data:
                    test_results[brand_name] = brand_data
                    print(f"   ✅ Succès: {brand_data['scraped_models']} modèles")
                else:
                    print(f"   ❌ Échec")
                    test_results[brand_name] = {}
            else:
                print(f"   ⚠️ Marque non trouvée")
                test_results[brand_name] = {}
            
            # Pause entre les marques
            import time
            time.sleep(3)
        
        # Sauvegarder les résultats du test
        test_summary = {
            'metadata': {
                'test_date': '2025-11-12T08:19:00Z',
                'test_type': 'multi_brand_validation',
                'brands_tested': test_brands
            },
            'results': test_results
        }
        
        output_file = scraper.save_technical_data(
            {'metadata': test_summary['metadata'], 'brands_technical_data': test_results},
            "data/autodata_technical_test_multi.json"
        )
        
        if output_file:
            print(f"\n💾 Résultats test multi-marques: {output_file}")
            return True
        
    except Exception as e:
        print(f"❌ Erreur test multi-marques: {e}")
        return False
    
    finally:
        if 'scraper' in locals():
            scraper.close()

def main():
    """Menu principal de test."""
    print("🔧 AUTODATA TECHNICAL SCRAPER - TESTS DE VALIDATION")
    print("=" * 55)
    print()
    print("Choisissez un test :")
    print("1. Test rapide BMW (5 modèles)")
    print("2. Test multi-marques (Toyota, BMW, Audi - 3 modèles chacune)")
    print("3. Quitter")
    print()
    
    while True:
        try:
            choice = input("Votre choix (1-3): ").strip()
            
            if choice == "1":
                print("\n" + "="*50)
                test_popular_brand()
                break
                
            elif choice == "2":
                print("\n" + "="*50)
                test_multiple_brands()
                break
                
            elif choice == "3":
                print("👋 Au revoir!")
                break
                
            else:
                print("❌ Choix invalide. Choisissez 1, 2 ou 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Test interrompu.")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()