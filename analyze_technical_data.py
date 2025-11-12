#!/usr/bin/env python3
"""
Utilitaire d'analyse des données techniques Auto-Data
Analyse et structure les spécifications pour intégration site web
"""

import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse

class TechnicalDataAnalyzer:
    """Analyseur pour données techniques Auto-Data."""
    
    def __init__(self, technical_data_file):
        """Initialise avec un fichier de données techniques."""
        self.data_file = Path(technical_data_file)
        self.data = self.load_technical_data()
        self.analysis_results = {}
    
    def load_technical_data(self):
        """Charge les données techniques depuis le fichier JSON."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Données chargées: {len(data.get('brands_technical_data', {}))} marques")
            return data
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return {}
    
    def analyze_data_coverage(self):
        """Analyse la couverture des données par catégorie."""
        print("\n📊 ANALYSE DE COUVERTURE DES DONNÉES")
        print("=" * 50)
        
        coverage_stats = {
            'total_brands': len(self.data.get('brands_technical_data', {})),
            'total_models': 0,
            'categories_coverage': {
                'basic': {'brands': 0, 'models': 0},
                'performance': {'brands': 0, 'models': 0},
                'dimensions': {'brands': 0, 'models': 0},
                'engine': {'brands': 0, 'models': 0},
                'transmission': {'brands': 0, 'models': 0},
                'equipment': {'brands': 0, 'models': 0}
            }
        }
        
        for brand_name, brand_data in self.data.get('brands_technical_data', {}).items():
            models_count = brand_data.get('scraped_models', 0)
            coverage_stats['total_models'] += models_count
            
            if models_count > 0:
                for model_name, model_data in brand_data.get('models', {}).items():
                    specs = model_data.get('specifications', {})
                    
                    # Compter les catégories avec des données
                    for category in coverage_stats['categories_coverage'].keys():
                        if specs.get(category) and len(specs[category]) > 0:
                            coverage_stats['categories_coverage'][category]['models'] += 1
                            break
                    else:
                        # Si aucune catégorie avec données, passer à la suivante
                        continue
                
                # Comptage des marques par catégorie (au moins un modèle avec données)
                for category in coverage_stats['categories_coverage'].keys():
                    has_data_in_brand = False
                    for model_name, model_data in brand_data.get('models', {}).items():
                        specs = model_data.get('specifications', {})
                        if specs.get(category) and len(specs[category]) > 0:
                            has_data_in_brand = True
                            break
                    
                    if has_data_in_brand:
                        coverage_stats['categories_coverage'][category]['brands'] += 1
        
        # Affichage des résultats
        print(f"📋 Marques totales: {coverage_stats['total_brands']}")
        print(f"🚗 Modèles traités: {coverage_stats['total_models']}")
        print("\n📈 Couverture par catégorie:")
        
        for category, stats in coverage_stats['categories_coverage'].items():
            brand_pct = (stats['brands'] / coverage_stats['total_brands'] * 100) if coverage_stats['total_brands'] > 0 else 0
            model_pct = (stats['models'] / coverage_stats['total_models'] * 100) if coverage_stats['total_models'] > 0 else 0
            
            category_names = {
                'basic': 'Spécifications de base',
                'performance': 'Performance', 
                'dimensions': 'Dimensions',
                'engine': 'Moteur',
                'transmission': 'Transmission',
                'equipment': 'Équipements'
            }
            
            print(f"   {category_names[category]:<20} : {brand_pct:5.1f}% marques, {model_pct:5.1f}% modèles")
        
        self.analysis_results['coverage'] = coverage_stats
        return coverage_stats
    
    def find_most_complete_models(self, min_categories=3):
        """Trouve les modèles avec le plus de spécifications complètes."""
        print(f"\n🔍 MODÈLES LES PLUS COMPLETS (≥{min_categories} catégories)")
        print("=" * 60)
        
        complete_models = []
        
        for brand_name, brand_data in self.data.get('brands_technical_data', {}).items():
            for model_name, model_data in brand_data.get('models', {}).items():
                specs = model_data.get('specifications', {})
                
                # Compter les catégories avec des données
                filled_categories = 0
                categories_details = {}
                
                for category, data in specs.items():
                    if data and len(data) > 0:
                        filled_categories += 1
                        categories_details[category] = len(data)
                
                if filled_categories >= min_categories:
                    complete_models.append({
                        'brand': brand_name,
                        'model': model_name,
                        'categories_count': filled_categories,
                        'categories_details': categories_details,
                        'url': model_data.get('url', '')
                    })
        
        # Trier par nombre de catégories (décroissant)
        complete_models.sort(key=lambda x: x['categories_count'], reverse=True)
        
        # Afficher le top 20
        print(f"Top {min(20, len(complete_models))} modèles les plus complets:")
        
        for i, model in enumerate(complete_models[:20], 1):
            print(f"\n{i:2d}. {model['brand']} {model['model']} ({model['categories_count']} catégories)")
            for category, count in model['categories_details'].items():
                print(f"    • {category}: {count} spécifications")
        
        self.analysis_results['complete_models'] = complete_models[:20]
        return complete_models[:20]
    
    def generate_web_ready_data(self):
        """Génère des données prêtes pour le site web."""
        print("\n🌐 GÉNÉRATION DONNÉES PRÊTES POUR WEB")
        print("=" * 50)
        
        web_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source': 'Auto-Data Technical Specifications',
                'total_brands': len(self.data.get('brands_technical_data', {})),
                'total_models': sum(
                    brand.get('scraped_models', 0) 
                    for brand in self.data.get('brands_technical_data', {}).values()
                )
            },
            'brands': []
        }
        
        # Traiter chaque marque
        for brand_name, brand_data in self.data.get('brands_technical_data', {}).items():
            brand_entry = {
                'name': brand_name,
                'models': []
            }
            
            for model_name, model_data in brand_data.get('models', {}).items():
                specs = model_data.get('specifications', {})
                
                # Structurer les specs pour le web
                web_specs = {
                    'basic': specs.get('basic', {}),
                    'performance': specs.get('performance', {}),
                    'dimensions': specs.get('dimensions', {}),
                    'engine': specs.get('engine', {}),
                    'transmission': specs.get('transmission', {}),
                }
                
                # Filtrer les spécifications vides
                web_specs = {k: v for k, v in web_specs.items() if v}
                
                model_entry = {
                    'name': model_name,
                    'specifications': web_specs,
                    'source_url': model_data.get('url', ''),
                    'last_updated': model_data.get('scraped_at', '')
                }
                
                # N'ajouter que les modèles avec au moins des specs de base
                if web_specs:
                    brand_entry['models'].append(model_entry)
            
            # N'ajouter que les marques avec des modèles
            if brand_entry['models']:
                web_data['brands'].append(brand_entry)
        
        # Trier les marques et modèles
        web_data['brands'].sort(key=lambda x: x['name'])
        for brand in web_data['brands']:
            brand['models'].sort(key=lambda x: x['name'])
        
        print(f"✅ {len(web_data['brands'])} marques prêtes pour le web")
        total_models = sum(len(brand['models']) for brand in web_data['brands'])
        print(f"✅ {total_models} modèles avec spécifications")
        
        # Sauvegarder
        output_file = Path("data/autodata_web_ready.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(web_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Fichier web-ready sauvegardé: {output_file}")
        
        # Générer aussi un CSV pour analyse
        self.generate_web_csv(web_data, "data/autodata_web_ready.csv")
        
        self.analysis_results['web_ready'] = web_data
        return web_data
    
    def generate_web_csv(self, web_data, csv_file):
        """Génère un CSV structuré pour le web."""
        try:
            rows = []
            
            for brand in web_data['brands']:
                for model in brand['models']:
                    row = {
                        'brand': brand['name'],
                        'model': model['name'],
                        'source_url': model['source_url']
                    }
                    
                    # Aplatir les spécifications
                    all_specs = {}
                    for category, specs in model['specifications'].items():
                        if isinstance(specs, dict):
                            for spec_name, spec_value in specs.items():
                                row[f'{category}_{spec_name}'] = spec_value
                    
                    rows.append(row)
            
            # Créer le DataFrame et sauvegarder
            df = pd.DataFrame(rows)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
            print(f"📊 CSV web-ready généré: {csv_file} ({len(rows)} lignes)")
            
        except Exception as e:
            print(f"❌ Erreur génération CSV: {e}")
    
    def generate_website_integration_guide(self):
        """Génère un guide d'intégration pour le site web."""
        guide_content = """# Guide d'Intégration - Données Techniques Auto-Data

## 📁 Structure des Données

### Fichiers Générés
- `autodata_web_ready.json` : Données structurées pour l'intégration web
- `autodata_web_ready.csv` : Données tabulaires pour analyse

### Structure JSON
```json
{
  "metadata": {
    "generated_at": "2025-11-12T08:20:00Z",
    "total_brands": 50,
    "total_models": 500
  },
  "brands": [
    {
      "name": "BMW",
      "models": [
        {
          "name": "320i",
          "specifications": {
            "basic": {
              "years": "2019-2023",
              "fuel_type": "Essence"
            },
            "performance": {
              "power_hp": "184 ch",
              "acceleration_0_100": "7.3 s"
            },
            "dimensions": {
              "length": "4709 mm",
              "weight": "1490 kg"
            }
          },
          "source_url": "https://www.auto-data.net/..."
        }
      ]
    }
  ]
}
```

## 🚗 Intégration Site de Suivi Véhicule

### 1. Base de Données de Référence
```sql
-- Table des marques
CREATE TABLE vehicle_brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des modèles
CREATE TABLE vehicle_models (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES vehicle_brands(id),
    name VARCHAR(200) NOT NULL,
    specifications JSONB,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(brand_id, name)
);
```

### 2. API Endpoints Suggérés
```
GET /api/brands                    # Liste des marques
GET /api/brands/{brand_id}/models  # Modèles d'une marque
GET /api/models/{model_id}         # Spécifications d'un modèle
```

### 3. Interface Utilisateur
```javascript
// Sélection déroulante marque
const brands = await fetch('/api/brands').then(r => r.json());
const brandSelect = document.getElementById('brand-select');
brands.forEach(brand => {
    const option = document.createElement('option');
    option.value = brand.id;
    option.textContent = brand.name;
    brandSelect.appendChild(option);
});

// Sélection déroulante modèle basée sur la marque
brandSelect.addEventListener('change', async (e) => {
    const models = await fetch(`/api/brands/${e.target.value}/models`).then(r => r.json());
    // Remplir le select des modèles
});
```

## 📊 Données Disponibles par Catégorie

### Spécifications de Base
- Années de production
- Type de carburant
- Nombre de portes
- Nombre de places

### Performance
- Puissance (kW et ch)
- Couple (Nm)
- Accélération 0-100 km/h
- Vitesse maximale
- Consommation mixte

### Dimensions
- Longueur, Largeur, Hauteur (mm)
- Poids (kg)
- Volume du coffre (l)
- Capacité du réservoir (l)

### Moteur
- Cylindrée (cm³)
- Type de moteur
- Nombre de cylindres
- Nombre de soupapes
- Taux de compression

### Transmission
- Boîte de vitesses
- Type de traction
- Nombre de vitesses

## 🔧 Utilisation Pratique

### 1. Recherche de Véhicule
L'utilisateur sélectionne une marque → les modèles se chargent → les spécifications s'affichent.

### 2. Comparaison de Véhicules
Plusieurs véhicules peuvent être comparés en côte à côte.

### 3. Statistiques Personnalisées
Les spécifications peuvent être utilisées pour générer des statistiques d'usage basées sur le type de véhicule.

## 📈 Métriques pour Suivi de Dépenses

### Consommation (l/100km)
- Calcul du coût carburant par trajet
- Comparaison efficacité énergétique

### Puissance (ch/kW)
- Estimation des coûts d'assurance
- Impact sur la consommation

### Type de Carburant
- Différenciation des coûts (Essence vs Diesel vs Électrique)

### Dimensions/Poids
- Frais de parking, péages
- Consommation réelle

---
*Guide généré automatiquement depuis les données Auto-Data*
"""
        
        guide_file = Path("docs/autodata_web_integration_guide.md")
        guide_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"📚 Guide d'intégration généré: {guide_file}")
    
    def run_full_analysis(self):
        """Lance une analyse complète."""
        print("🔍 ANALYSE COMPLÈTE DES DONNÉES TECHNIQUES")
        print("=" * 55)
        
        # Couverture des données
        self.analyze_data_coverage()
        
        # Modèles les plus complets
        self.find_most_complete_models()
        
        # Données prêtes pour le web
        self.generate_web_ready_data()
        
        # Guide d'intégration
        self.generate_website_integration_guide()
        
        # Résumé final
        print("\n🏆 ANALYSE TERMINÉE")
        print("=" * 25)
        print("📁 Fichiers générés:")
        print("   • data/autodata_web_ready.json (données web)")
        print("   • data/autodata_web_ready.csv (analyse)")
        print("   • docs/autodata_web_integration_guide.md (guide)")
        print("\n✅ Prêt pour intégration dans le site de suivi!")

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Analyseur de données techniques Auto-Data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('data_file', nargs='?', 
                       help='Fichier de données techniques (JSON)')
    parser.add_argument('--popular', action='store_true',
                       help='Analyser seulement les marques populaires')
    
    args = parser.parse_args()
    
    # Chercher le fichier le plus récent si non spécifié
    if not args.data_file:
        data_dir = Path("data")
        tech_files = list(data_dir.glob("autodata_technical_specs_*.json"))
        
        if tech_files:
            latest_file = max(tech_files, key=lambda x: x.stat().st_mtime)
            args.data_file = str(latest_file)
            print(f"📁 Fichier détecté: {latest_file}")
        else:
            print("❌ Aucun fichier de données techniques trouvé")
            print("💡 Utilisez d'abord: python autodata_technical_scraper.py --popular-brands")
            return
    
    # Lancer l'analyse
    analyzer = TechnicalDataAnalyzer(args.data_file)
    
    if analyzer.data:
        analyzer.run_full_analysis()
    else:
        print("❌ Impossible de charger les données")

if __name__ == "__main__":
    main()