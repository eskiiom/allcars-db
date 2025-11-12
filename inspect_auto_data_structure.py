#!/usr/bin/env python3
"""
Analyseur de Structure Auto-Data
Analyse la structure réelle du site pour adapter les sélecteurs
"""

import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def analyze_auto_data_structure():
    """Analyse la structure du site Auto-Data."""
    
    # Configuration du driver
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1. Analyser la page d'accueil pour trouver les marques
        print("🔍 ANALYSE AUTO-DATA.NET")
        print("=" * 40)
        
        driver.get("https://www.auto-data.net")
        print("✅ Page d'accueil chargée")
        
        # Attendre le chargement
        time.sleep(5)
        
        # 2. Naviguer vers la page des marques
        print("\n📋 Recherche de la page des marques...")
        
        # Essayer différents liens vers les marques
        brand_urls = [
            "https://www.auto-data.net/bg/brand-list/",
            "https://www.auto-data.net/bg/mark-list/",
            "https://www.auto-data.net/bg/brands/"
        ]
        
        brand_page_found = False
        for url in brand_urls:
            try:
                print(f"   🔗 Essai: {url}")
                driver.get(url)
                time.sleep(3)
                
                # Vérifier si on a une page de marques
                if "brand" in driver.current_url.lower() or "mark" in driver.current_url.lower():
                    print(f"   ✅ Page marques trouvée: {driver.current_url}")
                    brand_page_found = True
                    break
            except Exception as e:
                print(f"   ❌ Erreur {url}: {e}")
                continue
        
        if not brand_page_found:
            # Essayer avec BMW directement
            print("\n🎯 Navigation directe vers BMW...")
            driver.get("https://www.auto-data.net/bg/brand/86/")
            time.sleep(5)
            
            if "brand" in driver.current_url:
                brand_page_found = True
                print("✅ Page BMW accessible")
        
        # 3. Analyser les sélecteurs de modèles
        if brand_page_found:
            print("\n🔧 ANALYSE DES SÉLECTEURS DE MODÈLES")
            print("-" * 45)
            
            # Sauvegarder le HTML pour analyse
            html_content = driver.page_source
            
            # Chercher les liens de modèles
            model_selectors_to_test = [
                "a[href*='/bg/car/']",
                "a[href*='car/']",
                "a[href*='/car']",
                "td a",
                "table a",
                "a[href*='/bg/']",
                ".car-link",
                ".model-link",
                ".vehicle-link"
            ]
            
            print("Test des sélecteurs de modèles:")
            
            for selector in model_selectors_to_test:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"   ✅ {selector}: {len(elements)} éléments trouvés")
                        
                        # Afficher les 3 premiers liens
                        for i, element in enumerate(elements[:3]):
                            try:
                                href = element.get_attribute("href")
                                text = element.text.strip()
                                print(f"      {i+1}. {text} -> {href}")
                            except:
                                continue
                    else:
                        print(f"   ❌ {selector}: 0 élément")
                except Exception as e:
                    print(f"   ❌ {selector}: Erreur - {e}")
            
            # 4. Tester une page de modèle spécifique
            print("\n🚗 TEST D'UNE PAGE DE MODÈLE")
            print("-" * 35)
            
            # Chercher le premier lien de modèle
            first_model_link = None
            for selector in model_selectors_to_test:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements[:1]:  # Prendre le premier
                            href = element.get_attribute("href")
                            if href and "car" in href:
                                first_model_link = href
                                break
                    if first_model_link:
                        break
                except:
                    continue
            
            if first_model_link:
                print(f"🔗 Premier modèle trouvé: {first_model_link}")
                
                # Naviguer vers la page du modèle
                driver.get(first_model_link)
                time.sleep(5)
                
                # Analyser les spécifications
                print("\n📊 ANALYSE DES SPÉCIFICATIONS")
                print("-" * 35)
                
                # Sauvegarder le HTML du modèle
                model_html = driver.page_source
                model_file = Path("data/auto_data_model_page.html")
                model_file.parent.mkdir(exist_ok=True)
                
                with open(model_file, 'w', encoding='utf-8') as f:
                    f.write(model_html)
                print(f"💾 HTML sauvegardé: {model_file}")
                
                # Tester les sélecteurs de spécifications
                spec_selectors_to_test = [
                    # Tables
                    "table tr td:nth-child(1)",
                    "table tr td:nth-child(2)", 
                    "table td",
                    "table tr td:first-child",
                    
                    # Sections
                    "h2",
                    "h3", 
                    ".spec-name",
                    ".spec-value",
                    ".tech-spec",
                    
                    # Patterns génériques
                    "td:contains('Puissance')",
                    "td:contains('Power')",
                    "td:contains('Vitesse')",
                    "td:contains('Speed')",
                ]
                
                print("Test des sélecteurs de spécifications:")
                
                for selector in spec_selectors_to_test:
                    try:
                        if ":contains(" in selector:
                            # XPath pour contains
                            xpath = f"//td[contains(text(), '{selector.split('(')[1].split(')')[0]}')]"
                            elements = driver.find_elements(By.XPATH, xpath)
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if elements:
                            print(f"   ✅ {selector}: {len(elements)} éléments")
                            
                            # Afficher le texte des premiers éléments
                            for i, element in enumerate(elements[:5]):
                                try:
                                    text = element.text.strip()
                                    if text:
                                        print(f"      {i+1}. {text[:100]}...")
                                except:
                                    continue
                        else:
                            print(f"   ❌ {selector}: 0 élément")
                    except Exception as e:
                        print(f"   ❌ {selector}: Erreur - {e}")
            else:
                print("❌ Aucun modèle trouvé pour test")
        
        # 5. Sauvegarder l'analyse
        analysis_file = Path("data/auto_data_structure_analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump({
                'url_brand': driver.current_url if brand_page_found else None,
                'model_link_found': first_model_link if 'first_model_link' in locals() else None,
                'page_analysis': {
                    'brand_page': brand_page_found,
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Analyse sauvegardée: {analysis_file}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    finally:
        driver.quit()
        print("\n🔒 Driver fermé")

if __name__ == "__main__":
    analyze_auto_data_structure()