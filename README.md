# 🚗 AutoScout24 + CarGurus Scraper - Système Automobile Global

Ce projet extrait les **listes de modèles par marque** depuis **AutoScout24.fr (Europe)** et **CarGurus.com (États-Unis)** avec **extraction automatique des marques**, **rapport de versioning**, **historique détaillé**, **fichiers de données en format Markdown** et **consolidation multi-sources**.

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

### **Consolidation Multi-Sources**
```bash
# Consolider les marques et modèles de tous les scrapers
python consolidate_brands_models.py

# Génère:
# - data/consolidated_brands_models.json (pour scripts)
# - data/consolidated_brands_models.md (pour humains)
```

### **🔄 ORCHESTRATION PRINCIPALE (NOUVEAU!)**
```bash
# Script d'orchestration principal - GESTION COMPLÈTE
python update_all.py

# Menu interactif avec 6 options:
# 0. [DÉFAUT] 🔄 Mettre à jour TOUS + Consolider (PARALLÈLE)
# 1. 🇪🇺 AutoScout24 UNIQUEMENT (marché EU)
# 2. 🇺🇸 CarGurus UNIQUEMENT (marché US)
# 3. 🔄 Les 2 sources SANS consolidation
# 4. 🔗 Consolider UNIQUEMENT
# 9. 📊 Afficher stats stockées + Quitter
```

## 🌍 **NOUVELLE ARCHITECTURE GLOBALE v4.0**

### **1. ✅ AutoScout24 (Europe) - 280+ Marques**
- **279+ marques** européennes extraites automatiquement
- **Rapport de versioning** avec détection des nouvelles marques
- **Historique Markdown** automatique
- **Fichiers de données** JSON + Markdown
- **Log** : `logs/as24_scraper.log`

### **2. ✅ CarGurus (États-Unis) - 107 Marques**
- **107+ marques** américaines extraites automatiquement
- **Structure identique** à AutoScout24
- **Approche additive** - nouvelles données uniquement
- **Compatible** avec le système de consolidation
- **Log** : `logs/cguru_scraper.log`

### **3. 🆕 Consolidation Multi-Sources**
- **Fusion intelligente** des marques et modèles EU + US
- **Approche additive uniquement** - aucune suppression
- **Sorties JSON + Markdown** pour différents usages
- **Traçabilité** des sources pour chaque marque/modèle
- **Statistiques complètes** de consolidation

## 📊 **Résultats de Consolidation (10/11/2025)**

**Statistiques Globales :**
- **280 marques uniques** fusionnées
- **5,412 modèles** au total
- **19 marques** présentes dans les 2 sources (EU + US)
- **260 marques** uniquement européennes (AS24)
- **1 marque** uniquement américaine (CarGurus)

**Répartition des Données :**
- **AS24 (Europe)** : 280 marques, ~4,500+ modèles
- **CarGurus (US)** : 107 marques, 829 modèles
- **Sources Communes** : 19 marques (BMW, Audi, Ford, Toyota, etc.)

## 📁 **Structure du Projet Actuelle**

```
📦 Système Automobile Global
├── 🚀 autoscout24_scraper.py        # Script principal EU (v3.3+)
├── 🚀 car_gurus_scraper.py          # Script principal US (v1.0)
├── 🔗 consolidate_brands_models.py  # Consolidation multi-sources
├── 🔄 update_all.py                 # ⭐ Script d'orchestration principal
├── 📄 generate_brands_md.py         # Générateur Markdown marques
├── 📄 test_dependencies.py          # Test des dépendances
├── 📄 README.md                     # Documentation
├── 📄 requirements.txt              # Dépendances
├── 📄 .gitignore                    # Git ignore
├── 📁 logs/                         # Logs des scripts
│   ├── as24_scraper.log            # Log AutoScout24
│   └── cguru_scraper.log           # Log CarGurus
├── 📁 data/                         # Données de sortie
│   ├── as24_brands_for_scraping.json    # Marques EU
│   ├── as24_brands_for_scraping.md      # Marques EU (lisible)
│   ├── cargurus_brands_for_scraping.json # Marques US
│   ├── cargurus_brands_for_scraping.md   # Marques US (lisible)
│   ├── as24_scraped_models_*.json        # Résultats EU
│   ├── as24_scraped_models_*.md          # Résultats EU (lisible)
│   ├── cargurus_scraped_models_*.json    # Résultats US
│   ├── cargurus_scraped_models_*.md      # Résultats US (lisible)
│   ├── consolidated_brands_models.json   # ⭐ Consolidation (scripts)
│   ├── consolidated_brands_models.md     # ⭐ Consolidation (humains)
│   └── 📁 journal/                       # Historique détaillé
│       ├── as24_*_executions.json        # Exécutions EU détaillées
│       └── cguru_*_executions.json       # Exécutions US détaillées
├── 📁 docs/                         # Documentation
│   ├── execution_history.md         # Historique AutoScout24
│   └── cars_execution_history.md    # Historique CarGurus
└── 🏗️ archive/                      # Anciens scripts et fichiers
```

## 🔧 **Fonctionnalités Principales**

### **Extraction Intelligente Multi-Sources :**
1. **Détection automatique** de l'absence des fichiers de marques
2. **Extraction directe** depuis AutoScout24 ou CarGurus
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

### **Consolidation Intelligente :**
1. **Fusion** des données EU + US
2. **Traçabilité des sources** pour chaque marque
3. **Statistiques de consolidation** détaillées
4. **Sorties multiples** (JSON + Markdown)
5. **Incrémental** - re-exécutable pour ajouter des données

## 📈 **Performance et Données**

