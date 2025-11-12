#!/usr/bin/env python3
"""
Test de la base de données étendue du scraper technique autonome
Démontre la couverture de marques et modèles
"""

import json
from technical_scraper_autonomous import AutonomousTechnicalScraper

def test_expanded_database():
    """Test de la base de données étendue avec plusieurs marques."""

    print("🚗 TEST DE LA BASE DE DONNÉES ÉTENDUE")
    print("=" * 50)

    scraper = AutonomousTechnicalScraper()

    # Test avec différentes marques représentatives
    test_cases = [
        ("BMW", ["118i", "X5", "i8", "M340i"]),
        ("Audi", ["A3", "Q7", "TT", "e-tron"]),
        ("Mercedes-Benz", ["A-Class", "GLE", "S-Class", "EQC"]),
        ("Toyota", ["Yaris", "RAV4", "Supra", "Mirai"]),
        ("Honda", ["Civic", "CR-V", "NSX", "e"]),
        ("Tesla", ["Model 3", "Model S", "Cybertruck"]),
        ("Peugeot", ["208", "3008", "RCZ", "e-208"]),
        ("Ford", ["Fiesta", "Kuga", "Mustang", "F-150"]),
        ("Hyundai", ["i20", "Tucson", "Ioniq 5", "Nexo"]),
        ("Volkswagen", ["Golf", "Tiguan", "ID.4", "Arteon"])
    ]

    results = {}

    for brand, models in test_cases:
        print(f"\n🏷️ Test de {brand}:")
        brand_results = {}

        for model in models:
            try:
                specs = scraper.generate_technical_specs(brand, model)
                if specs:
                    # Afficher un résumé
                    fuel = specs.get("basic", {}).get("fuel_type", "N/A")
                    power = specs.get("performance", {}).get("power_hp", "N/A")
                    weight = specs.get("dimensions", {}).get("weight", "N/Akg").replace("kg", "")
                    confidence = specs.get("_metadata", {}).get("confidence", "N/A")

                    print(f"   ✅ {model}: {power}hp, {fuel}, {weight}kg ({confidence})")

                    brand_results[model] = {
                        "power_hp": power,
                        "fuel_type": fuel,
                        "weight_kg": weight,
                        "confidence": confidence
                    }
                else:
                    print(f"   ❌ {model}: Échec génération")
                    brand_results[model] = {"error": "generation_failed"}

            except Exception as e:
                print(f"   ❌ {model}: Erreur {e}")
                brand_results[model] = {"error": str(e)}

        results[brand] = brand_results

    # Statistiques finales
    print(f"\n📊 STATISTIQUES FINALES:")
    print("=" * 30)

    total_tests = sum(len(models) for models in test_cases)
    successful_tests = 0
    high_confidence = 0

    for brand, brand_results in results.items():
        brand_success = 0
        brand_high_conf = 0

        for model, result in brand_results.items():
            if "error" not in result:
                successful_tests += 1
                brand_success += 1
                if result.get("confidence") == "high":
                    high_confidence += 1
                    brand_high_conf += 1

        print(f"{brand}: {brand_success}/{len(brand_results)} modèles ({brand_high_conf} haute confiance)")

    print(f"\n🎯 RÉSULTATS GLOBAUX:")
    print(f"   • Tests totaux: {total_tests}")
    print(f"   • Réussites: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"   • Haute confiance: {high_confidence} ({high_confidence/total_tests*100:.1f}%)")
    print(f"   • Marques testées: {len(test_cases)}")

    # Sauvegarder les résultats
    with open("data/expanded_database_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "test_results": results,
            "statistics": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "high_confidence": high_confidence,
                "success_rate": successful_tests/total_tests*100,
                "high_confidence_rate": high_confidence/total_tests*100,
                "brands_tested": len(test_cases)
            }
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Résultats sauvegardés: data/expanded_database_test_results.json")

    return results

if __name__ == "__main__":
    test_expanded_database()