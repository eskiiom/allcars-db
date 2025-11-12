#!/usr/bin/env python3
"""
Testeur Simple Auto-Data - Version Fonctionnelle
Test basique avec URLs directes et extraction simple
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_auto_data_simple():
    """Test simple et fonctionnel d'Auto-Data."""
    
    print("=== TEST AUTO-DATA SIMPLE ===")
    
    # Configuration driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # URLs de test directe
    test_urls = [
        "https://www.auto-data.net/bg/brand/86/",   # BMW
        "https://www.auto-data.net/bg/brand/140/",  # Toyota
        "https://www.auto-data.net/bg/brand/2/",    # Audi
    ]
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        try:
            print(f"[{i}/3] Test: {url}")
            
            driver.get(url)
            time.sleep(3)
            
            # Chercher des liens de modèles
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='car']")
            print(f"   Liens trouvés: {len(links)}")
            
            if links:
                # Tester le premier modèle
                first_link = links[0]
                model_url = first_link.get_attribute("href")
                model_text = first_link.text.strip()
                
                print(f"   Premier modèle: {model_text}")
                print(f"   URL: {model_url}")
                
                # Naviguer vers le modèle
                driver.get(model_url)
                time.sleep(3)
                
                # Extraire quelques specs basiques
                specs = {}
                
                # Chercher du contenu textuel avec specs
                page_text = driver.page_source.lower()
                
                # Mots-clés de spécifications
                keywords = ['power', 'torque', 'speed', 'fuel', 'consumption', 'weight', 'length']
                
                for keyword in keywords:
                    if keyword in page_text:
                        specs[keyword] = True
                
                results.append({
                    'brand_page': url,
                    'model_text': model_text,
                    'model_url': model_url,
                    'specs_found': list(specs.keys()),
                    'success': len(specs) > 0
                })
                
                print(f"   SUCCESS: {len(specs)} spec types")
            
        except Exception as e:
            print(f"   Erreur: {e}")
            continue
    
    driver.quit()
    
    # Sauvegarder résultats
    output_file = "data/simple_auto_data_test.json"
    with open(output_file, 'w') as f:
        json.dump({
            'test_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'results': results
        }, f, indent=2)
    
    print(f"\nRESULTATS SAUVEGARDES: {output_file}")
    print(f"Modèles testés: {len(results)}")
    successful = sum(1 for r in results if r['success'])
    print(f"Avec specs: {successful}")
    
    return results

if __name__ == "__main__":
    test_auto_data_simple()