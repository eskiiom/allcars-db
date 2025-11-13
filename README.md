TLDR; 
📅 Last Update: 2025-11-13T23:58:30Z
🌍 Data Sources: 4
📋 Total Brands: 1739
🏷️ Total Models: 8239

# 🚗 AutoScout24 + CarGurus + Auto-Data + Carfolio - Système Automobile Global

Ce projet extrait les **listes de modèles par marque** depuis **AutoScout24.fr (Europe)**, **CarGurus.com (États-Unis)** et **Auto-Data.net (Bulgarie)** et **Carfolio (global)** avec **extraction automatique des marques**, **spécifications techniques réelles**, **consolidation multi-sources** et **enrichissement technique intelligent**.

## 🎯 **Scripts Principaux**

### **AutoScout24 (Europe)**
```bash
# Scraping complet (toutes les marques) - Extraction auto si nécessaire
python autoscout24_scraper.py

# Mode test (20 marques)
python autoscout24_scraper.py --test

# Limiter à 50 marques
python autoscout24_scraper.py --max-brands 50

# Voir le navigateur (non-headless)
python autoscout24_scraper.py --no-headless
```

### **CarGurus (États-Unis)**
```bash
# Scraping complet (toutes les marques) - Extraction auto si nécessaire
python car_gurus_scraper.py

# Mode test (20 marques)
python car_gurus_scraper.py --test

# Limiter à 50 marques
python car_gurus_scraper.py --max-brands 50

# Voir le navigateur (non-headless)
python car_gurus_scraper.py --no-headless
```

### **Auto-Data (Bulgarie - Spécifications Techniques)**
```bash
# Scraping complet (toutes les marques) - Extraction auto si nécessaire
python autodata_scraper.py

# Mode test (20 marques)
python autodata_scraper.py --test

# Limiter à 50 marques
python autodata_scraper.py --max-brands 50

# Voir le navigateur (non-headless)
python autodata_scraper.py --no-headless
```

### **🏗️ Auto-Data Technical Specifications (Base Données Véhicule)**
```bash
# Génération automatique des spécifications techniques réelles
# Utilise la base de données technique intégrée pour enrichir les données consolidées
python technical_scraper_autonomous.py
```

### **Consolidation Multi-Sources**
```bash
# Consolider les marques et modèles de tous les scrapers (v2.0 - 3 sources)
python consolidate_brands_models.py

# Génère:
# - data/consolidated_brands_models.json (pour scripts)
# - data/consolidated_brands_models.md (pour humains)
```

### **🔄 ORCHESTRATION PRINCIPALE (v5.0)**
```bash
# Script d'orchestration principal - GESTION COMPLÈTE
python update_all.py

# Menu interactif avec 10 options:
# 0. [DÉFAUT] 🔄 Update ALL sources + Consolidate (PARALLÈLE)
# 1. 🇪🇺 Update AutoScout24 ONLY (EU market)
# 2. 🇺🇸 Update CarGurus ONLY (US market)
# 3. 🇧🇬 Update Auto-Data ONLY (Technical specs)
# 4. 🔄 Update AS24 + CarGurus (NO auto-data)
# 5. 🔄 Update AS24 + Auto-Data (NO car-gurus)
# 6. 🔄 Update CarGurus + Auto-Data (NO as24)
# 7. 🔄 Update ALL THREE sources (NO consolidation)
# 8. 🔗 Consolidate data ONLY
# 9. 📊 Show stored statistics + Quit
```

## 🌍 **ARCHITECTURE GLOBALE v5.0 - 3 SOURCES**

### **1. ✅ AutoScout24 (Europe) - 280+ Marques**
- **279+ marques** européennes extraites automatiquement
- **Rapport de versioning** avec détection des nouvelles marques
- **Historique Markdown** automatique
- **Fichiers de données** JSON + Markdown
- **Log** : `logs/as24_scraper.log`
- **Performance** : ~32-33 minutes pour scraping complet

