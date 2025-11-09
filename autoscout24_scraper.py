#!/usr/bin/env python3
"""
AutoScout24 Scraper Principal - Version Autonome et Améliorée
Génère une liste de modèles par marque depuis AutoScout24.fr
Capable d'extraire automatiquement les marques si le fichier n'existe pas

Usage:
    python autoscout24_scraper.py                    # Scrape toutes les marques
    python autoscout24_scraper.py --test            # Test sur 20 marques
    python autoscout24_scraper.py --headless=False  # Voir le navigateur
    python autoscout24_scraper.py --max-brands 50   # Limiter à 50 marques
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

# Configuration logging avec emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AutoScout24Scraper:
    """Scraper AutoScout24 autonome et robuste."""
    
    def __init__(self, headless=True):
        self.base_url = "https://www.autoscout24.fr"
        self.brand_models_data = {}
        self.setup_driver(headless)
        self.load_brands_from_json()
        
    def setup_driver(self, headless=True):
        """Configure le driver Selenium avec des options optimisées."""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")  # Nouveau mode headless
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            logger.info("✅ Driver Selenium configuré")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration driver: {e}")
            raise
    
    def load_brands_from_json(self):
        """Charge la liste des marques depuis le fichier JSON ou l'extrait si nécessaire."""
        try:
            brands_file = Path("data/as24_brands_for_scraping.json")
            if brands_file.exists():
                with open(brands_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.brands_list = data["brands"]
                logger.info(f"📋 Chargé {len(self.brands_list)} marques depuis as24_brands_for_scraping.json")
                return True
            else:
                logger.warning("⚠️ Fichier as24_brands_for_scraping.json non trouvé")
                logger.info("🔄 Extraction automatique des marques depuis AutoScout24...")
                if self.extract_brands_from_autoscout24():
                    # Recharger après extraction
                    with open(brands_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.brands_list = data["brands"]
                    logger.info(f"✅ Extraction réussie: {len(self.brands_list)} marques")
                    return True
                else:
                    logger.error("❌ Impossible d'extraire les marques")
                    self.brands_list = []
                    return False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des marques: {e}")
            return False
    
    def extract_brands_from_autoscout24(self):
        """Extrait automatiquement les marques depuis AutoScout24."""
        try:
            logger.info("🔍 Extraction des marques depuis AutoScout24...")
            
            # S'assurer qu'on est sur la page d'accueil
            if not self.navigate_to_homepage():
                return False
            
            # Chercher le sélecteur des marques
            make_selectors = [
                "select[name='make']",
                "select[id='make']",
                "select[aria-label*='marque']",
                "select[aria-label*='brand']"
            ]
            
            make_select = None
            for selector in make_selectors:
                try:
                    make_select = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ Menu marques trouvé avec sélecteur: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not make_select:
                logger.error("❌ Menu déroulant des marques non trouvé")
                return False
            
            # Extraire toutes les options
            options = make_select.find_elements(By.TAG_NAME, "option")
            logger.info(f"🔍 Trouvé {len(options)} options dans le menu")
            
            brands_data = {}
            excluded_terms = [
                'top marques', 'autres marques', 'make', 'marque', 
                'tous', 'selectionner', 'toutes', '全部', '全部品牌'
            ]
            
            for option in options:
                try:
                    brand_name = option.text.strip()
                    brand_value = option.get_attribute("value")
                    
                    # Ignorer les options par défaut et les sections
                    if (brand_name and brand_value and 
                        brand_name not in ['Marque', 'Tous', 'Sélectionner', 'Make'] and
                        not any(term in brand_name.lower() for term in excluded_terms) and
                        brand_value != ''):
                        brands_data[brand_name] = brand_value
                        
                except Exception as e:
                    logger.debug(f"Erreur lors de l'extraction d'une option: {e}")
                    continue
            
            if not brands_data:
                logger.error("❌ Aucune marque trouvée")
                return False
            
            # Convertir en format attendu par le scraper
            self.brands_list = [{"name": name, "id": value} for name, value in brands_data.items()]
            
            # Sauvegarder le fichier brands_for_scraping.json
            output_data = {
                "metadata": {
                    "extracted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "source": "AutoScout24.fr Auto Extraction",
                    "method": "selenium_dropdown_analysis",
                    "total_brands": len(brands_data)
                },
                "brands": self.brands_list
            }

            brands_file = Path("data/as24_brands_for_scraping.json")
            brands_file.parent.mkdir(parents=True, exist_ok=True)
            with open(brands_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            # Générer aussi la version Markdown lisible
            self.generate_brands_markdown_version(output_data, str(brands_file))

            logger.info(f"💾 Fichier as24_brands_for_scraping.json créé: {len(brands_data)} marques")
            
            # Comparer avec la version précédente s'il y en a une
            self.compare_with_previous_version()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction des marques: {e}")
            return False
    
    def compare_with_previous_version(self):
        """Compare avec la version précédente et affiche les changements."""
        try:
            # Chercher le fichier de données le plus récent
            data_dir = Path("data")
            version_pattern = r"as24_scraped_models_(\d{8}_\d{6})\.json"
            
            versions = []
            for file in data_dir.glob("as24_scraped_models_*.json"):
                match = re.search(version_pattern, file.name)
                if match:
                    timestamp = match.group(1)
                    versions.append((timestamp, file))
            
            if not versions:
                logger.info("ℹ️ Aucune version précédente trouvée")
                return
            
            # Trouver la version la plus récente
            versions.sort(key=lambda x: x[0])
            previous_file = versions[-1][1]
            
            logger.info(f"🔄 Comparaison avec la version précédente: {previous_file.name}")
            
            # Charger la version précédente
            with open(previous_file, 'r', encoding='utf-8') as f:
                previous_data = json.load(f)
            
            # Comparer les marques
            previous_brands = set(previous_data["brands_models"].keys())
            current_brands = set(brand["name"] for brand in self.brands_list)
            
            new_brands = current_brands - previous_brands
            removed_brands = previous_brands - current_brands
            
            # Afficher le rapport de changements
            logger.info("📊 RAPPORT DE VERSIONING:")
            logger.info(f"   • Marques précédentes: {len(previous_brands)}")
            logger.info(f"   • Marques actuelles: {len(current_brands)}")
            logger.info(f"   • Changement: {len(current_brands) - len(previous_brands):+d}")
            
            if new_brands:
                logger.info(f"   • NOUVELLES MARQUES ({len(new_brands)}):")
                for brand in sorted(new_brands):
                    logger.info(f"     + {brand}")
            
            if removed_brands:
                logger.info(f"   • MARQUES SUPPRIMÉES ({len(removed_brands)}):")
                for brand in sorted(removed_brands):
                    logger.info(f"     - {brand}")
            
            if not new_brands and not removed_brands:
                logger.info("   ✅ Aucune marque ajoutée ou supprimée")
            
        except Exception as e:
            logger.debug(f"Erreur lors de la comparaison: {e}")
    
    def navigate_to_homepage(self):
        """Navigue vers la page d'accueil et attend le chargement complet."""
        try:
            logger.info(f"🌐 Navigation vers: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Attendre que les éléments critiques soient présents
            WebDriverWait(self.driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "body")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='make']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[id='make']"))
                )
            )
            
            # Attendre le chargement des menus déroulants
            time.sleep(3)
            logger.info("✅ Page d'accueil chargée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur navigation homepage: {e}")
            return False
    
    def select_brand_in_menu(self, brand_name, brand_id):
        """Sélectionne une marque dans le menu déroulant."""
        try:
            make_selectors = [
                "select[name='make']",
                "select[id='make']",
                ".make-select"
            ]
            
            make_select = None
            for selector in make_selectors:
                try:
                    make_select = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.debug(f"✅ Menu marques trouvé avec: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not make_select:
                logger.error("❌ Menu marques non trouvé")
                return False
            
            select = Select(make_select)
            select.select_by_value(brand_id)
            
            # Attendre que la page se mette à jour
            time.sleep(2)
            logger.debug(f"✅ Marque '{brand_name}' sélectionnée (ID: {brand_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection marque {brand_name}: {e}")
            return False
    
    def get_model_menu_options(self):
        """Récupère les options du menu déroulant des modèles."""
        try:
            model_selectors = [
                "select[name='model']",
                "select[id='model']",
                "select[aria-label*='modèle']",
                "select[aria-label*='model']",
                ".model-select",
                "#model-select"
            ]
            
            for selector in model_selectors:
                try:
                    model_select = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"{selector} option"))
                    )
                    
                    options = model_select.find_elements(By.TAG_NAME, "option")
                    models = []
                    
                    logger.debug(f"🔍 Menu modèles: {selector}, {len(options)} options")
                    
                    for option in options:
                        model_name = option.text.strip()
                        if model_name and model_name not in ['Modèle', 'Tous', 'Sélectionner', 'Model']:
                            models.append(model_name)
                    
                    if models:
                        logger.debug(f"✅ {len(models)} modèles trouvés")
                        return models
                    
                except (NoSuchElementException, TimeoutException):
                    continue
            
            logger.warning("⚠️ Menu modèles non trouvé ou vide")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération modèles: {e}")
            return []
    
    def scrape_brand_models(self, brand_name, brand_id):
        """Scrape les modèles d'une marque spécifique."""
        try:
            if not self.select_brand_in_menu(brand_name, brand_id):
                return []
            
            models = self.get_model_menu_options()
            
            if models:
                logger.info(f"✅ {brand_name}: {len(models)} modèles récupérés")
                return models
            else:
                logger.warning(f"⚠️ {brand_name}: Aucun modèle trouvé")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur scraping {brand_name}: {e}")
            return []
    
    def compare_model_changes_with_previous(self, brand_name, new_models):
        """Compare les modèles d'une marque avec la version précédente."""
        try:
            # Chercher le fichier de données le plus récent
            data_dir = Path("data")
            version_pattern = r"as24_scraped_models_(\d{8}_\d{6})\.json"
            
            versions = []
            for file in data_dir.glob("as24_scraped_models_*.json"):
                match = re.search(version_pattern, file.name)
                if match:
                    timestamp = match.group(1)
                    versions.append((timestamp, file))
            
            if not versions:
                return None
            
            # Trouver la version la plus récente
            versions.sort(key=lambda x: x[0])
            previous_file = versions[-1][1]
            
            # Charger la version précédente
            with open(previous_file, 'r', encoding='utf-8') as f:
                previous_data = json.load(f)
            
            # Comparer les modèles de cette marque
            previous_models = set(previous_data["brands_models"].get(brand_name, []))
            current_models = set(new_models)
            
            new_models_for_brand = current_models - previous_models
            removed_models_for_brand = previous_models - current_models
            
            if new_models_for_brand or removed_models_for_brand:
                logger.info(f"   🔄 Changements modèles pour {brand_name}:")
                if new_models_for_brand:
                    logger.info(f"     + Nouveaux: {', '.join(sorted(new_models_for_brand))}")
                if removed_models_for_brand:
                    logger.info(f"     - Supprimés: {', '.join(sorted(removed_models_for_brand))}")
            
            return {
                "new_models": list(new_models_for_brand),
                "removed_models": list(removed_models_for_brand),
                "total_changes": len(new_models_for_brand) + len(removed_models_for_brand)
            }
            
        except Exception as e:
            logger.debug(f"Erreur lors de la comparaison des modèles pour {brand_name}: {e}")
            return None
    
    def update_execution_history(self, output_file, versioning_data=None):
        """Met à jour l'historique des exécutions en format Markdown."""
        try:
            history_file = Path("docs/execution_history.md")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Générer les données de versioning pour l'historique
            execution_data = self.generate_execution_data(output_file, versioning_data)
            
            # Lire l'historique existant ou créer un nouveau
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = self.generate_history_header()
            
            # Ajouter la nouvelle entrée au DÉBUT (après l'en-tête)
            entry = self.format_execution_entry(execution_data)
            
            if content.startswith("#"):
                lines = content.split('\n')
                header_end = 0
                
                # CORRECTION: Trouver la vraie fin de l'en-tête (après les "---" de séparation)
                for i, line in enumerate(lines):
                    if line.strip() == '---' and i > 5:  # Il doit y avoir du contenu avant
                        header_end = i + 1  # +1 pour passer la ligne "---"
                        break
                
                if header_end > 0:
                    # INSÉRER au début de la section historique (après l'en-tête)
                    content = '\n'.join(lines[:header_end]) + entry + '\n' + '\n'.join(lines[header_end:])
                else:
                    # Si on ne trouve pas la séparation, ajouter après l'en-tête existant
                    content += '\n' + entry
            else:
                content = self.generate_history_header() + entry
            
            # Sauvegarder
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"📝 Historique mis à jour: {history_file}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour de l'historique: {e}")
    
    def generate_history_header(self):
        """Génère l'en-tête du fichier d'historique."""
        return """# 📊 AutoScout24 Scraper - Historique des Exécutions

Ce fichier contient l'historique complet des exécutions du scraper avec les informations de versioning.

## 📋 Structure
- **Timestamp** : Date et heure d'exécution
- **Fichier de données** : Lien vers le fichier JSON généré
- **Statistiques** : Nombre de marques et modèles traités
- **Versioning** : Comparaison avec la version précédente
- **Changements** : Détail des nouvelles marques, marques supprimées et modèles modifiés

---

"""
    
    def generate_execution_data(self, output_file, versioning_data):
        """Génère les données de l'exécution pour l'historique."""
        # Charger le fichier de données pour récupérer les métadonnées
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data["metadata"]
        
        execution_data = {
            "timestamp": metadata["scraped_at"],
            "file": output_file,
            "file_name": Path(output_file).name,
            "total_brands": metadata["total_brands"],
            "total_models": metadata["total_models"],
            "brands_with_models": metadata["brands_with_models"],
            "brands_without_models": metadata["brands_without_models"],
            "scraper_version": metadata["scraper_version"],
            "method": metadata["method"],
            "versioning": versioning_data or {},
            "brands_data": data["brands_models"]
        }
        
        return execution_data
    
    def format_execution_entry(self, execution_data):
        """Formate une entrée d'exécution pour l'historique Markdown."""
        timestamp = execution_data["timestamp"]
        file_name = execution_data["file_name"]
        
        # Formater la date pour l'affichage
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            display_date = dt.strftime("%d/%m/%Y à %H:%M")
        except:
            display_date = timestamp
        
        # Construire l'entrée Markdown - STRUCTURE CLAIRE ET SÉPARÉE
        entry = f"\n## 📅 {display_date}\n\n"
        entry += f"**📄 Fichier de données** : `{file_name}`  \n"
        entry += f"**🚀 Scraper** : {execution_data['scraper_version']}  \n"
        entry += f"**🔧 Méthode** : {execution_data['method']}  \n\n"
        
        entry += "### 📊 Statistiques\n\n"
        entry += f"- **Marques traitées** : {execution_data['total_brands']}\n"
        entry += f"- **✅ Marques avec modèles** : {execution_data['brands_with_models']}\n"
        entry += f"- **❌ Marques sans modèles** : {execution_data['brands_without_models']}\n"
        entry += f"- **🏷️ Total modèles** : {execution_data['total_models']}\n\n"
        
        # Versioning détaillé seulement s'il y a des changements
        if execution_data.get('versioning') and any(execution_data['versioning'].values()):
            entry += "### 🔄 Versioning vs Version Précédente\n\n"
            
            if execution_data['versioning'].get('brand_changes', 0) != 0:
                entry += f"**📋 Marques** : {execution_data['versioning']['previous_brands']} → {execution_data['versioning']['current_brands']} ({execution_data['versioning']['brand_changes']:+d})\n"
            
            if execution_data['versioning'].get('model_changes', 0) != 0:
                entry += f"**🏷️ Modèles** : {execution_data['versioning']['previous_models']} → {execution_data['versioning']['current_models']} ({execution_data['versioning']['model_changes']:+d})\n\n"
            
            # Nouvelles marques
            if execution_data['versioning'].get('new_brands'):
                entry += f"**➕ Nouvelles marques ({len(execution_data['versioning']['new_brands'])})** :\n"
                for brand in execution_data['versioning']['new_brands']:
                    model_count = len(execution_data['brands_data'].get(brand, []))
                    entry += f"- {brand} ({model_count} modèles)\n"
                entry += "\n"
            
            # Marques supprimées
            if execution_data['versioning'].get('removed_brands'):
                entry += f"**➖ Marques supprimées ({len(execution_data['versioning']['removed_brands'])})** :\n"
                for brand in execution_data['versioning']['removed_brands']:
                    entry += f"- {brand}\n"
                entry += "\n"
            
            # Marques avec changements significatifs
            if execution_data['versioning'].get('significant_changes'):
                entry += f"**🔄 Marques avec changements significatifs ({len(execution_data['versioning']['significant_changes'])})** :\n"
                for change in execution_data['versioning']['significant_changes'][:5]:  # Limiter à 5
                    entry += f"- {change['brand']} : {change['previous_count']} → {change['current_count']} modèles\n"
                if len(execution_data['versioning']['significant_changes']) > 5:
                    entry += f"- ... et {len(execution_data['versioning']['significant_changes']) - 5} autres\n"
                entry += "\n"
        
        # Top marques par nombre de modèles (top 10)
        sorted_brands = sorted(
            execution_data['brands_data'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        entry += "### 🏆 Top 10 Marques (par nombre de modèles)\n\n"
        for i, (brand, models) in enumerate(sorted_brands, 1):
            entry += f"{i}. **{brand}** - {len(models)} modèles\n"
        entry += "\n"
        
        # Détail des nouvelles marques importantes (si en mode test, pas toutes)
        if execution_data.get('versioning', {}).get('new_brands') and execution_data['total_brands'] <= 50:
            entry += "### 🆕 Détail des Nouvelles Marques\n\n"
            for brand in execution_data['versioning']['new_brands']:
                models = execution_data['brands_data'].get(brand, [])
                entry += f"**{brand}** ({len(models)} modèles) :\n"
                for model in sorted(models)[:5]:  # Limiter à 5 modèles par marque
                    entry += f"- {model}\n"
                if len(models) > 5:
                    entry += f"- ... et {len(models) - 5} autres\n"
                entry += "\n"
        
        entry += "---\n\n"
        
        return entry
    
    def save_results(self, output_file=None):
        """Sauvegarde les résultats avec versioning automatique et version Markdown."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"data/as24_scraped_models_{timestamp}.json"
            
            # Préparer les données
            result_data = {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "scraper_version": "v3.3_autonomous_with_history_and_markdown",
                    "source": "AutoScout24.fr Auto Scraping",
                    "method": "selenium_dynamic_dropdown_interaction",
                    "total_brands": len(self.brand_models_data),
                    "total_models": sum(len(models) for models in self.brand_models_data.values()),
                    "brands_with_models": len([b for b, models in self.brand_models_data.items() if models]),
                    "brands_without_models": len([b for b, models in self.brand_models_data.items() if not models])
                },
                "brands_models": self.brand_models_data
            }
            
            # Sauvegarder le fichier JSON
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            # Générer la version Markdown
            md_file = self.generate_markdown_version(result_data, output_file)
            
            logger.info(f"💾 Résultats sauvegardés:")
            logger.info(f"   📄 JSON: {output_file}")
            logger.info(f"   📝 MD: {md_file}")
            
            # Résumé final avec versioning
            total_models = result_data["metadata"]["total_models"]
            brands_with_models = result_data["metadata"]["brands_with_models"]
            
            # Rapport de versioning final
            versioning_data = self.generate_versioning_report(result_data)
            
            # Mettre à jour l'historique Markdown
            self.update_execution_history(output_file, versioning_data)
            
            logger.info("📊 RÉSUMÉ FINAL:")
            logger.info(f"   • Marques traitées: {len(self.brand_models_data)}")
            logger.info(f"   • Marques avec modèles: {brands_with_models}")
            logger.info(f"   • Total modèles: {total_models}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return None
    
    def generate_markdown_version(self, result_data, json_file_path):
        """Génère une version Markdown lisible des données."""
        try:
            # Créer le chemin du fichier Markdown
            json_path = Path(json_file_path)
            md_file = json_path.with_suffix('.md')
            
            # Préparer le contenu Markdown
            md_content = self.format_data_as_markdown(result_data)
            
            # Sauvegarder le fichier Markdown
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"📝 Fichier Markdown généré: {md_file}")
            return str(md_file)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du fichier Markdown: {e}")
            return None
    
    def format_data_as_markdown(self, result_data):
        """Formate les données en Markdown lisible."""
        try:
            metadata = result_data["metadata"]
            brands_models = result_data["brands_models"]
            
            # En-tête
            md_content = f"""# 🚗 AutoScout24 - Marques et Modèles

**Fichier généré le** : {metadata['scraped_at']}  
**Scraper** : {metadata['scraper_version']}  
**Source** : {metadata['source']}  
**Méthode** : {metadata['method']}  

## 📊 Statistiques Globales

- **📋 Marques traitées** : {metadata['total_brands']}
- **✅ Marques avec modèles** : {metadata['brands_with_models']}
- **❌ Marques sans modèles** : {metadata['brands_without_models']}
- **🏷️ Total modèles** : {metadata['total_models']}

---

## 📋 Liste Complète des Marques et Modèles

"""

            # Trier les marques alphabétiquement
            sorted_brands = sorted(brands_models.items())
            
            for brand_name, models in sorted_brands:
                if models:  # Seulement les marques avec des modèles
                    md_content += f"### {brand_name}\n\n"
                    md_content += f"**{len(models)} modèles** :\n\n"
                    
                    # Trier les modèles pour chaque marque
                    sorted_models = sorted(models)
                    
                    # Organiser en colonnes pour une meilleure lisibilité
                    if len(sorted_models) <= 10:
                        # Si peu de modèles, les afficher en ligne
                        md_content += "• " + "\n• ".join(sorted_models) + "\n\n"
                    else:
                        # Si beaucoup de modèles, les organiser en colonnes
                        md_content += "| Colonne 1 | Colonne 2 | Colonne 3 |\n"
                        md_content += "|-----------|-----------|----------|\n"
                        
                        # Remplir les colonnes
                        for i in range(0, len(sorted_models), 3):
                            col1 = sorted_models[i] if i < len(sorted_models) else ""
                            col2 = sorted_models[i+1] if i+1 < len(sorted_models) else ""
                            col3 = sorted_models[i+2] if i+2 < len(sorted_models) else ""
                            md_content += f"| {col1} | {col2} | {col3} |\n"
                        md_content += "\n"
            
            # Section des marques sans modèles (si il y en a)
            brands_without_models = [brand for brand, models in brands_models.items() if not models]
            if brands_without_models:
                md_content += f"\n## ❌ Marques Sans Modèles ({len(brands_without_models)})\n\n"
                for brand in sorted(brands_without_models):
                    md_content += f"- {brand}\n"
                md_content += "\n"
            
            # Top marques par nombre de modèles
            md_content += "## 🏆 Top 15 Marques (par nombre de modèles)\n\n"
            sorted_by_models = sorted(
                [(brand, len(models)) for brand, models in brands_models.items() if models],
                key=lambda x: x[1],
                reverse=True
            )[:15]
            
            for i, (brand, model_count) in enumerate(sorted_by_models, 1):
                md_content += f"{i}. **{brand}** - {model_count} modèles\n"
            
            # Répartition par nombre de modèles
            model_counts = [len(models) for models in brands_models.values() if models]
            if model_counts:
                md_content += "\n## 📈 Répartition du Nombre de Modèles\n\n"
                from collections import Counter
                count_distribution = Counter(model_counts)
                
                for model_count in sorted(count_distribution.keys(), reverse=True):
                    brand_count = count_distribution[model_count]
                    md_content += f"- **{model_count} modèles** : {brand_count} marque{'s' if brand_count > 1 else ''}\n"
            
            # Pied de page
            md_content += f"\n---\n\n"
            md_content += f"**Fichier source** : `as24_scraped_models_{metadata['scraped_at'].replace(':', '').replace('-', '').replace('T', '_')}.json`\n"
            md_content += f"**Généré par** : AutoScout24 Scraper {metadata['scraper_version']}\n"
            md_content += f"**Date de génération** : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n"
            
            return md_content
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du formatage Markdown: {e}")
            return f"# 🚗 AutoScout24 - Marques et Modèles\n\n**Erreur lors du formatage :** {e}\n"

    def generate_brands_markdown_version(self, brands_data, json_file_path):
        """Génère une version Markdown lisible des marques extraites."""
        try:
            # Créer le chemin du fichier Markdown
            json_path = Path(json_file_path)
            md_file = json_path.with_suffix('.md')

            # Préparer le contenu Markdown
            md_content = self.format_brands_as_markdown(brands_data)

            # Sauvegarder le fichier Markdown
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)

            logger.info(f"📝 Fichier Markdown des marques généré: {md_file}")
            return str(md_file)

        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du fichier Markdown des marques: {e}")
            return None

    def format_brands_as_markdown(self, brands_data):
        """Formate les données des marques en Markdown lisible."""
        try:
            metadata = brands_data["metadata"]
            brands_list = brands_data["brands"]

            # En-tête
            md_content = f"""# 🚗 AutoScout24 - Liste des Marques Disponibles

**Fichier généré le** : {metadata['extracted_at']}
**Source** : {metadata['source']}
**Méthode** : {metadata['method']}

## 📊 Statistiques

- **📋 Marques extraites** : {metadata['total_brands']}
- **🔍 Provenance** : Menu déroulant AutoScout24.fr

---

## 📋 Liste Complète des Marques

"""

            # Trier les marques alphabétiquement
            sorted_brands = sorted(brands_list, key=lambda x: x['name'])

            # Organiser en colonnes pour une meilleure lisibilité
            md_content += "| Marque | ID |\n"
            md_content += "|--------|----|\n"

            for brand in sorted_brands:
                md_content += f"| {brand['name']} | `{brand['id']}` |\n"

            md_content += "\n"

            # Section des statistiques supplémentaires
            md_content += "## 📈 Analyse des Marques\n\n"

            # Répartition par première lettre
            from collections import defaultdict
            letter_distribution = defaultdict(int)
            for brand in brands_list:
                first_letter = brand['name'][0].upper()
                letter_distribution[first_letter] += 1

            md_content += "### Répartition par Première Lettre\n\n"
            sorted_letters = sorted(letter_distribution.items())
            for letter, count in sorted_letters:
                md_content += f"- **{letter}** : {count} marque{'s' if count > 1 else ''}\n"

            # Top marques par longueur de nom
            md_content += "\n### Marques avec Noms les Plus Longs\n\n"
            longest_names = sorted(brands_list, key=lambda x: len(x['name']), reverse=True)[:10]
            for brand in longest_names:
                md_content += f"- **{brand['name']}** ({len(brand['name'])} caractères)\n"

            # Pied de page
            md_content += f"\n---\n\n"
            md_content += f"**Fichier source** : `as24_brands_for_scraping.json`\n"
            md_content += f"**Généré par** : AutoScout24 Scraper v{metadata.get('scraper_version', '3.3')}\n"
            md_content += f"**Date de génération** : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n"

            return md_content

        except Exception as e:
            logger.error(f"❌ Erreur lors du formatage Markdown des marques: {e}")
            return f"# 🚗 AutoScout24 - Liste des Marques\n\n**Erreur lors du formatage :** {e}\n"
    
    def generate_versioning_report(self, current_data):
        """Génère un rapport détaillé de versioning et retourne les données pour l'historique."""
        try:
            # Chercher le fichier de données le plus récent (sauf le fichier actuel)
            data_dir = Path("data")
            version_pattern = r"as24_scraped_models_(\d{8}_\d{6})\.json"
            
            versions = []
            for file in data_dir.glob("as24_scraped_models_*.json"):
                match = re.search(version_pattern, file.name)
                if match:
                    timestamp = match.group(1)
                    versions.append((timestamp, file))
            
            if len(versions) < 2:
                logger.info("ℹ️ Première exécution - aucun rapport de versioning")
                return {}
            
            # Trouver la version précédente (pas la plus récente, mais l'avant-dernière)
            versions.sort(key=lambda x: x[0])
            previous_file = versions[-2][1]  # L'avant-dernière version
            
            logger.info(f"🔄 Rapport de versioning vs {previous_file.name}")
            
            # Charger la version précédente
            with open(previous_file, 'r', encoding='utf-8') as f:
                previous_data = json.load(f)
            
            # Comparaisons globales
            previous_brands_count = len(previous_data["brands_models"])
            current_brands_count = len(current_data["brands_models"])
            brand_change = current_brands_count - previous_brands_count
            
            previous_models_count = sum(len(models) for models in previous_data["brands_models"].values())
            current_models_count = sum(len(models) for models in current_data["brands_models"].values())
            models_change = current_models_count - previous_models_count
            
            logger.info("📊 COMPARAISON GLOBALE:")
            logger.info(f"   • Marques: {previous_brands_count} → {current_brands_count} ({brand_change:+d})")
            logger.info(f"   • Modèles: {previous_models_count} → {current_models_count} ({models_change:+d})")
            
            # Détail des marques
            previous_brands = set(previous_data["brands_models"].keys())
            current_brands = set(current_data["brands_models"].keys())
            
            new_brands = current_brands - previous_brands
            removed_brands = previous_brands - current_brands
            
            if new_brands:
                logger.info(f"   • NOUVELLES MARQUES ({len(new_brands)}):")
                for brand in sorted(new_brands):
                    model_count = len(current_data["brands_models"][brand])
                    logger.info(f"     + {brand} ({model_count} modèles)")
            
            if removed_brands:
                logger.info(f"   • MARQUES SUPPRIMÉES ({len(removed_brands)}):")
                for brand in sorted(removed_brands):
                    logger.info(f"     - {brand}")
            
            # Marques avec changements de modèles significatifs
            significant_changes = []
            for brand in previous_brands & current_brands:
                previous_models = set(previous_data["brands_models"][brand])
                current_models = set(current_data["brands_models"][brand])
                
                if len(previous_models ^ current_models) >= 3:  # Au moins 3 changements
                    previous_count = len(previous_models)
                    current_count = len(current_models)
                    significant_changes.append({
                        "brand": brand,
                        "previous_count": previous_count,
                        "current_count": current_count,
                        "change": current_count - previous_count
                    })
            
            if significant_changes:
                logger.info(f"   • MARQUES AVEC CHANGEMENTS SIGNIFICATIFS ({len(significant_changes)}):")
                for change in sorted(significant_changes, key=lambda x: abs(x['change']), reverse=True)[:5]:  # Top 5
                    logger.info(f"     ~ {change['brand']}: {change['previous_count']} → {change['current_count']} modèles")
                if len(significant_changes) > 5:
                    logger.info(f"     ... et {len(significant_changes) - 5} autres")
            
            logger.info("📁 Fichier de comparaison disponible pour analyse détaillée")
            
            # Préparer les données pour l'historique
            return {
                "previous_brands": previous_brands_count,
                "current_brands": current_brands_count,
                "brand_changes": brand_change,
                "previous_models": previous_models_count,
                "current_models": current_models_count,
                "model_changes": models_change,
                "new_brands": list(new_brands),
                "removed_brands": list(removed_brands),
                "significant_changes": significant_changes
            }
            
        except Exception as e:
            logger.debug(f"Erreur lors de la génération du rapport de versioning: {e}")
            return {}
    
    def scrape_all_brands(self, max_brands=None):
        """Scrape toutes les marques de la liste JSON."""
        try:
            if not self.navigate_to_homepage():
                return False
            
            # Déterminer les marques à traiter
            brands_to_process = self.brands_list[:max_brands] if max_brands else self.brands_list
            logger.info(f"🚀 Début du scraping pour {len(brands_to_process)} marques")
            
            for i, brand_info in enumerate(brands_to_process, 1):
                brand_name = brand_info["name"]
                brand_id = brand_info["id"]
                
                logger.info(f"🏷️ [{i}/{len(brands_to_process)}] {brand_name}")
                
                try:
                    models = self.scrape_brand_models(brand_name, brand_id)
                    self.brand_models_data[brand_name] = models
                    
                    # Comparer avec la version précédente pour cette marque
                    model_changes = self.compare_model_changes_with_previous(brand_name, models)
                    
                    if models:
                        logger.info(f"   ✅ {len(models)} modèles")
                        if model_changes and model_changes["total_changes"] > 0:
                            logger.info(f"   🔄 Changements: +{len(model_changes['new_models'])} -{len(model_changes['removed_models'])}")
                    else:
                        logger.warning(f"   ⚠️ Aucun modèle")
                    
                except Exception as e:
                    logger.error(f"   ❌ Erreur: {e}")
                    self.brand_models_data[brand_name] = []
                
                # Pause entre les marques (2-4 secondes)
                time.sleep(random.uniform(2, 4))
                
                # Afficher le progrès tous les 10 marques
                if i % 10 == 0:
                    brands_with_models = len([b for b, models in self.brand_models_data.items() if models])
                    logger.info(f"📊 Progrès: {i}/{len(brands_to_process)} marques, {brands_with_models} avec modèles")
            
            logger.info(f"🎉 Scraping terminé! {len(self.brand_models_data)} marques traitées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping: {e}")
            return False
    
    def close(self):
        """Ferme le driver proprement."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("🔒 Driver fermé")

def main():
    """Fonction principale avec gestion d'arguments."""
    parser = argparse.ArgumentParser(
        description="AutoScout24 Scraper Autonome - Extrait les modèles par marque avec historique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python autoscout24_scraper.py                 # Toutes les marques (extraction auto si nécessaire)
  python autoscout24_scraper.py --test          # Test rapide (20 marques)
  python autoscout24_scraper.py --max-brands 50 # 50 marques maximum
  python autoscout24_scraper.py --headless=False # Voir le navigateur
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Mode test (20 marques seulement)')
    parser.add_argument('--max-brands', type=int, metavar='N',
                       help='Limiter le nombre de marques à scraper')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Mode headless (défaut: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                       help='Afficher le navigateur')
    
    args = parser.parse_args()
    
    # Déterminer les paramètres
    max_brands = 20 if args.test else args.max_brands
    
    logger.info("🚀 AutoScout24 Scraper Autonome - Version 3.3 avec Historique et Markdown")
    logger.info(f"   • Mode: {'Test' if args.test else 'Complet'}")
    logger.info(f"   • Headless: {args.headless}")
    logger.info(f"   • Marques max: {max_brands or 'Toutes'}")
    logger.info("   • 🚀 Extraction automatique des marques si nécessaire")
    logger.info("   • 📊 Rapport de versioning automatique")
    logger.info("   • 📝 Historique Markdown automatique")
    
    try:
        scraper = AutoScout24Scraper(headless=args.headless)
        
        # Lancer le scraping
        success = scraper.scrape_all_brands(max_brands=max_brands)
        
        if success:
            output_file = scraper.save_results()
            if output_file:
                logger.info(f"🎉 SUCCESS! Fichier généré: {output_file}")
                logger.info(f"📝 Historique disponible: docs/execution_history.md")
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