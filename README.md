# 🚗 AutoScout24 Scraper - Version Autonome v3.3 avec Historique et Markdown

Ce projet extrait les **listes de modèles par marque** depuis AutoScout24.fr avec **extraction automatique des marques**, **rapport de versioning**, **historique détaillé en Markdown** et **fichiers de données en format Markdown lisible**.

## 🎯 **Script Principal Autonome**

### Utilisation Simple
```bash
# Scraping complet (toutes les marques) - Extraction auto si nécessaire
python autoscout24_scraper.py

# Mode test (20 marques)
python autoscout24_scraper.py --test

# Limiter à 50 marques
python autoscout24_scraper.py --max-brands 50

# Voir le navigateur (non-headless)
python autoscout24_scraper.py --no-headless

# Aide
python autoscout24_scraper.py --help
```

### Prérequis
- **Chrome/Chromium** installé
- **Dépendances** : `selenium`

## 🚀 **NOUVELLES FONCTIONNALITÉS v3.3**

### **1. Extraction Automatique des Marques ✅**
- Le script **détecte automatiquement** l'absence du fichier `brands_for_scraping.json`
- **Extrait les marques** directement depuis AutoScout24 si nécessaire
- **Crée le fichier** `brands_for_scraping.json` automatiquement
- **Plus besoin** de gérer manuellement la liste des marques

### **2. Rapport de Versioning Complet ✅**
- **Détecte les nouvelles marques** ajoutées sur AutoScout24
- **Identifie les marques supprimées** 
- **Analyse les changements de modèles** par marque
- **Rapport détaillé** à la fin de chaque exécution

### **3. 🆕 Historique Markdown Automatique ✅**
- **Génère automatiquement** un fichier `docs/execution_history.md`
- **Traçabilité complète** de toutes les exécutions
- **Comparaison versionnée** avec les exécutions précédentes
- **Top 10 des marques** par nombre de modèles
- **Détail des nouvelles marques** en mode test

### **4. 🆕 🆕 Fichiers Markdown de Données Automatiques ✅**
- **Génère automatiquement** un fichier `.md` lisible pour chaque dataset
- **Format Markdown structuré** avec tableaux et organisation claire
- **Statistiques globales** et métadonnées
- **Top 15 des marques** par nombre de modèles
- **Répartition détaillée** du nombre de modèles par marque
- **🆕 Partie détaillées des nouvelles marques** (en mode test)

### **5. Surveillance Automatique ✅**
- **Première exécution** : Extrait toutes les marques, pas de comparaison
- **Exécutions suivantes** : Compare avec la version précédente
- **Alerte sur les changements** : Nouvelles marques, marques supprimées
- **Statistiques détaillées** : Évolution du nombre de modèles

## 📊 **Exemple de Fichiers Générés**

### **Fichier JSON (auto_scraped_models_20251108_001510.json)**
```json
{
  "metadata": {
    "scraped_at": "2025-11-08T00:15:10Z",
    "scraper_version": "v3.3_autonomous_with_history_and_markdown",
    "source": "AutoScout24.fr Auto Scraping",
    "method": "selenium_dynamic_dropdown_interaction",
    "total_brands": 20,
    "total_models": 1179
  },
  "brands_models": {
    "Audi": ["A1", "A3", "A4", ...],
    "BMW": ["1 Series", "2 Series", "3 Series", ...]
  }
}
```

### **🆕 Fichier Markdown (auto_scraped_models_20251108_001510.md)**
```markdown
# 🚗 AutoScout24 - Marques et Modèles

**Fichier généré le** : 2025-11-08T00:15:10Z
**Scraper** : v3.3_autonomous_with_history_and_markdown
**Source** : AutoScout24.fr Auto Scraping
**Méthode** : selenium_dynamic_dropdown_interaction

## 📊 Statistiques Globales

- **📋 Marques traitées** : 20
- **✅ Marques avec modèles** : 20
- **❌ Marques sans modèles** : 0
- **🏷️ Total modèles** : 1179

---

## 📋 Liste Complète des Marques et Modèles

### Audi

**65 modèles** :

| Colonne 1 | Colonne 2 | Colonne 3 |
|-----------|-----------|-----------|
| A1 | A2 | A3 |
| A4 | A4 allroad | A5 |
| A6 | A6 allroad | A6 e-tron |

### BMW

**125 modèles** :

| Colonne 1 | Colonne 2 | Colonne 3 |
|-----------|-----------|-----------|
| Série 1 (tous) | 114 | 116 |
| 118 | 120 | 123 |
| 125 | 128 | 130 |

## 🏆 Top 15 Marques (par nombre de modèles)

1. **Mercedes-Benz** - 382 modèles
2. **BMW** - 125 modèles
3. **Volkswagen** - 129 modèles
4. **Toyota** - 101 modèles
5. **Renault** - 65 modèles

## 📈 Répartition du Nombre de Modèles

- **50+ modèles** : 5 marques
- **20-49 modèles** : 8 marques
- **10-19 modèles** : 12 marques
- **5-9 modèles** : 15 marques

---

```

