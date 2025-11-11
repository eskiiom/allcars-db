#!/usr/bin/env python3
"""
Auto-Data.net Scraper - Version Intégrée
Scraper pour auto-data.net intégré au système de consolidation
Utilise les patterns découverts : /bg/{brand-name}-brand-{brand-id}
Génère des fichiers avec préfixe as24_ pour identifier la source

Usage:
    python autodata_scraper.py                    # Scrape toutes les marques
    python autodata_scraper.py --test            # Test sur 5 marques
    python autodata_scraper.py --headless=False  # Voir le navigateur
    python autodata_scraper.py --max-brands 15   # Limiter à 15 marques
"""

import argparse
import json
import time
import random
import logging
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration logging avec emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('autodata_scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AutoDataScraper:
    """Scraper Auto-Data.net intégré au système de consolidation."""
    
    def __init__(self, headless=True):
        self.base_url = "https://www.auto-data.net"
        self.language = "/bg"  # Bulgarian version (plus complète)
        self.full_base_url = f"{self.base_url}{self.language}"
        self.brand_models_data = {}
        self.setup_driver(headless)
        self.brand_mapping = self.get_brand_mapping()
        
    def setup_driver(self, headless=True):
        """Configure le driver Selenium avec des options optimisées."""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            logger.info("✅ Auto-Data driver configuré")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration driver: {e}")
            raise
    
    def get_brand_mapping(self):
        """Mapping des marques avec leurs IDs basé sur l'exploration."""
        return {
            # Marques confirmées avec extraction réussie
            "acura": {"name": "Acura", "id": "6"},
            "alfa-romeo": {"name": "Alfa Romeo", "id": "11"},
            "audi": {"name": "Audi", "id": "41"},
            "bmw": {"name": "BMW", "id": "86"},
            "ferrari": {"name": "Ferrari", "id": "62"},
            "honda": {"name": "Honda", "id": "127"},
            "hyundai": {"name": "Hyundai", "id": "147"},
            "mercedes": {"name": "Mercedes", "id": "41"},
            "porsche": {"name": "Porsche", "id": "307"},
            "lamborghini": {"name": "Lamborghini", "id": "187"},
            "bentley": {"name": "Bentley", "id": "66"},
            "maserati": {"name": "Maserati", "id": "237"},
            "bugatti": {"name": "Bugatti", "id": "106"},
            "aston-martin": {"name": "Aston Martin", "id": "36"},
            "volkswagen": {"name": "Volkswagen", "id": "417"},
            "toyota": {"name": "Toyota", "id": "407"},
            "nissan": {"name": "Nissan", "id": "277"},
            "mazda": {"name": "Mazda", "id": "247"},
            "subaru": {"name": "Subaru", "id": "377"},
            "mitsubishi": {"name": "Mitsubishi", "id": "267"}
        }
    
    def extract_model_links_from_brand_page(self, brand_slug, brand_name):
        """Extrait les liens vers les modèles d'une page de marque."""
        try:
            brand_url = f"{self.full_base_url}/{brand_slug}-brand-{self.brand_mapping[brand_slug]['id']}"
            logger.info(f"🌐 Extracting models from: {brand_url}")
            
            self.driver.get(brand_url)
            
            # Attendre que la page se charge
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            
            models = []
            
            # Pattern principal: Liens avec "model" dans l'URL
            model_link_selectors = [
                "a[href*='model']",
                "[class*='model'] a",
                ".model-list a"
            ]
            
            for selector in model_link_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.debug(f"🔍 Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            try:
                                href = element.get_attribute("href")
                                text = element.text.strip()
                                
                                # Vérifier si c'est un vrai lien de modèle
                                if href and "model" in href and text:
                                    # Extraire le nom du modèle (nettoyer le texte)
                                    model_name = text.replace('\n', ' ').strip()
                                    
                                    # Ignorer les liens qui ne sont pas des modèles
                                    if len(model_name) > 2 and model_name not in ['More', 'Read More', 'See All', 'All']:
                                        models.append({
                                            'name': model_name,
                                            'url': href,
                                            'selector': selector
                                        })
                            except Exception:
                                continue
                        
                        if models:  # Si on a trouvé des modèles, on s'arrête
                            break
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            logger.info(f"✅ {brand_name}: {len(models)} modèles trouvés")
            return models
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction modèles pour {brand_name}: {e}")
            return []
    
    def scrape_brand_models(self, brand_slug, brand_name):
        """Scrape les modèles d'une marque spécifique."""
        try:
            logger.info(f"🏷️ Scraping modèles pour: {brand_name}")
            
            # Extraire les modèles depuis la page de la marque
            models_data = self.extract_model_links_from_brand_page(brand_slug, brand_name)
            
            if models_data:
                # Nettoyer les noms de modèles
                model_names = []
                for model in models_data:
                    name = model['name']
                    # Nettoyer les noms (enlever les années, puissances, etc.)
                    cleaned_name = re.sub(r'\d{4}\s*-\s*\d{4}', '', name)  # Enlever années
                    cleaned_name = re.sub(r'\d{4}\s*-', '', cleaned_name)  # Enlever année début
                    cleaned_name = re.sub(r'\d+ ch', '', cleaned_name)     # Enlever puissance
                    cleaned_name = cleaned_name.strip()
                    
                    if cleaned_name and len(cleaned_name) > 1 and len(cleaned_name) < 30:
                        model_names.append(cleaned_name)
                
                # Enlever les doublons et trier
                unique_models = sorted(list(set(model_names)))
                
                logger.info(f"✅ {brand_name}: {len(unique_models)} modèles uniques après nettoyage")
                return unique_models
            else:
                logger.warning(f"⚠️ {brand_name}: Aucun modèle trouvé")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur scraping {brand_name}: {e}")
            return []
    
    def save_results(self, output_file=None):
        """Sauvegarde les résultats avec le préfixe as24_."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"data/as24_autodata_scraped_models_{timestamp}.json"
            
            result_data = {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "scraper_version": "autodata_scraper_v1.0",
                    "source": "Auto-Data.net",
                    "method": "link_extraction_from_brand_pages",
                    "url_pattern": "/bg/{brand-name}-brand-{brand-id}",
                    "total_brands": len(self.brand_models_data),
                    "total_models": sum(len(models) for models in self.brand_models_data.values()),
                    "brands_with_models": len([b for b, models in self.brand_models_data.items() if models]),
                    "brands_without_models": len([b for b, models in self.brand_models_data.items() if not models]),
                    "file_prefix": "as24_",
                    "integration_ready": True
                },
                "brands_models": self.brand_models_data
            }
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Résultats Auto-Data sauvegardés: {output_file}")
            
            # Résumé
            total_models = result_data["metadata"]["total_models"]
            brands_with_models = result_data["metadata"]["brands_with_models"]
            
            logger.info("📊 RÉSUMÉ AUTO-DATA:")
            logger.info(f"   • Marques traitées: {len(self.brand_models_data)}")
            logger.info(f"   • Marques avec modèles: {brands_with_models}")
            logger.info(f"   • Total modèles: {total_models}")
            logger.info(f"   • Fichier as24_: {Path(output_file).name}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde Auto-Data: {e}")
            return None
    
    def scrape_all_brands(self, max_brands=None):
        """Scrape toutes les marques."""
        try:
            brands_to_process = list(self.brand_mapping.items())[:max_brands] if max_brands else list(self.brand_mapping.items())
            logger.info(f"🚀 Début du scraping Auto-Data pour {len(brands_to_process)} marques")
            
            for i, (brand_slug, brand_info) in enumerate(brands_to_process, 1):
                brand_name = brand_info["name"]
                
                logger.info(f"🏷️ [{i}/{len(brands_to_process)}] {brand_name}")
                
                try:
                    models = self.scrape_brand_models(brand_slug, brand_name)
                    self.brand_models_data[brand_name] = models
                    
                    if models:
                        logger.info(f"   ✅ {len(models)} modèles")
                    else:
                        logger.warning(f"   ⚠️ Aucun modèle")
                    
                except Exception as e:
                    logger.error(f"   ❌ Erreur: {e}")
                    self.brand_models_data[brand_name] = []
                
                # Pause entre les marques
                time.sleep(random.uniform(2, 4))
                
                # Afficher le progrès
                if i % 5 == 0:
                    brands_with_models = len([b for b, models in self.brand_models_data.items() if models])
                    logger.info(f"📊 Progrès: {i}/{len(brands_to_process)} marques, {brands_with_models} avec modèles")
            
            logger.info(f"🎉 Scraping Auto-Data terminé! {len(self.brand_models_data)} marques traitées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping: {e}")
            return False
    
    def close(self):
        """Ferme le driver proprement."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("🔒 Auto-Data driver fermé")

def main():
    """Fonction principale avec gestion d'arguments."""
    parser = argparse.ArgumentParser(
        description="Auto-Data.net Scraper - Version Intégrée (préfixe as24_)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python autodata_scraper.py                 # Toutes les marques
  python autodata_scraper.py --test          # Test rapide (5 marques)
  python autodata_scraper.py --max-brands 10 # 10 marques maximum
  python autodata_scraper.py --headless=False # Voir le navigateur

Ce scraper génère des fichiers avec préfixe as24_ pour identification dans le système.
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Mode test (5 marques seulement)')
    parser.add_argument('--max-brands', type=int, metavar='N',
                       help='Limiter le nombre de marques à scraper')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Mode headless (défaut: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                       help='Afficher le navigateur')
    
    args = parser.parse_args()
    
    # Déterminer les paramètres
    max_brands = 5 if args.test else args.max_brands
    
    logger.info("🚀 Auto-Data.net Scraper - Version Intégrée")
    logger.info(f"   • Mode: {'Test' if args.test else 'Complet'}")
    logger.info(f"   • Headless: {args.headless}")
    logger.info(f"   • Marques max: {max_brands or 'Toutes'}")
    logger.info(f"   • Source: Auto-Data.net (intégrée)")
    logger.info(f"   • Pattern: /bg/{{brand-name}}-brand-{{brand-id}}")
    logger.info(f"   • Préfixe fichiers: as24_")
    
    try:
        scraper = AutoDataScraper(headless=args.headless)
        
        # Lancer le scraping
        success = scraper.scrape_all_brands(max_brands=max_brands)
        
        if success:
            output_file = scraper.save_results()
            if output_file:
                logger.info(f"🎉 SUCCESS! Fichier généré: {output_file}")
            else:
                logger.error("❌ Erreur lors de la sauvegarde")
        else:
            logger.error("❌ Échec du scraping")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Interruption par l'utilisateur")
        if 'scraper' in locals():
            scraper.save_results()
    except Exception as e:
        logger.error(f"💥 Erreur générale: {e}")
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main()