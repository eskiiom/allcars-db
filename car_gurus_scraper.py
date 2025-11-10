#!/usr/bin/env python3
"""
CarGurus.com Scraper Principal - Extension automobile pour le marché américain
Extracts models by brand from CarGurus.com
Capable of automatically extracting brands if file doesn't exist

Usage:
    python car_gurus_scraper.py                    # Scrape all brands
    python car_gurus_scraper.py --test             # Test on 20 brands
    python car_gurus_scraper.py --headless=False   # See the browser
    python car_gurus_scraper.py --max-brands 50    # Limit to 50 brands
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

# Configuration logging with emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/cguru_scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class CarGurusScraper:
    """CarGurus.com autonomous and robust scraper."""
    
    def __init__(self, headless=True):
        self.base_url = "https://www.cargurus.com"
        self.brand_models_data = {}
        self.setup_driver(headless)
        self.load_brands_from_json()
        
    def setup_driver(self, headless=True):
        """Configure Selenium driver with optimized options."""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")  # New headless mode
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
            logger.info("✅ Selenium driver configured")
            
        except Exception as e:
            logger.error(f"❌ Driver configuration error: {e}")
            raise
    
    def load_brands_from_json(self):
        """Load brand list from JSON file or extract if necessary."""
        try:
            brands_file = Path("data/cargurus_brands_for_scraping.json")
            if brands_file.exists():
                with open(brands_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.brands_list = data["brands"]
                logger.info(f"📋 Loaded {len(self.brands_list)} brands from cargurus_brands_for_scraping.json")
                return True
            else:
                logger.warning("⚠️ File cargurus_brands_for_scraping.json not found")
                logger.info("🔄 Automatic brand extraction from CarGurus...")
                if self.extract_brands_from_cargurus():
                    # Reload after extraction
                    with open(brands_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.brands_list = data["brands"]
                    logger.info(f"✅ Extraction successful: {len(self.brands_list)} brands")
                    return True
                else:
                    logger.error("❌ Unable to extract brands")
                    self.brands_list = []
                    return False
                
        except Exception as e:
            logger.error(f"❌ Error loading brands: {e}")
            return False
    
    def extract_brands_from_cargurus(self):
        """Automatically extract brands from CarGurus.com."""
        try:
            logger.info("🔍 Extracting brands from CarGurus...")
            
            # Make sure we're on the homepage
            if not self.navigate_to_homepage():
                return False
            
            # CarGurus specific brand selector
            make_select = self.driver.find_element(By.ID, "car-picker-make-select")
            logger.info("✅ CarGurus brand menu found")
            
            # Extract all options
            options = make_select.find_elements(By.TAG_NAME, "option")
            logger.info(f"🔍 Found {len(options)} options in menu")
            
            brands_data = {}
            excluded_terms = [
                'all makes', 'make', 'brand', 
                'all', 'select', 'any'
            ]
            
            for option in options:
                try:
                    brand_name = option.text.strip()
                    brand_value = option.get_attribute("value")
                    
                    # Ignore default options and sections
                    if (brand_name and brand_value and 
                        brand_name not in ['All makes', 'Make', 'Any Make', 'Select Make', 'All Makes'] and
                        not any(term in brand_name.lower() for term in excluded_terms) and
                        brand_value != ''):
                        brands_data[brand_name] = brand_value
                        
                except Exception as e:
                    logger.debug(f"Error extracting option: {e}")
                    continue
            
            if not brands_data:
                logger.error("❌ No brands found")
                return False
            
            # Convert to expected format
            self.brands_list = [{"name": name, "id": value} for name, value in brands_data.items()]
            
            # Save the brands_for_scraping.json file
            output_data = {
                "metadata": {
                    "extracted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "source": "CarGurus.com Auto Extraction",
                    "method": "selenium_dropdown_analysis",
                    "total_brands": len(brands_data)
                },
                "brands": self.brands_list
            }

            brands_file = Path("data/cargurus_brands_for_scraping.json")
            brands_file.parent.mkdir(parents=True, exist_ok=True)
            with open(brands_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            # Generate markdown version
            self.generate_brands_markdown_version(output_data, str(brands_file))

            logger.info(f"💾 File cargurus_brands_for_scraping.json created: {len(brands_data)} brands")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error extracting brands: {e}")
            return False
    
    def navigate_to_homepage(self):
        """Navigate to homepage and wait for complete loading."""
        try:
            logger.info(f"🌐 Navigating to: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for CarGurus brand selector to be present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "car-picker-make-select"))
            )
            
            # Wait for dropdown menus to load
            time.sleep(3)
            logger.info("✅ Homepage loaded")
            return True
            
        except Exception as e:
            logger.error(f"❌ Homepage navigation error: {e}")
            return False
    
    def select_brand_in_menu(self, brand_name, brand_id):
        """Select a brand in the dropdown menu."""
        try:
            make_select = self.driver.find_element(By.ID, "car-picker-make-select")
            
            select = Select(make_select)
            select.select_by_value(brand_id)
            
            # Wait for page to update
            time.sleep(2)
            logger.debug(f"✅ Brand '{brand_name}' selected (ID: {brand_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error selecting brand {brand_name}: {e}")
            return False
    
    def get_model_menu_options(self):
        """Get options from model dropdown menu."""
        try:
            # Wait for model selector to be present
            model_select = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "car-picker-model-select"))
            )
            
            options = model_select.find_elements(By.TAG_NAME, "option")
            models = []
            
            logger.debug(f"🔍 Model menu: {len(options)} options")
            
            for option in options:
                model_name = option.text.strip()
                if model_name and model_name not in ['All models', 'Model', 'Any Model', 'Select Model', 'All Models']:
                    models.append(model_name)
            
            if models:
                logger.debug(f"✅ {len(models)} models found")
                return models
            else:
                logger.warning("⚠️ No models found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error retrieving models: {e}")
            return []
    
    def scrape_brand_models(self, brand_name, brand_id):
        """Scrape models for a specific brand."""
        try:
            if not self.select_brand_in_menu(brand_name, brand_id):
                return []
            
            models = self.get_model_menu_options()
            
            if models:
                logger.info(f"✅ {brand_name}: {len(models)} models retrieved")
                return models
            else:
                logger.warning(f"⚠️ {brand_name}: No models found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error scraping {brand_name}: {e}")
            return []
    
    def save_results(self, output_file=None):
        """Save results with automatic versioning and Markdown version."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"data/cargurus_scraped_models_{timestamp}.json"
            
            # Prepare data
            result_data = {
                "metadata": {
                    "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "scraper_version": "v1.0_cargurus_us_market",
                    "source": "CarGurus.com Auto Scraping",
                    "method": "selenium_dropdown_interaction",
                    "total_brands": len(self.brand_models_data),
                    "total_models": sum(len(models) for models in self.brand_models_data.values()),
                    "brands_with_models": len([b for b, models in self.brand_models_data.items() if models]),
                    "brands_without_models": len([b for b, models in self.brand_models_data.items() if not models])
                },
                "brands_models": self.brand_models_data
            }
            
            # Save JSON file
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            # Generate Markdown version
            md_file = self.generate_markdown_version(result_data, output_file)
            
            logger.info(f"💾 Results saved:")
            logger.info(f"   📄 JSON: {output_file}")
            logger.info(f"   📝 MD: {md_file}")
            
            # Final summary
            total_models = result_data["metadata"]["total_models"]
            brands_with_models = result_data["metadata"]["brands_with_models"]
            
            logger.info("📊 FINAL SUMMARY:")
            logger.info(f"   • Brands processed: {len(self.brand_models_data)}")
            logger.info(f"   • Brands with models: {brands_with_models}")
            logger.info(f"   • Total models: {total_models}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Save error: {e}")
            return None
    
    def generate_markdown_version(self, result_data, json_file_path):
        """Generate a readable Markdown version of the data."""
        try:
            # Create Markdown file path
            json_path = Path(json_file_path)
            md_file = json_path.with_suffix('.md')
            
            # Prepare Markdown content
            md_content = self.format_data_as_markdown(result_data)
            
            # Save Markdown file
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"📝 Markdown file generated: {md_file}")
            return str(md_file)
            
        except Exception as e:
            logger.error(f"❌ Error generating Markdown file: {e}")
            return None
    
    def format_data_as_markdown(self, result_data):
        """Format data as readable Markdown."""
        try:
            metadata = result_data["metadata"]
            brands_models = result_data["brands_models"]
            
            # Header
            md_content = f"""# 🚗 CarGurus.com - Brands and Models

**File generated on** : {metadata['scraped_at']}  
**Scraper** : {metadata['scraper_version']}  
**Source** : {metadata['source']}  
**Method** : {metadata['method']}  

## 📊 Global Statistics

- **📋 Brands processed** : {metadata['total_brands']}
- **✅ Brands with models** : {metadata['brands_with_models']}
- **❌ Brands without models** : {metadata['brands_without_models']}
- **🏷️ Total models** : {metadata['total_models']}

---

## 📋 Complete List of Brands and Models

"""

            # Sort brands alphabetically
            sorted_brands = sorted(brands_models.items())
            
            for brand_name, models in sorted_brands:
                if models:  # Only brands with models
                    md_content += f"### {brand_name}\n\n"
                    md_content += f"**{len(models)} models** :\n\n"
                    
                    # Sort models for each brand
                    sorted_models = sorted(models)
                    md_content += "• " + "\n• ".join(sorted_models) + "\n\n"
            
            # Section of brands without models (if any)
            brands_without_models = [brand for brand, models in brands_models.items() if not models]
            if brands_without_models:
                md_content += f"\n## ❌ Brands Without Models ({len(brands_without_models)})\n\n"
                for brand in sorted(brands_without_models):
                    md_content += f"- {brand}\n"
                md_content += "\n"
            
            # Top brands by number of models
            md_content += "## 🏆 Top 15 Brands (by number of models)\n\n"
            sorted_by_models = sorted(
                [(brand, len(models)) for brand, models in brands_models.items() if models],
                key=lambda x: x[1],
                reverse=True
            )[:15]
            
            for i, (brand, model_count) in enumerate(sorted_by_models, 1):
                md_content += f"{i}. **{brand}** - {model_count} models\n"
            
            # Footer
            md_content += f"\n---\n\n"
            md_content += f"**Source file** : `cargurus_scraped_models_{metadata['scraped_at'].replace(':', '').replace('-', '').replace('T', '_')}.json`\n"
            md_content += f"**Generated by** : CarGurus Scraper {metadata['scraper_version']}\n"
            md_content += f"**Generation date** : {datetime.now().strftime('%m/%d/%Y at %H:%M:%S')}\n"
            
            return md_content
            
        except Exception as e:
            logger.error(f"❌ Error formatting Markdown: {e}")
            return f"# 🚗 CarGurus.com - Brands and Models\n\n**Formatting error:** {e}\n"
    
    def generate_brands_markdown_version(self, brands_data, json_file_path):
        """Generate a readable Markdown version of extracted brands."""
        try:
            # Create Markdown file path
            json_path = Path(json_file_path)
            md_file = json_path.with_suffix('.md')

            # Prepare Markdown content
            md_content = self.format_brands_as_markdown(brands_data)

            # Save Markdown file
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)

            logger.info(f"📝 Brands Markdown file generated: {md_file}")
            return str(md_file)

        except Exception as e:
            logger.error(f"❌ Error generating brands Markdown file: {e}")
            return None
    
    def format_brands_as_markdown(self, brands_data):
        """Format brand data as readable Markdown."""
        try:
            metadata = brands_data["metadata"]
            brands_list = brands_data["brands"]

            # Header
            md_content = f"""# 🚗 CarGurus.com - Available Brands List

**File generated on** : {metadata['extracted_at']}
**Source** : {metadata['source']}
**Method** : {metadata['method']}

## 📊 Statistics

- **📋 Brands extracted** : {metadata['total_brands']}
- **🔍 Source** : CarGurus.com dropdown menu

---

## 📋 Complete List of Brands

"""

            # Sort brands alphabetically
            sorted_brands = sorted(brands_list, key=lambda x: x['name'])

            # Organize in columns for better readability
            md_content += "| Brand | ID |\n"
            md_content += "|--------|----|\n"

            for brand in sorted_brands:
                md_content += f"| {brand['name']} | `{brand['id']}` |\n"

            md_content += "\n"

            # Footer
            md_content += f"\n---\n\n"
            md_content += f"**Source file** : `cargurus_brands_for_scraping.json`\n"
            md_content += f"**Generated by** : CarGurus Scraper v{metadata.get('scraper_version', '1.0')}\n"
            md_content += f"**Generation date** : {datetime.now().strftime('%m/%d/%Y at %H:%M:%S')}\n"

            return md_content

        except Exception as e:
            logger.error(f"❌ Error formatting brands Markdown: {e}")
            return f"# 🚗 CarGurus.com - Brands List\n\n**Formatting error:** {e}\n"
    
    def scrape_all_brands(self, max_brands=None):
        """Scrape all brands from JSON list."""
        try:
            if not self.navigate_to_homepage():
                return False
            
            # Determine brands to process
            brands_to_process = self.brands_list[:max_brands] if max_brands else self.brands_list
            logger.info(f"🚀 Starting scraping for {len(brands_to_process)} brands")
            
            for i, brand_info in enumerate(brands_to_process, 1):
                brand_name = brand_info["name"]
                brand_id = brand_info["id"]
                
                logger.info(f"🏷️ [{i}/{len(brands_to_process)}] {brand_name}")
                
                try:
                    models = self.scrape_brand_models(brand_name, brand_id)
                    self.brand_models_data[brand_name] = models
                    
                    if models:
                        logger.info(f"   ✅ {len(models)} models")
                    else:
                        logger.warning(f"   ⚠️ No models")
                    
                except Exception as e:
                    logger.error(f"   ❌ Error: {e}")
                    self.brand_models_data[brand_name] = []
                
                # Pause between brands (1-2 seconds)
                time.sleep(random.uniform(1, 2))
                
                # Show progress every 10 brands
                if i % 10 == 0:
                    brands_with_models = len([b for b, models in self.brand_models_data.items() if models])
                    logger.info(f"📊 Progress: {i}/{len(brands_to_process)} brands, {brands_with_models} with models")
            
            logger.info(f"🎉 Scraping complete! {len(self.brand_models_data)} brands processed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            return False
    
    def close(self):
        """Properly close the driver."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("🔒 Driver closed")

def main():
    """Main function with argument handling."""
    parser = argparse.ArgumentParser(
        description="CarGurus.com Autonomous Scraper - Extract models by brand",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples of use:
  python car_gurus_scraper.py                 # All brands (auto extraction if needed)
  python car_gurus_scraper.py --test          # Quick test (20 brands)
  python car_gurus_scraper.py --max-brands 50 # 50 brands maximum
  python car_gurus_scraper.py --headless=False # See the browser
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Test mode (20 brands only)')
    parser.add_argument('--max-brands', type=int, metavar='N',
                       help='Limit number of brands to scrape')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Headless mode (default: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                       help='Show the browser')
    
    args = parser.parse_args()
    
    # Determine parameters
    max_brands = 20 if args.test else args.max_brands
    
    logger.info("🚀 CarGurus.com Autonomous Scraper - US Market v1.0")
    logger.info(f"   • Mode: {'Test' if args.test else 'Complete'}")
    logger.info(f"   • Headless: {args.headless}")
    logger.info(f"   • Max brands: {max_brands or 'All'}")
    logger.info("   • 🚀 Automatic brand extraction if needed")
    
    try:
        scraper = CarGurusScraper(headless=args.headless)
        
        # Launch scraping
        success = scraper.scrape_all_brands(max_brands=max_brands)
        
        if success:
            output_file = scraper.save_results()
            if output_file:
                logger.info(f"🎉 SUCCESS! File generated: {output_file}")
            else:
                logger.error("❌ Error during save")
        else:
            logger.error("❌ Scraping failed")
        
    except KeyboardInterrupt:
        logger.info("⏹️ User interruption")
        if 'scraper' in locals():
            scraper.save_results()
    except Exception as e:
        logger.error(f"💥 General error: {e}")
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main()