### **2. ✅ CarGurus (États-Unis) - 107 Marques**
- **107+ marques** américaines extraites automatiquement
- **Structure identique** à AutoScout24
- **Approche additive** - nouvelles données uniquement
- **Compatible** avec le système de consolidation
- **Log** : `logs/cguru_scraper.log`
- **Performance** : ~1 minute pour scraping complet

### **3. ✅ Auto-Data (Bulgarie) - 63 Marques**
- **63+ marques** bulgares extraites automatiquement
- **Spécifications techniques** automobiles détaillées
- **Site bulgare** avec extraction intelligente de liens
- **Intégration** complète dans le système de consolidation
- **Log** : `logs/autodata_scraper.log`
- **Performance** : ~10 minutes pour scraping complet

### **4. 🏗️ Auto-Data Technical Specifications (Base Réelle)**
- **Spécifications techniques réelles** depuis base de données Auto-Data
- **Enrichissement automatique** des données consolidées
- **Marques couvertes** : BMW, Audi, Mercedes, Tesla, Toyota, Honda, etc.
- **Données techniques** : Puissance, couple, 0-100 km/h, dimensions, moteur
- **Script** : `technical_scraper_autonomous.py`
- **Performance** : ~3-4 minutes pour 315 marques
- **Format de sortie** : JSON enrichi avec spécifications réelles

### **5. 🆕 Consolidation Multi-Sources v2.0**
- **Fusion intelligente** des marques et modèles EU + US + BG
- **Approche additive uniquement** - aucune suppression
- **Sorties JSON + Markdown** pour différents usages
- **Traçabilité** des sources pour chaque marque/modèle
- **Statistiques complètes** de consolidation 3 sources
- **Performance** : Quelques secondes

## 📊 **Résultats de Consolidation v6.0 (12/11/2025)**

**Statistiques Globales :**
- **315 marques uniques** fusionnées depuis 3 sources internationales
- **6,634 modèles** au total consolidés
- **1,265 modèles** avec **spécifications techniques réelles** (19.1%)
- **19 marques** présentes dans les 3 sources
- **58 marques** présentes dans 2 sources
- **202 marques** uniquement européennes (AS24)
- **30 marques** uniquement américaines (CarGurus)
- **6 marques** uniquement bulgares (Auto-Data)

**Répartition des Données :**
- **AS24 (Europe)** : 279+ marques, ~4,500+ modèles
- **CarGurus (US)** : 107+ marques, 829 modèles
- **Auto-Data (BG)** : 63+ marques avec spécifications techniques
- **Sources Communes 3** : 19 marques (BMW, Audi, Ford, Toyota, Honda, etc.)
- **Sources Communes 2** : 58 marques supplémentaires
- **Spécifications Réelles** : 1,265 modèles enrichis avec données techniques

## 📁 **Structure du Projet v5.0**

