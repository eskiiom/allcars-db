#!/usr/bin/env python3
"""
Auto-Data Technical Specifications Scraper v1.0
Récupère les spécifications techniques détaillées des véhicules depuis Auto-Data.net
Base de données pour site de suivi de dépenses véhicule

Data Schema:
- Basic specs: Années, moteur, boîte, carburant
- Performance: Puissance, couple, 0-100km/h, vitesse max, consommation  
- Dimensions: Longueur, largeur, hauteur, poids, volume coffre
- Equipment: Fonctionnalités et options disponibles

Usage:
    python autodata_technical_scraper.py
    python autodata_technical_scraper.py --brand "BMW"
    python autodata_technical_scraper.py --popular-brands
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
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# Optional import for CSV export
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('autodata_technical_scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AutoDataTechnicalScraper:
    """Scraper Auto-Data pour spécifications techniques détaillées."""
    
    def __init__(self, headless=True):
        self.base_url = "https://www.auto-data.net"
        self.technical_data = {}
        self.setup_driver(headless)
        self.load_brand_mapping()
    
    def setup_driver(self, headless=True):
        """Configure le driver Selenium."""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            logger.info("✅ Driver Selenium configuré pour spécifications techniques")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration driver: {e}")
            raise
    
    def load_brand_mapping(self):
        """Charge le mapping marques Auto-Data."""
        try:
            brands_file = Path("data/autodata_brands_for_scraping.json")
            if brands_file.exists():
                with open(brands_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.brands_list = data["brands"]
                logger.info(f"📋 Chargé {len(self.brands_list)} marques depuis Auto-Data")
                
                # Marques populaires à prioriser
                self.popular_brands = [
                    "Toyota", "BMW", "Audi", "Volkswagen", "Ford", 
                    "Mercedes-Benz", "Honda", "Nissan", "Hyundai", "Kia",
                    "Peugeot", "Renault", "Skoda", "SEAT", "Citroen"
                ]
                
            else:
                logger.error("❌ Fichier autodata_brands_for_scraping.json non trouvé")
                self.brands_list = []
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement marques: {e}")
            self.brands_list = []
    
    def get_brand_technical_url(self, brand_name):
        """Construit l'URL technique pour une marque."""
        # Nettoyer le nom de marque pour l'URL
        brand_slug = self.make_url_slug(brand_name)
        return f"{self.base_url}/bg/brand/{brand_slug}/"
    
    def make_url_slug(self, text):
        """Convertit un texte en slug URL."""
        # Transliteration pour les caractères spéciaux
        transliteration_map = {
            ' ': '-',
            'Š': 'S', 'š': 's', 'Č': 'C', 'č': 'c', 'Ć': 'C', 'ć': 'c',
            'Đ': 'DJ', 'đ': 'dj', 'Ž': 'Z', 'ž': 'z'
        }
        
        text = text.lower()
        for old, new in transliteration_map.items():
            text = text.replace(old, new)
        
        # Supprimer caractères non alphanumériques sauf tirets
        text = re.sub(r'[^a-z0-9-]', '', text)
        return text
    
    def navigate_to_brand_models(self, brand_name, brand_id):
        """Navigue vers la liste des modèles d'une marque."""
        try:
            logger.info(f"🔍 Navigation vers {brand_name}")
            
            # URL directe si on a l'ID de marque
            if brand_id:
                url = f"{self.base_url}/bg/brand-{brand_id}/"
            else:
                url = self.get_brand_technical_url(brand_name)
            
            self.driver.get(url)
            
            # Attendre le chargement
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur navigation {brand_name}: {e}")
            return False
    
    def get_model_links_from_page(self, brand_name):
        """Récupère tous les liens de modèles sur la page."""
        model_links = []
        
        try:
            # Sélecteurs pour les liens de modèles
            model_selectors = [
                "a[href*='/bg/car/']",
                ".model-list a",
                "table a[href*='car']",
                "td a[href*='car']"
            ]
            
            for selector in model_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute("href")
                        text = element.text.strip()
                        
                        if href and text and len(text) > 2:
                            model_links.append({
                                'name': text,
                                'url': href,
                                'brand': brand_name
                            })
                    
                    if model_links:
                        logger.info(f"   📄 Trouvé {len(model_links)} liens modèles avec {selector}")
                        break
                        
                except Exception:
                    continue
            
            # Dédoublonner par nom de modèle
            unique_models = {}
            for link in model_links:
                if link['name'] not in unique_models:
                    unique_models[link['name']] = link
            
            return list(unique_models.values())
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération liens modèles: {e}")
            return []
    
    def extract_model_generations(self, model_element):
        """Extrait les générations de modèles."""
        generations = []
        
        try:
            # Chercher les générations dans le texte de l'élément
            text = model_element.text
            
            # Patterns pour les années et générations
            generation_patterns = [
                r'(\d{4})\s*-\s*(\d{4})',  # 2005-2015
                r'since\s+(\d{4})',        # since 2010
                r'(\d{4})\+',               # 2005+
                r'([IVX]+)\.?',             # I, II, III, IV, V
            ]
            
            for pattern in generation_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        generations.append(' - '.join(match))
                    else:
                        generations.append(match)
            
            return generations
            
        except Exception:
            return []
    
    def scrape_model_specifications(self, model_link):
        """Scrape les spécifications détaillées d'un modèle."""
        try:
            logger.info(f"   🚗 Scraping: {model_link['name']}")
            
            # Naviguer vers la page du modèle
            self.driver.get(model_link['url'])
            time.sleep(2)
            
            # Extraire les spécifications techniques
            specs = {
                'brand': model_link['brand'],
                'model': model_link['name'],
                'url': model_link['url'],
                'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                'specifications': {}
            }
            
            # Spécifications de base
            specs['specifications']['basic'] = self.extract_basic_specs()
            
            # Performance
            specs['specifications']['performance'] = self.extract_performance_specs()
            
            # Dimensions
            specs['specifications']['dimensions'] = self.extract_dimension_specs()
            
            # Moteur
            specs['specifications']['engine'] = self.extract_engine_specs()
            
            # Transmission
            specs['specifications']['transmission'] = self.extract_transmission_specs()
            
            # Équipements (si disponibles)
            specs['specifications']['equipment'] = self.extract_equipment_specs()
            
            # Vérifier si on a des données
            has_data = any(specs['specifications'].values())
            
            if has_data:
                logger.info(f"   ✅ Spécifications extraites pour {model_link['name']}")
                return specs
            else:
                logger.warning(f"   ⚠️ Aucune spécification trouvée pour {model_link['name']}")
                return None
                
        except Exception as e:
            logger.error(f"   ❌ Erreur scraping {model_link['name']}: {e}")
            return None
    
    def extract_basic_specs(self):
        """Extrait les spécifications de base."""
        basic = {}
        
        # Sélecteurs pour les specs de base
        basic_selectors = {
            'years': ['Années de production', 'Production years', 'Annee de fabricatie'],
            'fuel_type': ['Carburant', 'Fuel type', 'Combustibil'],
            'doors': ['Nombre de portes', 'Number of doors', 'Numar usi'],
            'seats': ['Nombre de places', 'Number of seats', 'Locuri scaune'],
        }
        
        try:
            for spec_name, selectors in basic_selectors.items():
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{selector}')]/following-sibling::td")
                        value = element.text.strip()
                        if value and value != 'N/A':
                            basic[spec_name] = value
                            break
                    except:
                        continue
            
            return basic
            
        except Exception as e:
            logger.debug(f"Erreur extraction specs de base: {e}")
            return basic
    
    def extract_performance_specs(self):
        """Extrait les spécifications de performance."""
        performance = {}
        
        # Sélecteurs pour performance
        perf_selectors = {
            'power_kw': ['Puissance (kW)', 'Power (kW)', 'Putere (kW)'],
            'power_hp': ['Puissance (ch)', 'Power (hp)', 'Putere (cp)'],
            'torque': ['Couple (Nm)', 'Torque (Nm)', 'Cuplu (Nm)'],
            'acceleration_0_100': ['0-100 km/h (s)', '0-100 km/h (s)', '0-100 km/h (s)'],
            'max_speed': ['Vitesse max (km/h)', 'Max speed (km/h)', 'Viteza maxima (km/h)'],
            'fuel_consumption': ['Consommation mixte (l/100km)', 'Mixed fuel consumption', 'Consum mixt (l/100km)'],
        }
        
        try:
            for spec_name, selectors in perf_selectors.items():
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{selector}')]/following-sibling::td")
                        value = element.text.strip()
                        if value and value != 'N/A':
                            performance[spec_name] = value
                            break
                    except:
                        continue
            
            return performance
            
        except Exception as e:
            logger.debug(f"Erreur extraction performance: {e}")
            return performance
    
    def extract_dimension_specs(self):
        """Extrait les spécifications dimensionnelles."""
        dimensions = {}
        
        # Sélecteurs pour dimensions
        dim_selectors = {
            'length': ['Longueur (mm)', 'Length (mm)', 'Lungime (mm)'],
            'width': ['Largeur (mm)', 'Width (mm)', 'Latime (mm)'],
            'height': ['Hauteur (mm)', 'Height (mm)', 'Inaltime (mm)'],
            'weight': ['Masse (kg)', 'Weight (kg)', 'Masa (kg)'],
            'boot_volume': ['Volume du coffre (l)', 'Boot volume (l)', 'Volum portbagaj (l)'],
            'fuel_tank': ['Capacité carburant (l)', 'Fuel tank capacity (l)', 'Capacitate rezervor (l)'],
        }
        
        try:
            for spec_name, selectors in dim_selectors.items():
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{selector}')]/following-sibling::td")
                        value = element.text.strip()
                        if value and value != 'N/A':
                            dimensions[spec_name] = value
                            break
                    except:
                        continue
            
            return dimensions
            
        except Exception as e:
            logger.debug(f"Erreur extraction dimensions: {e}")
            return dimensions
    
    def extract_engine_specs(self):
        """Extrait les spécifications moteur."""
        engine = {}
        
        # Sélecteurs pour moteur
        engine_selectors = {
            'displacement': ['Cylindrée (cm³)', 'Displacement (cm³)', 'Cilindree (cm³)'],
            'engine_type': ['Type de moteur', 'Engine type', 'Tip motor'],
            'cylinders': ['Nombre de cylindres', 'Number of cylinders', 'Numar cilindri'],
            'valves': ['Nombre de soupapes', 'Number of valves', 'Numar supape'],
            'compression_ratio': ['Taux de compression', 'Compression ratio', 'Raport compresie'],
        }
        
        try:
            for spec_name, selectors in engine_selectors.items():
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{selector}')]/following-sibling::td")
                        value = element.text.strip()
                        if value and value != 'N/A':
                            engine[spec_name] = value
                            break
                    except:
                        continue
            
            return engine
            
        except Exception as e:
            logger.debug(f"Erreur extraction moteur: {e}")
            return engine
    
    def extract_transmission_specs(self):
        """Extrait les spécifications de transmission."""
        transmission = {}
        
        # Sélecteurs pour transmission
        trans_selectors = {
            'gearbox': ['Boîte de vitesses', 'Gearbox', 'Cutie de viteze'],
            'drive': ['Traction', 'Drive', 'Tractiune'],
            'gears': ['Nombre de vitesses', 'Number of gears', 'Numar viteze'],
        }
        
        try:
            for spec_name, selectors in trans_selectors.items():
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{selector}')]/following-sibling::td")
                        value = element.text.strip()
                        if value and value != 'N/A':
                            transmission[spec_name] = value
                            break
                    except:
                        continue
            
            return transmission
            
        except Exception as e:
            logger.debug(f"Erreur extraction transmission: {e}")
            return transmission
    
    def extract_equipment_specs(self):
        """Extrait les équipements optionnels."""
        equipment = []
        
        try:
            # Chercher dans une section équipements
            equipment_selectors = [
                "h3:contains('Équipements')",
                "h3:contains('Equipment')", 
                "h3:contains('Echipamente')"
            ]
            
            for selector in equipment_selectors:
                try:
                    section = self.driver.find_element(By.CSS_SELECTOR, selector)
                    equipment_items = section.find_elements(By.XPATH, "./following-sibling::ul//li")
                    
                    for item in equipment_items:
                        equipment_name = item.text.strip()
                        if equipment_name and len(equipment_name) > 2:
                            equipment.append(equipment_name)
                    
                    if equipment:
                        break
                        
                except:
                    continue
            
            return equipment
            
        except Exception as e:
            logger.debug(f"Erreur extraction équipements: {e}")
            return equipment
    
    def scrape_brand_technical_data(self, brand_name, brand_id, limit_models=None):
        """Scrape toutes les données techniques d'une marque."""
        try:
            if not self.navigate_to_brand_models(brand_name, brand_id):
                return {}
            
            # Récupérer les liens de modèles
            model_links = self.get_model_links_from_page(brand_name)
            
            if not model_links:
                logger.warning(f"⚠️ Aucun modèle trouvé pour {brand_name}")
                return {}
            
            # Limiter le nombre de modèles si demandé
            if limit_models:
                model_links = model_links[:limit_models]
                logger.info(f"   🔢 Limitation à {limit_models} modèles")
            
            brand_data = {
                'brand': brand_name,
                'total_models': len(model_links),
                'scraped_models': 0,
                'models': {},
                'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
            logger.info(f"🔄 Début scraping technique pour {brand_name} ({len(model_links)} modèles)")
            
            for i, model_link in enumerate(model_links, 1):
                try:
                    logger.info(f"   [{i}/{len(model_links)}] {model_link['name']}")
                    
                    model_specs = self.scrape_model_specifications(model_link)
                    
                    if model_specs:
                        brand_data['models'][model_link['name']] = model_specs
                        brand_data['scraped_models'] += 1
                        
                        # Afficher résumé des specs trouvées
                        specs_count = sum(1 for cat in model_specs['specifications'].values() if cat)
                        logger.info(f"      ✅ {specs_count} catégories de specs extraites")
                    else:
                        logger.warning(f"      ⚠️ Échec extraction specs")
                    
                    # Pause entre les modèles (2-3 secondes)
                    time.sleep(random.uniform(2, 3))
                    
                except Exception as e:
                    logger.error(f"      ❌ Erreur modèle {model_link['name']}: {e}")
                    continue
            
            # Résumé de la marque
            logger.info(f"✅ {brand_name}: {brand_data['scraped_models']}/{brand_data['total_models']} modèles avec specs")
            
            return brand_data
            
        except Exception as e:
            logger.error(f"❌ Erreur scraping {brand_name}: {e}")
            return {}
    
    def scrape_popular_brands(self):
        """Scrape les marques populaires en priorité."""
        logger.info("🎯 Début scraping des marques populaires")
        
        popular_data = {}
        
        for brand in self.popular_brands:
            # Trouver la marque dans notre liste
            brand_info = None
            for b in self.brands_list:
                if b['name'].lower() == brand.lower():
                    brand_info = b
                    break
            
            if brand_info:
                brand_data = self.scrape_brand_technical_data(
                    brand_info['name'], 
                    brand_info['id'],
                    limit_models=20  # Limiter à 20 modèles par marque populaire
                )
                
                if brand_data:
                    popular_data[brand] = brand_data
                    
                    # Pause entre les marques
                    time.sleep(random.uniform(5, 8))
            else:
                logger.warning(f"⚠️ Marque {brand} non trouvée dans la liste")
        
        return popular_data
    
    def scrape_all_brands_with_progress(self, max_brands=None):
        """Scrape toutes les marques avec suivi de progression."""
        brands_to_process = self.brands_list[:max_brands] if max_brands else self.brands_list
        
        logger.info(f"🚀 Début scraping complet: {len(brands_to_process)} marques")
        
        all_technical_data = {
            'metadata': {
                'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                'scraper_version': 'v1.0_technical_specs',
                'source': 'Auto-Data.net Technical Specifications',
                'method': 'selenium_table_extraction',
                'total_brands': len(brands_to_process)
            },
            'brands_technical_data': {}
        }
        
        for i, brand_info in enumerate(brands_to_process, 1):
            brand_name = brand_info['name']
            brand_id = brand_info['id']
            
            logger.info(f"🏷️ [{i}/{len(brands_to_process)}] {brand_name}")
            
            try:
                brand_data = self.scrape_brand_technical_data(brand_name, brand_id)
                
                if brand_data:
                    all_technical_data['brands_technical_data'][brand_name] = brand_data
                    
                    # Pause entre les marques (5-7 secondes)
                    time.sleep(random.uniform(5, 7))
                    
                    # Afficher le progrès tous les 10 marques
                    if i % 10 == 0:
                        brands_with_data = len(all_technical_data['brands_technical_data'])
                        logger.info(f"📊 Progrès: {i}/{len(brands_to_process)} marques, {brands_with_data} avec données")
                
            except Exception as e:
                logger.error(f"   ❌ Erreur: {e}")
                continue
        
        # Métadonnées finales
        total_models = sum(
            brand['scraped_models'] 
            for brand in all_technical_data['brands_technical_data'].values()
        )
        
        all_technical_data['metadata']['brands_with_data'] = len(all_technical_data['brands_technical_data'])
        all_technical_data['metadata']['total_models_scraped'] = total_models
        
        return all_technical_data
    
    def save_technical_data(self, technical_data, output_file=None):
        """Sauvegarde les données techniques."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"data/autodata_technical_specs_{timestamp}.json"
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(technical_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Données techniques sauvegardées: {output_file}")
            
            # Générer aussi un CSV pour analyse
            self.generate_technical_csv(technical_data, output_file.replace('.json', '.csv'))
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return None
    
    def generate_technical_csv(self, technical_data, csv_file):
        """Génère un fichier CSV pour analyse des données techniques."""
        try:
            rows = []
            
            for brand_name, brand_data in technical_data['brands_technical_data'].items():
                for model_name, model_data in brand_data['models'].items():
                    specs = model_data['specifications']
                    
                    # Ligne de base
                    row = {
                        'brand': brand_name,
                        'model': model_name,
                        'url': model_data['url'],
                        'scraped_at': model_data['scraped_at']
                    }
                    
                    # Ajouter toutes les spécifications
                    for category, category_specs in specs.items():
                        if isinstance(category_specs, dict):
                            for spec_name, spec_value in category_specs.items():
                                row[f'{category}_{spec_name}'] = spec_value
                        elif isinstance(category_specs, list):
                            row[f'{category}_list'] = '; '.join(category_specs)
                        else:
                            row[f'{category}_value'] = category_specs
                    
                    rows.append(row)
            
            # Sauvegarder avec pandas si disponible, sinon avec csv standard
            if HAS_PANDAS:
                df = pd.DataFrame(rows)
                df.to_csv(csv_file, index=False, encoding='utf-8')
                logger.info(f"📊 CSV technique généré (pandas): {csv_file} ({len(rows)} lignes)")
            else:
                # Génération CSV sans pandas
                import csv
                
                # Déterminer toutes les colonnes
                all_columns = set()
                for row in rows:
                    all_columns.update(row.keys())
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_columns))
                    writer.writeheader()
                    writer.writerows(rows)
                
                logger.info(f"📊 CSV technique généré (csv standard): {csv_file} ({len(rows)} lignes)")
            
        except Exception as e:
            logger.error(f"❌ Erreur génération CSV: {e}")
    
    def close(self):
        """Ferme le driver."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("🔒 Driver fermé")

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Auto-Data Technical Specifications Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python autodata_technical_scraper.py                    # Toutes les marques
  python autodata_technical_scraper.py --popular-brands   # Marques populaires seulement
  python autodata_technical_scraper.py --brand "BMW"      # Marque spécifique
  python autodata_technical_scraper.py --limit 50         # Maximum 50 marques
        """
    )
    
    parser.add_argument('--popular-brands', action='store_true',
                       help='Scraper seulement les marques populaires')
    parser.add_argument('--brand', type=str, metavar='BRAND_NAME',
                       help='Scraper une marque spécifique')
    parser.add_argument('--limit', type=int, metavar='N',
                       help='Limiter le nombre de marques à scraper')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Mode headless (défaut: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                       help='Afficher le navigateur')
    
    args = parser.parse_args()
    
    logger.info("🚀 Auto-Data Technical Specifications Scraper v1.0")
    logger.info(f"   • Mode headless: {args.headless}")
    
    try:
        scraper = AutoDataTechnicalScraper(headless=args.headless)
        
        if args.brand:
            # Scraper une marque spécifique
            logger.info(f"🎯 Scraping marque spécifique: {args.brand}")
            
            # Trouver la marque
            brand_info = None
            for b in scraper.brands_list:
                if b['name'].lower() == args.brand.lower():
                    brand_info = b
                    break
            
            if brand_info:
                brand_data = scraper.scrape_brand_technical_data(
                    brand_info['name'], 
                    brand_info['id']
                )
                
                technical_data = {
                    'metadata': {
                        'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'scraper_version': 'v1.0_technical_specs',
                        'source': 'Auto-Data.net Technical Specifications',
                        'single_brand': brand_info['name']
                    },
                    'brands_technical_data': {args.brand: brand_data}
                }
                
                output_file = scraper.save_technical_data(technical_data)
                
            else:
                logger.error(f"❌ Marque {args.brand} non trouvée")
        
        elif args.popular_brands:
            # Scraper les marques populaires
            logger.info("🎯 Scraping marques populaires...")
            popular_data = scraper.scrape_popular_brands()
            
            technical_data = {
                'metadata': {
                    'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'scraper_version': 'v1.0_technical_specs',
                    'source': 'Auto-Data.net Technical Specifications',
                    'type': 'popular_brands'
                },
                'brands_technical_data': popular_data
            }
            
            output_file = scraper.save_technical_data(technical_data)
        
        else:
            # Scraper toutes les marques
            logger.info("🌍 Scraping complet...")
            technical_data = scraper.scrape_all_brands_with_progress(max_brands=args.limit)
            output_file = scraper.save_technical_data(technical_data)
        
        if output_file:
            logger.info(f"🎉 SUCCESS! Données techniques: {output_file}")
            
            # Afficher un résumé
            if 'brands_technical_data' in technical_data:
                brands_count = len(technical_data['brands_technical_data'])
                models_count = sum(
                    brand['scraped_models'] 
                    for brand in technical_data['brands_technical_data'].values()
                )
                
                logger.info(f"📊 RÉSUMÉ:")
                logger.info(f"   • Marques avec données: {brands_count}")
                logger.info(f"   • Modèles avec specs: {models_count}")
        else:
            logger.error("❌ Échec sauvegarde")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Interruption par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur générale: {e}")
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main()