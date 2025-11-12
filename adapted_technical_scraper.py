#!/usr/bin/env python3
"""
Scraper Auto-Data Adapté - Version Fonctionnelle
Basé sur l'analyse réelle de la structure du site
"""

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
        logging.FileHandler('adapted_technical_scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AdaptedAutoDataScraper:
    """Scraper Auto-Data adapté à la vraie structure du site."""
    
    def __init__(self, headless=True):
        self.base_url = "https://www.auto-data.net"
        self.technical_data = {}
        self.setup_driver(headless)
        
        # Marques prioritaires basées sur l'analyse
        self.priority_brands = [
            "BMW", "Toyota", "Audi", "Volkswagen", "Ford",
            "Mercedes-Benz", "Honda", "Nissan", "Hyundai", "Kia",
            "Peugeot", "Renault", "Skoda", "SEAT", "Citroen"
        ]
    
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
            logger.info("✅ Driver Selenium configuré (adapté Auto-Data)")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration driver: {e}")
            raise
    
    def navigate_to_brand_page(self, brand_name):
        """Navigate à la page de marque spécifique."""
        try:
            # URLs testées manuellement
            brand_urls = [
                f"{self.base_url}/bg/brand-list/",  # Page liste des marques
                f"{self.base_url}/bg/brand/86/",   # BMW direct (ID 86 d'après analyse)
                f"{self.base_url}/bg/brand/1/",    # Alfa Romeo (ID approximatif)
            ]
            
            for url in brand_urls:
                try:
                    logger.info(f"🔍 Test URL: {url}")
                    self.driver.get(url)
                    time.sleep(3)
                    
                    # Vérifier si on a accès à la page
                    if "brand" in self.driver.current_url.lower():
                        logger.info(f"✅ Page marques accessible: {self.driver.current_url}")
                        return True
                except Exception as e:
                    logger.debug(f"URL échouée: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur navigation marques: {e}")
            return False
    
    def search_for_brand_models(self, brand_name):
        """Cherche les modèles d'une marque via recherche ou navigation."""
        try:
            logger.info(f"🔍 Recherche de modèles pour {brand_name}")
            
            # Méthode 1: Utiliser la recherche du site
            try:
                # Chercher la barre de recherche
                search_selectors = [
                    "input[name='search']",
                    "input[placeholder*='search']",
                    "input[placeholder*='recherche']",
                    "#search",
                    ".search-input",
                    "input[type='text']"
                ]
                
                search_input = None
                for selector in search_selectors:
                    try:
                        search_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if search_input:
                    logger.info("   🔍 Utilisation de la recherche du site")
                    search_input.clear()
                    search_input.send_keys(brand_name)
                    time.sleep(2)
                    
                    # Soumettre la recherche
                    submit_selectors = [
                        "button[type='submit']",
                        "input[type='submit']",
                        ".search-btn",
                        "#search-btn"
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            submit_btn.click()
                            time.sleep(3)
                            break
                        except:
                            continue
                    
                    # Analyser les résultats de recherche
                    return self.extract_model_links_from_current_page(brand_name)
                
            except Exception as e:
                logger.debug(f"Erreur recherche: {e}")
            
            # Méthode 2: Analyser la page actuelle pour des liens directs
            return self.extract_model_links_from_current_page(brand_name)
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche {brand_name}: {e}")
            return []
    
    def extract_model_links_from_current_page(self, brand_name):
        """Extrait les liens de modèles depuis la page actuelle."""
        model_links = []
        
        try:
            # Sélecteurs étendus basés sur l'analyse
            extended_selectors = [
                # Sélecteurs génériques
                "a[href*='/bg/car/']",
                "a[href*='car/']", 
                "a[href*='/car']",
                "a[href*='bmw']",  # Spécifique BMW
                "a[href*='toyota']", # Spécifique Toyota
                "a[href*='audi']",   # Spécifique Audi
                
                # Liens dans tableaux
                "table a",
                "td a",
                "tr a",
                
                # Liens dans listes
                "ul a",
                "li a",
                
                # Classes génériques
                "a[href*='/bg/']",
                "a[href*='/']",
            ]
            
            logger.info("   🔍 Test des sélecteurs étendus")
            
            for selector in extended_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute("href")
                        text = element.text.strip()
                        
                        if href and text and len(text) > 1:
                            # Filtrer par pertinence (marque dans l'URL ou le texte)
                            is_relevant = (
                                brand_name.lower() in text.lower() or
                                brand_name.lower() in href.lower() or
                                "car" in href.lower() or
                                "vehicle" in href.lower()
                            )
                            
                            if is_relevant:
                                model_links.append({
                                    'name': text,
                                    'url': href,
                                    'brand': brand_name,
                                    'selector_used': selector
                                })
                    
                    if model_links:
                        logger.info(f"   ✅ {selector}: {len(model_links)} modèles trouvés")
                        break
                        
                except Exception as e:
                    continue
            
            # Dédupliquer par URL
            unique_links = {}
            for link in model_links:
                if link['url'] not in unique_links:
                    unique_links[link['url']] = link
            
            final_links = list(unique_links.values())
            
            if final_links:
                logger.info(f"   📊 {len(final_links)} liens de modèles extraits")
                return final_links[:10]  # Limiter à 10 modèles
            else:
                logger.warning(f"   ⚠️ Aucun modèle trouvé pour {brand_name}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur extraction liens: {e}")
            return []
    
    def scrape_model_specifications(self, model_link):
        """Scrape les spécifications d'un modèle."""
        try:
            logger.info(f"   🚗 Scraping: {model_link['name']}")
            
            # Naviguer vers la page du modèle
            self.driver.get(model_link['url'])
            time.sleep(3)
            
            specs = {
                'brand': model_link['brand'],
                'model': model_link['name'],
                'url': model_link['url'],
                'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                'specifications': {}
            }
            
            # Extraire les spécifications avec méthodes multiples
            specs['specifications']['basic'] = self.extract_basic_specs_adapted()
            specs['specifications']['performance'] = self.extract_performance_specs_adapted()
            specs['specifications']['dimensions'] = self.extract_dimension_specs_adapted()
            specs['specifications']['engine'] = self.extract_engine_specs_adapted()
            specs['specifications']['transmission'] = self.extract_transmission_specs_adapted()
            
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
    
    def extract_basic_specs_adapted(self):
        """Extrait les specs de base avec méthodes adaptées."""
        basic = {}
        
        try:
            # Méthode 1: Recherche par texte avec multiples langues
            spec_names = [
                'Years', 'Production years', 'Annee de fabricatie',
                'Fuel', 'Carburant', 'Combustibil', 'Treburi',
                'Doors', 'Portes', 'Usi',
                'Seats', 'Places', 'Locuri'
            ]
            
            for spec_name in spec_names:
                try:
                    # XPath flexible
                    xpath = f"//*[contains(text(), '{spec_name}')]/following::*[1]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        value = element.text.strip()
                        if value and value not in ['N/A', 'N/A', '']:
                            key = spec_name.lower().replace(' ', '_')
                            basic[key] = value
                            logger.debug(f"   📝 {spec_name}: {value}")
                            break
                except:
                    continue
            
            # Méthode 2: Extraire depuis le titre de la page ou les meta
            try:
                title = self.driver.title
                if title:
                    # Essayer d'extraire l'année depuis le titre
                    year_match = re.search(r'(\d{4})', title)
                    if year_match:
                        basic['page_year'] = year_match.group(1)
            except:
                pass
            
            return basic
            
        except Exception as e:
            logger.debug(f"Erreur extraction specs de base: {e}")
            return basic
    
    def extract_performance_specs_adapted(self):
        """Extrait les specs de performance adaptées."""
        performance = {}
        
        try:
            # Recherche plus flexible pour les performances
            perf_names = [
                'Power', 'Puissance', 'Putere',
                'Torque', 'Couple', 'Cuplu', 
                'Speed', 'Vitesse', 'Viteza',
                'Acceleration', 'Accelereaza',
                'Consumption', 'Consommation', 'Consum'
            ]
            
            for perf_name in perf_names:
                try:
                    xpath = f"//*[contains(text(), '{perf_name}')]/following::*[1]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        value = element.text.strip()
                        if value and value not in ['N/A', 'N/A', '']:
                            key = perf_name.lower().replace(' ', '_')
                            performance[key] = value
                            logger.debug(f"   🚀 {perf_name}: {value}")
                            break
                except:
                    continue
            
            return performance
            
        except Exception as e:
            logger.debug(f"Erreur extraction performance: {e}")
            return performance
    
    def extract_dimension_specs_adapted(self):
        """Extrait les specs dimensionnelles adaptées."""
        dimensions = {}
        
        try:
            dim_names = [
                'Length', 'Longueur', 'Lungime',
                'Width', 'Largeur', 'Latime', 
                'Height', 'Hauteur', 'Inaltime',
                'Weight', 'Masse', 'Masa',
                'Volume', 'Boot', 'Portbagaj'
            ]
            
            for dim_name in dim_names:
                try:
                    xpath = f"//*[contains(text(), '{dim_name}')]/following::*[1]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        value = element.text.strip()
                        if value and value not in ['N/A', 'N/A', '']:
                            key = dim_name.lower().replace(' ', '_')
                            dimensions[key] = value
                            logger.debug(f"   📏 {dim_name}: {value}")
                            break
                except:
                    continue
            
            return dimensions
            
        except Exception as e:
            logger.debug(f"Erreur extraction dimensions: {e}")
            return dimensions
    
    def extract_engine_specs_adapted(self):
        """Extrait les specs moteur adaptées."""
        engine = {}
        
        try:
            engine_names = [
                'Displacement', 'Cylindree', 'Cilindree',
                'Engine', 'Moteur', 'Motor',
                'Cylinder', 'Cilindru', 'Cilindri',
                'Valve', 'Supape',
                'Compression', 'Compresie'
            ]
            
            for engine_name in engine_names:
                try:
                    xpath = f"//*[contains(text(), '{engine_name}')]/following::*[1]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        value = element.text.strip()
                        if value and value not in ['N/A', 'N/A', '']:
                            key = engine_name.lower().replace(' ', '_')
                            engine[key] = value
                            logger.debug(f"   🔧 {engine_name}: {value}")
                            break
                except:
                    continue
            
            return engine
            
        except Exception as e:
            logger.debug(f"Erreur extraction moteur: {e}")
            return engine
    
    def extract_transmission_specs_adapted(self):
        """Extrait les specs de transmission adaptées."""
        transmission = {}
        
        try:
            trans_names = [
                'Gearbox', 'Boite', 'Cutie',
                'Drive', 'Traction', 'Tractiune',
                'Gear', 'Vitesse', 'Viteza'
            ]
            
            for trans_name in trans_names:
                try:
                    xpath = f"//*[contains(text(), '{trans_name}')]/following::*[1]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        value = element.text.strip()
                        if value and value not in ['N/A', 'N/A', '']:
                            key = trans_name.lower().replace(' ', '_')
                            transmission[key] = value
                            logger.debug(f"   ⚙️ {trans_name}: {value}")
                            break
                except:
                    continue
            
            return transmission
            
        except Exception as e:
            logger.debug(f"Erreur extraction transmission: {e}")
            return transmission
    
    def scrape_brand_with_adapted_method(self, brand_name, max_models=5):
        """Scrape une marque avec la méthode adaptée."""
        try:
            if not self.navigate_to_brand_page(brand_name):
                return {}
            
            # Chercher les modèles
            model_links = self.search_for_brand_models(brand_name)
            
            if not model_links:
                logger.warning(f"⚠️ Aucun modèle trouvé pour {brand_name}")
                return {}
            
            # Limiter le nombre de modèles
            model_links = model_links[:max_models]
            
            brand_data = {
                'brand': brand_name,
                'total_models_found': len(model_links),
                'scraped_models': 0,
                'models': {},
                'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                'method': 'adapted_auto_data_scraper'
            }
            
            logger.info(f"🔄 Scraping adapté pour {brand_name} ({len(model_links)} modèles)")
            
            for i, model_link in enumerate(model_links, 1):
                try:
                    logger.info(f"   [{i}/{len(model_links)}] {model_link['name']}")
                    
                    model_specs = self.scrape_model_specifications(model_link)
                    
                    if model_specs:
                        brand_data['models'][model_link['name']] = model_specs
                        brand_data['scraped_models'] += 1
                        
                        # Afficher résumé des specs
                        specs_count = sum(1 for cat in model_specs['specifications'].values() if cat)
                        logger.info(f"      ✅ {specs_count} catégories de specs")
                    else:
                        logger.warning(f"      ⚠️ Échec extraction specs")
                    
                    # Pause entre modèles
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"      ❌ Erreur modèle {model_link['name']}: {e}")
                    continue
            
            # Résumé
            logger.info(f"✅ {brand_name}: {brand_data['scraped_models']}/{brand_data['total_models_found']} modèles traités")
            
            return brand_data
            
        except Exception as e:
            logger.error(f"❌ Erreur scraping adapté {brand_name}: {e}")
            return {}
    
    def scrape_popular_brands_adapted(self):
        """Scrape les marques populaires avec la méthode adaptée."""
        logger.info("🎯 Scraping marques populaires (méthode adaptée)")
        
        results = {}
        
        for brand in self.priority_brands:
            logger.info(f"🎯 Traitement de {brand}")
            
            brand_data = self.scrape_brand_with_adapted_method(brand, max_models=3)
            
            if brand_data:
                results[brand] = brand_data
                
                # Pause entre marques
                time.sleep(random.uniform(5, 8))
            else:
                logger.warning(f"⚠️ Échec pour {brand}")
        
        return results
    
    def save_adapted_data(self, adapted_data, output_file=None):
        """Sauvegarde les données du scraper adapté."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"data/autodata_adapted_specs_{timestamp}.json"
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(adapted_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Données adaptées sauvegardées: {output_file}")
            
            # Générer CSV si possible
            if HAS_PANDAS:
                try:
                    csv_file = output_file.replace('.json', '.csv')
                    self.generate_adapted_csv(adapted_data, csv_file)
                except:
                    pass
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde adaptée: {e}")
            return None
    
    def generate_adapted_csv(self, adapted_data, csv_file):
        """Génère un CSV des données adaptées."""
        try:
            rows = []
            
            for brand_name, brand_data in adapted_data.get('brands_technical_data', {}).items():
                for model_name, model_data in brand_data.get('models', {}).items():
                    row = {
                        'brand': brand_name,
                        'model': model_name,
                        'url': model_data.get('url', ''),
                        'scraped_at': model_data.get('scraped_at', '')
                    }
                    
                    # Aplatir les spécifications
                    for category, specs in model_data.get('specifications', {}).items():
                        if isinstance(specs, dict):
                            for spec_name, spec_value in specs.items():
                                row[f'{category}_{spec_name}'] = spec_value
                        elif isinstance(specs, list):
                            row[f'{category}_list'] = '; '.join(specs)
                        else:
                            row[f'{category}_value'] = specs
                    
                    rows.append(row)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(csv_file, index=False, encoding='utf-8')
                logger.info(f"📊 CSV adapté généré: {csv_file} ({len(rows)} lignes)")
            
        except Exception as e:
            logger.error(f"❌ Erreur génération CSV adapté: {e}")
    
    def close(self):
        """Ferme le driver."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("🔒 Driver fermé")

def main():
    """Fonction principale du scraper adapté."""
    logger.info("🚀 Auto-Data Scraper Adapté v1.0")
    logger.info("   📋 Méthode basée sur l'analyse réelle du site")
    
    try:
        scraper = AdaptedAutoDataScraper(headless=True)
        
        # Scraper les marques populaires avec méthode adaptée
        logger.info("🎯 Démarrage scraping marques populaires...")
        adapted_results = scraper.scrape_popular_brands_adapted()
        
        if adapted_results:
            # Préparer les données pour sauvegarde
            final_data = {
                'metadata': {
                    'scraped_at': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'scraper_version': 'v1.0_adapted',
                    'source': 'Auto-Data.net Adapted Scraper',
                    'method': 'analyzed_structure_adaptation'
                },
                'brands_technical_data': adapted_results
            }
            
            # Sauvegarder
            output_file = scraper.save_adapted_data(final_data)
            
            if output_file:
                # Résumé final
                brands_count = len(adapted_results)
                models_count = sum(
                    brand.get('scraped_models', 0) 
                    for brand in adapted_results.values()
                )
                
                logger.info(f"🎉 SUCCESS! Données adaptées: {output_file}")
                logger.info(f"📊 RÉSUMÉ FINAL:")
                logger.info(f"   • Marques traitées: {brands_count}")
                logger.info(f"   • Modèles avec specs: {models_count}")
                logger.info(f"   • Méthode: Analyse structure réelle")
        else:
            logger.error("❌ Aucun résultat obtenu")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Interruption par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur générale: {e}")
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main()