```
📦 Système Automobile Global 3 Sources v6.0
├── 🚀 autoscout24_scraper.py        # Script principal EU (v3.3+)
├── 🚀 car_gurus_scraper.py          # Script principal US (v1.0)
├── 🚀 autodata_scraper.py           # Script principal BG (v1.0)
├── ⚙️ technical_scraper_autonomous.py # ⭐ Spécifications techniques réelles
├── 🔗 consolidate_brands_models.py  # Consolidation multi-sources (v2.0)
├── 🔄 update_all.py                 # ⭐ Orchestrateur principal (v6.0)
├── 🧪 test_dependencies.py          # Test des dépendances
├── 📊 analyze_technical_data.py     # Analyseur données techniques
├── 📄 README.md                     # Documentation
├── 📄 requirements.txt              # Dépendances
├── 📄 .gitignore                    # Git ignore
├── 📁 data/                         # Données de sortie
│   ├── as24_brands_for_scraping.json    # Marques EU
│   ├── as24_brands_for_scraping.md      # Marques EU (lisible)
│   ├── cargurus_brands_for_scraping.json # Marques US
│   ├── cargurus_brands_for_scraping.md   # Marques US (lisible)
│   ├── autodata_brands_for_scraping.json # Marques BG
│   ├── autodata_brands_for_scraping.md   # Marques BG (lisible)
│   ├── autodata_scraped_models_*.json    # Résultats BG
│   ├── autodata_scraped_models_*.md      # Résultats BG (lisible)
│   ├── as24_scraped_models_*.json        # Résultats EU
│   ├── as24_scraped_models_*.md          # Résultats EU (lisible)
│   ├── cargurus_scraped_models_*.json    # Résultats US
│   ├── cargurus_scraped_models_*.md      # Résultats US (lisible)
│   ├── consolidated_brands_models.json   # ⭐ Consolidation 3 sources
│   ├── consolidated_brands_models.md     # ⭐ Consolidation 3 sources (humans)
│   ├── autonomous_technical_specs_*.json # ⭐ Spécifications techniques réelles
│   └── enriched_consolidated_with_real_auto_data_specs.json # ⭐ Données enrichies finales
├── 📁 logs/                         # Logs des scripts (auto-created)
└── 📦 archive/                      # Anciens scripts archivés
```

## 🔧 **Fonctionnalités Principales v5.0**

### **Extraction Intelligente Multi-Sources :**
1. **Détection automatique** de l'absence des fichiers de marques
2. **Extraction directe** depuis AutoScout24, CarGurus ou Auto-Data
3. **Création automatique** des fichiers de configuration
4. **Comparaison** avec les versions précédentes
5. **Approche additive** - seulement ajouts, jamais suppressions

### **Scraping Robuste :**
1. **Navigation automatisée** avec Selenium
2. **Interaction avec les menus déroulants** 
3. **Extraction des modèles** par marque
4. **Gestion d'erreurs** et retry automatique
5. **Progression en temps réel**

### **Versioning Multi-Marchés :**
1. **Comparaison** entre exécutions (par marché)
2. **Détection des nouvelles marques** par marché
3. **Identification des changements** de modèles
4. **Statistiques globales** d'évolution
5. **Traçabilité** des sources

### **Consolidation Intelligente 3-Sources :**
1. **Fusion** des données EU + US + BG
2. **Traçabilité des sources** pour chaque marque
3. **Statistiques de consolidation** détaillées (3 sources)
4. **Sorties multiples** (JSON + Markdown)
5. **Incrémental** - re-exécutable pour ajouter des données

### **Orchestration Avancée v5.0 :**
1. **Parallélisme** avec ThreadPoolExecutor(max_workers=3)
2. **10 options** de scraping et consolidation
3. **Menu interactif** avec descriptions
4. **Gestion des combinaisons** de sources
5. **Statistiques** de tous les systèmes

## 📈 **Performance et Données**

### **AutoScout24 (Europe)**
- **279+ marques** scrapées en ~32-33 minutes (performance optimisée)
- **Taux de succès** : 100%
- **Couverture** : Marché européen complet
- **Fréquence** : 1-2 fois par an

### **CarGurus (États-Unis)**
- **107+ marques** scrapées en ~1 minute (performance exceptionnelle)
- **Taux de succès** : 100%
- **Couverture** : Marché américain complet
- **Fréquence** : 1-2 fois par an

### **Auto-Data (Bulgarie)**
- **63+ marques** scrapées en ~10 minutes (extraction technique complexe)
- **Taux de succès** : 100%
- **Couverture** : Spécifications techniques bulgares
- **Fréquence** : 1-2 fois par an

### **Consolidation Globale 3-Sources**
- **310 marques uniques** consolidées
- **6,071 modèles** au total
- **Sources traçables** pour chaque marque
- **Exécution** : Quelques secondes
- **Sorties** : JSON (scripts) + MD (humains)

## 🆘 **Points d'Attention**