### **AutoScout24 (Europe)**
- **279+ marques** scrapées en ~45-60 minutes
- **Taux de succès** : 100%
- **Couverture** : Marché européen complet
- **Fréquence** : 1-2 fois par an

### **CarGurus (États-Unis)**  
- **107+ marques** scrapées en ~30-45 minutes
- **Taux de succès** : 100%
- **Couverture** : Marché américain complet
- **Fréquence** : 1-2 fois par an

### **Consolidation Globale**
- **280 marques uniques** consolidées
- **5,412 modèles** au total
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
- **Données historiques** : Conserver dans `data/journal/`
- **Consolidation** : Re-exécuter après chaque nouveau scraping
- **Taille des fichiers** : Monitoring recommandé (JSONs peuvent devenir volumineux)

### **3. Approche Additive**
- **Aucune suppression** : Les marques/modèles existants sont préservés
- **Ajouts uniquement** : Nouvelles données ajoutées aux existantes
- **Re-exécution** : Le script de consolidation est toujours sûr à re-exécuter
- **Historique** : Préservé dans `data/journal/`

### **4. Compatibilité des Versions**
- **Scripts** : Versions dans les métadonnées JSON
- **Consolidation** : Gère différentes versions de scrapers
- **Migration** : Scripts backward compatibles
- **Test** : Utiliser `--test` pour validation

### **5. Monitoring et Alertes**
- **Logs** : Consultation régulière recommandée
- **Statistiques** : Vérification après chaque exécution
- **Consolidation** : Comparaison des totaux entre sources
- **Anomalies** : Marques absentes d'une source habituelle

## 🚀 **Étapes Rapides d'Utilisation**

### **1. Configuration Initiale**
```bash
# Installer les dépendances
pip install -r requirements.txt

# Tester les dépendances
python test_dependencies.py
```

### **2. Scraping EU (AutoScout24)**
```bash
# Test rapide EU
python autoscout24_scraper.py --test

# Scraping complet EU
python autoscout24_scraper.py
```

### **3. Scraping US (CarGurus)**
```bash
# Test rapide US
python car_gurus_scraper.py --test

# Scraping complet US
python car_gurus_scraper.py
```

### **4. Consolidation Globale**
```bash
# Consolider toutes les données
python consolidate_brands_models.py

# Consulter les résultats
cat data/consolidated_brands_models.md
```

### **5. Consultation des Données**
```bash
# Logs d'exécution
tail logs/as24_scraper.log
tail logs/cguru_scraper.log

# Données consolidées
cat data/consolidated_brands_models.md

# Marques par marché
cat data/as24_brands_for_scraping.md
cat data/cargurus_brands_for_scraping.md
```

## 🔄 **Scénarios d'Usage Avancés**

### **Surveillance Continue (Production)**
```bash
# 1. Scraping complet EU
python autoscout24_scraper.py

# 2. Scraping complet US  
python car_gurus_scraper.py

# 3. Consolidation avec versioning
python consolidate_brands_models.py

# 4. Vérification des résultats
head data/consolidated_brands_models.md
```

### **Test de Validation (Développement)**
```bash
# Test rapide EU + US
python autoscout24_scraper.py --test
python car_gurus_scraper.py --test

# Consolidation des tests
python consolidate_brands_models.py

# Vérification rapide
wc -l data/consolidated_brands_models.md
```

### **Migration ou Mise à Jour**
```bash
# Sauvegarder les données existantes
cp -r data/ data_backup_$(date +%Y%m%d)/

# Nouveau scraping avec consolidation
python autoscout24_scraper.py
python car_gurus_scraper.py  
python consolidate_brands_models.py

# Comparer les statistiques
head data/consolidated_brands_models.md
```

## 📊 **Analyse des Données Consolidées**

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
[... et 270+ autres marques]

### **Marques Présentes dans les 2 Sources (19 marques)**
- **BMW, Audi, Ford, Toyota, Honda, Nissan, Volkswagen, Mercedes-Benz, Kia, Hyundai, INFINITI, Jaguar, Jeep, Cadillac, GMC, Ram, Subaru, Tesla, Volvo**

### **Analyse de Couverture**
- **Marques EU Uniques** : 260 (Porsche, Renault, Peugeot, etc.)
- **Marques US Uniques** : 1 (Abarth)
- **Marques Communes** : 19 (grandes marques internationales)
- **Couverture Globale** : 280+ marques uniques

## 🆕 **Nouveautés v4.0 - Système Global**

### **Extension Géographique**
- **Europe** : AutoScout24 (279+ marques)
- **États-Unis** : CarGurus (107+ marques)
- **Global** : 280+ marques consolidées

### **Système de Consolidation**
- **Approche additive** - données préservées
- **Traçabilité des sources** - knows country of origin
- **Sorties multiples** - JSON (scripts) + MD (humans)
- **Exécution facile** - un seul script de consolidation

### **Organisation des Fichiers**
- **Logs séparés** - par script dans `logs/`
- **Données structurées** - préfixes par source
- **Journal historique** - dans `data/journal/`
- **Consolidation centrale** - `data/consolidated_*`

### **Documentation Complète**
- **Historique d'exécution** - par script
- **Statistiques de consolidation** - détaillées
- **Points d'attention** - pour maintenance
- **Scénarios d'usage** - exemples concrets

---

**Généré le** : 2025-11-10T20:46:00Z  
**Version** : v4.0 - Système Automobile Global  
**Sources** : AutoScout24 (EU) + CarGurus (US) + Consolidation  
**Marques** : 280+ uniques, 5,412+ modèles  
**Scripts** : 3 principaux + utilitaires  
**Maintenance** : Automatique + manuelle  