### **🆕 Fichier Markdown des Marques (brands_for_scraping.md)**
```markdown
# 🚗 AutoScout24 - Liste des Marques Disponibles

**Fichier généré le** : 2025-11-08T00:15:10Z
**Source** : AutoScout24.fr Auto Extraction
**Méthode** : selenium_dropdown_analysis

## 📊 Statistiques

- **📋 Marques extraites** : 279
- **🔍 Provenance** : Menu déroulant AutoScout24.fr

---

## 📋 Liste Complète des Marques

| Marque | ID |
|--------|----|
| 9ff | `9ff` |
| AC | `ac` |
| ACM | `acm` |
| Abarth | `abarth` |
| Acura | `acura` |
| ... | ... |

## 📈 Analyse des Marques

### Répartition par Première Lettre

- **A** : 45 marques
- **B** : 32 marques
- **C** : 18 marques
- **D** : 12 marques
- **E** : 8 marques
- **F** : 15 marques
- **G** : 12 marques
- **H** : 9 marques
- **I** : 8 marques
- **J** : 7 marques
- **K** : 8 marques
- **L** : 15 marques
- **M** : 18 marques
- **N** : 6 marques
- **O** : 4 marques
- **P** : 12 marques
- **Q** : 2 marques
- **R** : 10 marques
- **S** : 18 marques
- **T** : 12 marques
- **U** : 3 marques
- **V** : 9 marques
- **W** : 6 marques
- **X** : 3 marques
- **Y** : 2 marques
- **Z** : 5 marques

### Marques avec Noms les Plus Longs

- **Angelelli Automobili** (21 caractères)
- **Caravans-Wohnm** (15 caractères)
- **DR Automobiles** (14 caractères)
- **GTA** (3 caractères)
- **HUMMER** (6 caractères)
- **Iveco** (5 caractères)
- **Jensen** (6 caractères)
- **Koenigsegg** (10 caractères)
- **Lamborghini** (11 caractères)
- **Maserati** (8 caractères)

---

**Fichier source** : `brands_for_scraping.json`
**Généré par** : AutoScout24 Scraper v3.3
**Date de génération** : 08/11/2025 à 00:15:10
```
### **📄 Historique d'exécutions (docs/execution_history.md)**
```markdown
# 📊 AutoScout24 Scraper - Historique des Exécutions

## 📅 08/11/2025 à 00:15

**Fichier de données** : `auto_scraped_models_20251108_001510.json`  
**Scraper** : v3.3_autonomous_with_history_and_markdown  
**Méthode** : selenium_dynamic_dropdown_interaction  

### 📊 Statistiques

- **Marques traitées** : 20
- **Total modèles** : 1179

---
```

## 📁 **Structure du Projet **

```
📦 Projet Nettoyé
├── 🚀 autoscout24_scraper.py        # Script principal autonome v3.3
├── 📄 README.md                     # Documentation
├── 📄 requirements.txt              # Dépendances
├── 📄 .gitignore                    # Git ignore
├── 🆕 generate_brands_md.py         # 🆕 Génère la version Markdown des marques
├── 📁 data/                         # Données de sortie
│   ├── brands_for_scraping.json     # ⭐ Auto-généré (extraction auto)
│   ├── brands_for_scraping.md       # 🆕 Liste des marques en format lisible
│   ├── auto_scraped_models_*.json   # Résultats JSON du scraping
│   └── auto_scraped_models_*.md     # 🆕 Résultats MD (format lisible)
├── 📁 docs/                         # Documentation et historique
│   └── execution_history.md         # Historique des exécutions
└── 📁 logs/                         # Fichiers de log (généré)
    └── scraper.log                  # Log détaillé d'exécution
```

## 🔧 **Fonctionnalités Principales**

### **Extraction Intelligente :**
1. **Détection automatique** de l'absence du fichier des marques
2. **Extraction directe** depuis AutoScout24
3. **Création automatique** du fichier `brands_for_scraping.json`
4. **Comparaison avec la version précédente** si elle existe

### **Scraping Robuste :**
1. **Navigation automatisée** avec Selenium
2. **Interaction avec les menus déroulants** AutoScout24
3. **Extraction des modèles** par marque
4. **Gestion d'erreurs** et retry automatique
5. **Progression en temps réel**

### **Versioning Avancé :**
1. **Rapport de comparaison** avec la version précédente
2. **Détection des nouvelles marques** ajoutées
3. **Identification des marques supprimées**
4. **Analyse des changements de modèles** significatifs
5. **Statistiques globales** d'évolution