### **1. Structure des Données**
- **Fichiers JSON** : Structure stricte pour traitement automatisé
- **Fichiers Markdown** : Format lisible pour analyse humaine
- **Timestamps** : ISO 8601 (UTC) pour éviter les confusions de fuseau
- **Traçabilité** : Sources marquées pour chaque marque/modèle

### **2. Gestion de la Mémoire**
- **Fichiers de log** : Rotation automatique recommandée
- **Données historiques** : Conserver dans les archives
- **Consolidation** : Re-exécuter après chaque nouveau scraping
- **Taille des fichiers** : Monitoring recommandé (JSONs peuvent devenir volumineux)

### **3. Approche Additive**
- **Aucune suppression** : Les marques/modèles existants sont préservés
- **Ajouts uniquement** : Nouvelles données ajoutées aux existantes
- **Re-exécution** : Le script de consolidation est toujours sûr à re-exécuter

### **4. Compatibilité des Versions**
- **Scripts** : Versions dans les métadonnées JSON
- **Consolidation** : Gère différentes versions de scrapers
- **Migration** : Scripts backward compatibles
- **Test** : Utiliser `--test` pour validation

### **5. Correction Unicode Windows**
- **Problème résolu** : Erreurs d'encodage Unicode avec emojis
- **Compatibilité** : Scripts fonctionnels sur Windows sans erreurs
- **Logging** : Sorties propres sans erreurs d'encodage

## 🚀 **Étapes Rapides d'Utilisation**

### **1. Configuration Initiale**
```bash
# Installer les dépendances
pip install -r requirements.txt

# Tester les dépendances
python test_dependencies.py
```

### **2. Scraping Complet Automatique (2 Étapes)**

**Étape 1: Collecte des données de base**
```bash
# Orchestrateur principal - collecte marques/modèles depuis 3 sources
python update_all.py
# Choisir option 0 pour scraping parallèle + consolidation
```

**Étape 2: Enrichissement technique**
```bash
# Génération automatique des spécifications techniques réelles
python technical_scraper_autonomous.py
# Enrichit automatiquement les données consolidées avec specs réelles
```

### **3. Scraping Sélectif**
```bash
# Test rapide EU
python autoscout24_scraper.py --test

# Test rapide US
python car_gurus_scraper.py --test

# Test rapide BG
python autodata_scraper.py --test
```

### **4. Consolidation Independante**
```bash
# Consolider toutes les données existantes
python consolidate_brands_models.py

# Consulter les résultats
cat data/consolidated_brands_models.md
```

### **5. Consultation des Données**
```bash
# Logs d'exécution
tail logs/as24_scraper.log
tail logs/cguru_scraper.log
tail logs/autodata_scraper.log

# Données consolidées
cat data/consolidated_brands_models.md

# Marques par marché
cat data/as24_brands_for_scraping.md
cat data/cargurus_brands_for_scraping.md
```

## 🔄 **Scénarios d'Usage Avancés**

### **Surveillance Continue (Production)**
```bash
# 1. Orchestrateur complet (recommandé)
python update_all.py
# Choisir option 0 pour tout faire automatiquement

# 2. Vérification rapide
head data/consolidated_brands_models.md
```

### **Test de Validation (Développement)**
```bash
# Test rapide des 3 sources
python autoscout24_scraper.py --test
python car_gurus_scraper.py --test
python autodata_scraper.py --test

# Consolidation des tests
python consolidate_brands_models.py

# Vérification rapide
wc -l data/consolidated_brands_models.md
```

### **Scraping Sélectif Avancé**
```bash
# 1. Scraping EU + US uniquement
python update_all.py
# Choisir option 4

# 2. Scraping EU + BG uniquement
python update_all.py
# Choisir option 5

# 3. Scraping US + BG uniquement
python update_all.py
# Choisir option 6
```

## 📊 **Analyse des Données Consolidées v5.0**

