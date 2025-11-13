#!/usr/bin/env python3
"""
Carfolio.com Scraper - Version Intégrée
Scraper pour carfolio.com intégré au système de consolidation
Utilise les données d'exploration pour scraper marques et modèles
Génère des fichiers avec préfixe carfolio_ pour identifier la source

Usage:
    python carfolio_scraper.py                    # Scrape toutes les marques
    python carfolio_scraper.py --test            # Test sur 5 marques
    python carfolio_scraper.py --headless=False  # Voir le navigateur
    python carfolio_scraper.py --max-brands 15   # Limiter à 15 marques
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
        logging.FileHandler('logs/carfolio_scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class CarfolioScraper:
    """Scraper Carfolio.com intégré au système de consolidation."""

    def __init__(self, headless=True):
        self.base_url = "https://www.carfolio.com"
        self.brand_models_data = {}
        self.duplicate_log = []
        self.setup_driver(headless)
        self.load_exploration_data()

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
            logger.info("✅ Carfolio driver configuré")

        except Exception as e:
            logger.error(f"❌ Erreur configuration driver: {e}")
            raise

    def load_exploration_data(self):
        """Charge les données d'exploration Carfolio."""
        try:
            exploration_file = Path("data/carfolio_exploration_20251113_224759.json")
            if exploration_file.exists():
                with open(exploration_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.exploration_data = data
                    self.brands_to_scrape = data.get("brands_discovered", [])
                logger.info(f"📋 Chargé {len(self.brands_to_scrape)} marques depuis l'exploration Carfolio")
                return True
            else:
                logger.error("❌ Fichier d'exploration Carfolio non trouvé")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur chargement données exploration: {e}")
            return False

    def extract_all_models_from_specifications_page(self):
        """Extrait tous les modèles depuis la page de spécifications Carfolio."""
        try:
            specs_url = "https://www.carfolio.com/specifications/"
            logger.info(f"🌐 Extraction de tous les modèles depuis: {specs_url}")

            self.driver.get(specs_url)

            # Attendre que la page se charge
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            time.sleep(5)  # La page est lourde, attendre plus longtemps

            # Collecter tous les liens de modèles sur la page
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "a")

            models_by_brand = {}
            total_links_processed = 0

            logger.info(f"🔍 Analyse de {len(all_links)} liens sur la page...")

            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()

                    total_links_processed += 1

                    # Afficher progrès tous les 500 liens
                    if total_links_processed % 500 == 0:
                        logger.info(f"📊 Progrès: {total_links_processed}/{len(all_links)} liens analysés, {len(models_by_brand)} marques trouvées")

                    # Critères pour identifier un lien de modèle Carfolio
                    if (href and text and
                        'carfolio.com' in href and
                        len(text) > 2 and len(text) < 50 and
                        not text.isdigit() and
                        not text.startswith(('http', 'www')) and
                        not any(char in text for char in ['<', '>', '{', '}'])):

                        # Ignorer les termes de navigation
                        navigation_terms = [
                            'Home', 'About', 'Contact', 'Search', 'Privacy', 'Terms',
                            'All Specs', 'Latest', 'Articles', 'Abbreviations', 'Guide', 'Help',
                            'World\'s fastest cars', 'LOGIN', 'STABLE', 'Legal', 'Tools',
                            'Car specs', 'Specifications', 'A-Z', 'Privacy Policy', 'Terms of Use'
                        ]

                        if text not in navigation_terms and not text.lower().startswith(('car spec', 'specifications')):
                            # Extraire le nom de la marque depuis l'URL
                            # Pattern: https://www.carfolio.com/{brand-slug}/{brand-id}/
                            url_match = re.search(r'carfolio\.com/([^/]+)/(\d+)/', href)
                            if url_match:
                                brand_slug = url_match.group(1)
                                brand_id = url_match.group(2)

                                # Nettoyer le nom de la marque (enlever suffixes comme " car specs")
                                brand_name = text.replace(' car specs', '').replace(' car spec', '').strip()

                                # Si le texte contient "car specs", c'est probablement le nom de la marque
                                if ' car spec' in text.lower():
                                    # Le nom avant "car spec" est le nom de la marque
                                    brand_name = text.split(' car spec')[0].strip()
                                else:
                                    # Sinon, essayer d'extraire depuis le slug
                                    brand_name = brand_slug.replace('-', ' ').title()

                                # Initialiser la liste des modèles pour cette marque
                                if brand_name not in models_by_brand:
                                    models_by_brand[brand_name] = []

                                # Ajouter le modèle (le texte du lien est le nom du modèle)
                                model_name = text.strip()
                                if model_name not in models_by_brand[brand_name]:
                                    models_by_brand[brand_name].append(model_name)

                except Exception:
                    continue

            logger.info(f"✅ Extraction terminée: {len(models_by_brand)} marques trouvées avec modèles")
            return models_by_brand

        except Exception as e:
            logger.error(f"❌ Erreur extraction modèles depuis page spécifications: {e}")
            return {}

    def scrape_all_models(self):
        """Scrape tous les modèles depuis la page de spécifications."""
        try:
            logger.info("🏷️ Scraping de tous les modèles Carfolio depuis la page de spécifications")

            # Extraire tous les modèles depuis la page de spécifications
            models_by_brand = self.extract_all_models_from_specifications_page()

            if models_by_brand:
                # Traiter chaque marque
                processed_brands = {}
                total_duplicates = 0

                for brand_name, models in models_by_brand.items():
                    # Nettoyer et dédupliquer les noms de modèles
                    cleaned_models = []
                    for model in models:
                        # Nettoyer les noms (enlever les suffixes, années, etc.)
                        cleaned_name = re.sub(r' car specs?', '', model, flags=re.IGNORECASE)
                        cleaned_name = re.sub(r'\(\d{4}\)', '', cleaned_name)
                        cleaned_name = re.sub(r'\d{4}', '', cleaned_name)
                        cleaned_name = cleaned_name.strip()

                        if cleaned_name and len(cleaned_name) > 1 and len(cleaned_name) < 50:
                            cleaned_models.append(cleaned_name)

                    # Enlever les doublons et trier
                    unique_models = sorted(list(set(cleaned_models)))

                    # Détection de doublons avec autres sources
                    duplicates = self.check_for_duplicates(brand_name, unique_models)

                    processed_brands[brand_name] = (unique_models, duplicates)
                    total_duplicates += len(duplicates)

                    logger.info(f"✅ {brand_name}: {len(unique_models)} modèles uniques")
                    if duplicates:
                        logger.warning(f"⚠️ {brand_name}: {len(duplicates)} doublons détectés")

                logger.info(f"🎉 Scraping terminé: {len(processed_brands)} marques avec {sum(len(models) for models, _ in processed_brands.values())} modèles totaux")
                logger.info(f"🔍 Total doublons détectés: {total_duplicates}")

                return processed_brands
            else:
                logger.warning("⚠️ Aucun modèle trouvé")
                return {}

        except Exception as e:
            logger.error(f"❌ Erreur scraping tous les modèles: {e}")
            return {}

    def check_for_duplicates(self, brand_name, models):
        """Vérifie les doublons avec les autres sources de données."""
        duplicates = []

        try:
            # Charger les données de consolidation existantes
            consolidation_files = [
                "data/as24_brands_models.json",
                "data/cgurus_brands_models.json",
                "data/autodata_brands_models.json"
            ]

            for file_path in consolidation_files:
                try:
                    if Path(file_path).exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            existing_brands = data.get("brands_models", {})

                            if brand_name in existing_brands:
                                existing_models = set(existing_brands[brand_name])
                                current_models = set(models)

                                # Trouver les modèles en commun
                                common_models = existing_models.intersection(current_models)
                                if common_models:
                                    source_name = file_path.split('/')[-1].replace('_brands_models.json', '').replace('data/', '')
                                    duplicates.extend([{
                                        'model': model,
                                        'existing_source': source_name,
                                        'new_source': 'carfolio'
                                    } for model in common_models])

                except Exception as e:
                    logger.debug(f"Erreur vérification doublons {file_path}: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Erreur générale vérification doublons: {e}")

        return duplicates

    def save_results(self, output_file=None):
        """Sauvegarde les résultats avec le préfixe carfolio_."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"data/carfolio_scraped_models_{timestamp}.json"

            result_data = {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "scraper_version": "carfolio_scraper_v1.0",
                    "source": "Carfolio.com",
                    "method": "link_extraction_from_brand_pages",
                    "url_pattern": "/{brand-slug}/{brand-id}/",
                    "model_selector": "a[href*='/specifications/']",
                    "total_brands": len(self.brand_models_data),
                    "total_models": sum(len(models) for models, _ in self.brand_models_data.values()),
                    "brands_with_models": len([b for b, (models, _) in self.brand_models_data.items() if models]),
                    "brands_without_models": len([b for b, (models, _) in self.brand_models_data.items() if not models]),
                    "total_duplicates_detected": len(self.duplicate_log),
                    "file_prefix": "carfolio_",
                    "integration_ready": True
                },
                "brands_models": {brand: models for brand, (models, _) in self.brand_models_data.items()},
                "duplicates_log": self.duplicate_log
            }

            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Résultats Carfolio sauvegardés: {output_file}")

            # Résumé
            total_models = result_data["metadata"]["total_models"]
            brands_with_models = result_data["metadata"]["brands_with_models"]
            total_duplicates = result_data["metadata"]["total_duplicates_detected"]

            logger.info("📊 RÉSUMÉ CARFOLIO:")
            logger.info(f"   • Marques traitées: {len(self.brand_models_data)}")
            logger.info(f"   • Marques avec modèles: {brands_with_models}")
            logger.info(f"   • Total modèles: {total_models}")

            return output_file

        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde Carfolio: {e}")
            return None

    def scrape_all_brands(self, max_brands=None):
        """Scrape toutes les marques en une seule opération depuis la page de spécifications."""
        try:
            logger.info("🚀 Début du scraping Carfolio - extraction de tous les modèles")

            # Scraper tous les modèles en une seule opération
            all_brand_data = self.scrape_all_models()

            if all_brand_data:
                # Limiter le nombre de marques si demandé
                if max_brands:
                    limited_data = {}
                    for i, (brand_name, (models, duplicates)) in enumerate(all_brand_data.items()):
                        if i >= max_brands:
                            break
                        limited_data[brand_name] = (models, duplicates)
                    all_brand_data = limited_data

                self.brand_models_data = all_brand_data

                # Construire le log des doublons
                self.duplicate_log = []
                for brand_name, (models, duplicates) in self.brand_models_data.items():
                    self.duplicate_log.extend([{
                        'brand': brand_name,
                        **dup
                    } for dup in duplicates])

                brands_with_models = len([b for b, (models, _) in self.brand_models_data.items() if models])
                total_models = sum(len(models) for models, _ in self.brand_models_data.values())
                total_duplicates = len(self.duplicate_log)

                logger.info(f"🎉 Scraping Carfolio terminé!")
                logger.info(f"   • Marques traitées: {len(self.brand_models_data)}")
                logger.info(f"   • Marques avec modèles: {brands_with_models}")
                logger.info(f"   • Total modèles: {total_models}")
                logger.info(f"   • Doublons détectés: {total_duplicates}")

                return True
            else:
                logger.error("❌ Échec de l'extraction des modèles")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping: {e}")
            return False

    def close(self):
        """Ferme le driver proprement."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("🔒 Carfolio driver fermé")

def main():
    """Fonction principale avec gestion d'arguments."""
    parser = argparse.ArgumentParser(
        description="Carfolio.com Scraper - Version Intégrée (préfixe carfolio_)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python carfolio_scraper.py                 # Toutes les marques
  python carfolio_scraper.py --test          # Test rapide (5 marques)
  python carfolio_scraper.py --max-brands 10 # 10 marques maximum
  python carfolio_scraper.py --headless=False # Voir le navigateur

Ce scraper génère des fichiers avec préfixe carfolio_ pour identification dans le système.
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

    logger.info("🚀 Carfolio.com Scraper - Version Intégrée")
    logger.info(f"   • Mode: {'Test' if args.test else 'Complet'}")
    logger.info(f"   • Headless: {args.headless}")
    logger.info(f"   • Marques max: {max_brands or 'Toutes'}")
    logger.info(f"   • Source: Carfolio.com (intégrée)")
    logger.info(f"   • Pattern: /{{brand-slug}}/{{brand-id}}/")
    logger.info(f"   • Sélecteur modèles: a[href*='/specifications/']")
    logger.info(f"   • Préfixe fichiers: carfolio_")

    try:
        scraper = CarfolioScraper(headless=args.headless)

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