### **🆕 Historique Markdown :**
1. **Génération automatique** de `docs/execution_history.md`
2. **Traçabilité complète** de toutes les exécutions
3. **Format lisible** avec emojis et structure claire
4. **Top 10 des marques** par nombre de modèles
5. **Détail des nouvelles marques** et leurs modèles

### **🆕 Fichiers de Données en Markdown :**
1. **Génération automatique** d'un fichier `.md` par dataset
2. **Format structuré** avec tableaux et organisation claire
3. **Statistiques globales** et métadonnées détaillées
4. **Top 15 des marques** par nombre de modèles
5. **Répartition** du nombre de modèles par marque
6. **Partie détaillée** des nouvelles marques (en mode test)

### **🆕 Script de Génération Markdown des Marques :**
1. **`generate_brands_md.py`** : Génère `brands_for_scraping.md` depuis `brands_for_scraping.json`
2. **Format lisible** avec tableau des marques et IDs
3. **Analyse statistique** : Répartition par première lettre
4. **Top marques** par longueur de nom
5. **Utilisation** : `python generate_brands_md.py`

### **Logging Structuré :**
1. **Console + fichier** `scraper.log`
2. **Rapports détaillés** en temps réel
3. **Progression** tous les 10 marques
4. **Erreurs contextuelles** pour debugging
5. **Historique détaillé** en format Markdown

## 📈 **Performance**

- **279 marques** scrapées en ~45-60 minutes
- **Taux de succès** : 100% (avec la v1 fonctionnelle)
- **Formats de sortie** : JSON + Markdown avec métadonnées complètes
- **🆕 Historique et fichiers MD** : Formatés automatiquement
- **Fréquence d'usage** : 1-2 fois par an (production)
- **Monitoring automatique** des changements

## 🆘 **Support & Maintenance**

- **Documentation** : Ce README + logs
- **Logs** : `scraper.log` pour debugging
- **🆕 Historique** : `docs/execution_history.md` pour revue des changements
- **🆕 Fichiers de données** : Format Markdown lisible pour analyse
- **Données** : Timestamps automatiques pour versioning
- **Versioning** : Rapports automatiques à chaque exécution

## 🚀 **Étapes Rapides pour Utiliser le Projet**

1. **Utiliser le script principal** :
   ```bash
   python autoscout24_scraper.py --test    # Test rapide (extraction auto)
   python autoscout24_scraper.py           # Scraping complet avec versioning + historique + Markdown
   ```

2. **🆕 Générer la version Markdown des marques** (si nécessaire) :
   ```bash
   python generate_brands_md.py            # Génère brands_for_scraping.md depuis brands_for_scraping.json
   ```

3. **Consulter l'historique et les fichiers** :
   ```bash
   cat docs/execution_history.md           # Voir l'historique des exécutions
   cat data/brands_for_scraping.md         # 🆕 Voir la liste des marques en format lisible
   cat data/auto_scraped_models_*.md       # Voir les données en format lisible
   ```

## 🔄 **Scénarios d'Usage Typiques**

### **Première Exécution (nouveau projet) :**
```bash
python autoscout24_scraper.py
# → Extrait automatiquement 279 marques
# → Crée brands_for_scraping.json
# → Génère le premier dataset
# → Crée les fichiers JSON et Markdown
# → Crée l'historique execution_history.md
```

### **Exécution Récurrente (surveillance) :**
```bash
python autoscout24_scraper.py
# → Charge les marques existantes
# → Compare avec la version précédente
# → Signale les nouvelles marques/modèles
# → Met à jour le dataset (JSON + MD)
# → Ajoute l'entrée dans l'historique Markdown
```

### **Test Rapide (validation) :**
```bash
python autoscout24_scraper.py --test
# → Test sur 20 marques seulement
# → Extraction rapide des marques si nécessaire
# → Validation du fonctionnement
# → Fichiers JSON + Markdown générés
# → Historique avec détail des nouvelles marques
```

## 🆕 **NOUVEAUTÉS v3.3 : Fichiers Markdown de Données**

Le script génère maintenant **automatiquement deux fichiers** par exécution :

### **1. Fichier JSON (Structure de Données)**
- Format strict pour traitement automatisé
- Métadonnées complètes
- Structure normalisée
- Idéal pour intégration système

### **2. 🆕 Fichier Markdown (Lisibilité Humaine)**
- **En-tête** avec métadonnées et statistiques
- **Liste complète** des marques et modèles triés
- **Organisation en colonnes** pour les marques avec beaucoup de modèles
- **Top 15** des marques par nombre de modèles
- **Répartition** du nombre de modèles par marque
- **Partie détaillée** des nouvelles marques (mode test)

### **Avantages du Format Markdown :**
- **Lecture immédiate** des données sans outil spécial
- **Recherche et navigation** facile dans le fichier
- **Documentation automatique** de chaque dataset
- **Format lisible** pour partage et analyse
- **Intégration** possible dans documentation projet

---