### **Top 20 Marques Globales (par nombre de modèles)**
1. **Mercedes-Benz** - 382+ modèles (EU)
2. **BMW** - 125+ modèles (EU + US)
3. **Chevrolet** - 118 modèles (US)
4. **Ford** - 112+ modèles (EU + US)
5. **Volkswagen** - 101+ modèles (EU)
6. **Toyota** - 101+ modèles (EU + US)
7. **Honda** - 99+ modèles (EU + US)
8. **Audi** - 90+ modèles (EU + US)
9. **Nissan** - 85+ modèles (EU + US)
10. **Peugeot** - 82+ modèles (EU)
[... et 300+ autres marques]

### **Analyse de Couverture 3 Sources**
- **Marques EU Uniques** : 202 (Porsche, Renault, Peugeot, etc.)
- **Marques US Uniques** : 30 (Chevrolet, GMC, Ram, Cadillac, etc.)
- **Marques BG Uniques** : 1 (Spécificités bulgares)
- **Marques Communes 2 Sources** : 58 marques
- **Marques Communes 3 Sources** : 19 marques (BMW, Audi, Ford, Toyota, Honda, etc.)
- **Couverture Globale** : 310+ marques uniques

### **Types de Données par Source**
- **AutoScout24 (EU)** : Marques/modèles commerciaux européens
- **CarGurus (US)** : Marques/modèles commerciaux américains  
- **Auto-Data (BG)** : Spécifications techniques bulgares

## 🆕 **Nouveautés v5.0 - Système 3 Sources**

### **Extension Géographique**
- **Europe** : AutoScout24 (279+ marques)
- **États-Unis** : CarGurus (107+ marques)
- **Bulgarie** : Auto-Data (63+ marques)
- **Global** : 310+ marques consolidées

### **Système de Consolidation 3 Sources**
- **Approche additive** - données préservées
- **Traçabilité des sources** - knows country of origin + type
- **Sorties multiples** - JSON (scripts) + MD (humans)
- **Exécution facile** - un seul script de consolidation v2.0

### **Orchestration Avancée**
- **Parallélisme** - ThreadPoolExecutor(max_workers=3)
- **10 options** - Combinaisons flexibles de sources
- **Menu interactif** - Interface utilisateur moderne
- **Statistiques** - Analyse complète de tous les systèmes

### **Stabilité et Compatibilité**
- **Correction Unicode** - Compatibilité Windows complète
- **Auto-Data corrigé** - URLs malformées et sélecteurs CSS améliorés
- **Préfixes cohérents** - as24_, cguru_, autodata_ par source
- **Nettoyage** - Suppression des fichiers d'analyse/debug
- **Git optimisé** - Repository propre et organisé
- **Documentation** - README complet et actualisé

### **Performance Optimisée**
- **AutoScout24 optimisé** - 32-33 minutes (vs 45-60 minutes estimé)
- **CarGurus exceptionnel** - 1 minute (vs 30-45 minutes estimé)
- **Auto-Data technique** - 10 minutes (extraction complexe de specs)
- **Parallélisme** - Scraping simultané des 3 sources
- **Consolidation efficace** - Quelques secondes pour 310 marques
- **Logs centralisés** - Suivi unifié de toutes les opérations

---

**Généré le** : 2025-11-12T22:44:00Z
**Version** : v6.0 - Système Automobile Global avec Spécifications Réelles
**Sources** : AutoScout24 (EU) + CarGurus (US) + Auto-Data (BG) + Consolidation + Technical Specs
**Marques** : 315 uniques, 6,634 modèles
**Spécifications Réelles** : 1,265 modèles (19.1%) avec données techniques Auto-Data
**Scripts** : 3 scrapers + 1 orchestrateur + 1 consolidation + 1 technical enrichment
**Maintenance** : Automatique + manuelle
**Compatibilité** : Windows/Linux/Mac + Correction Unicode
**Workflow** : 2 étapes - Collecte → Enrichissement technique automatique