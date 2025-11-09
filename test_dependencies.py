#!/usr/bin/env python3
"""
Test de Vérification des Dépendances
Vérifie que toutes les dépendances réelles sont installées et utilisables
"""

import sys
import importlib.util

def test_dependency(module_name, description):
    """Teste si un module peut être importé."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            module = importlib.import_module(module_name)
            print(f"✅ {description}: {module_name} - OK")
            return True
        else:
            print(f"❌ {description}: {module_name} - MANQUANT")
            return False
    except Exception as e:
        print(f"⚠️  {description}: {module_name} - ERREUR: {e}")
        return False

def test_selenium_specific():
    """Test des imports spécifiques Selenium."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium: Tous les imports spécifiques - OK")
        return True
    except ImportError as e:
        print(f"❌ Selenium: Import spécifique manquant: {e}")
        return False

def main():
    print("🧪 Test des Dépendances Réelles du Scraper")
    print("=" * 50)
    
    # Modules Python natifs (système)
    print("\n📚 Modules Python Natifs:")
    native_modules = [
        ("json", "Manipulation JSON"),
        ("re", "Expressions régulières"),
        ("datetime", "Gestion des dates"),
        ("pathlib", "Manipulation de fichiers"),
        ("argparse", "Parsing d'arguments"),
        ("logging", "Journalisation"),
        ("time", "Gestion du temps"),
        ("random", "Génération aléatoire"),
        ("sys", "Paramètres système"),
        ("collections", "Structures de données")
    ]
    
    for module_name, description in native_modules:
        test_dependency(module_name, description)
    
    # Dépendances externes
    print("\n🌐 Dépendances Externes:")
    external_deps = [
        ("selenium", "Automatisation navigateur"),
        ("webdriver_manager", "Gestion drivers (optionnel)")
    ]
    
    all_good = True
    for module_name, description in external_deps:
        if not test_dependency(module_name, description):
            all_good = False
    
    # Test spécifique Selenium
    print("\n🔍 Tests Spécifiques Selenium:")
    if not test_selenium_specific():
        all_good = False
    
    # Résultat final
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 SUCCÈS: Toutes les dépendances requises sont disponibles!")
        print("🚀 Le script autoscout24_scraper.py peut être exécuté.")
    else:
        print("⚠️  PROBLÈME: Certaines dépendances manquent.")
        print("📦 Installez avec: pip install -r requirements.txt")
    
    return all_good

if __name__ == "__main__":
    main()