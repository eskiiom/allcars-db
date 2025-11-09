#!/usr/bin/env python3
"""
Script pour générer la version Markdown du fichier brands_for_scraping.json
"""

import json
from pathlib import Path
from datetime import datetime

def generate_brands_markdown(brands_data, json_file_path):
    """Génère une version Markdown lisible des marques extraites."""
    try:
        # Créer le chemin du fichier Markdown
        json_path = Path(json_file_path)
        md_file = json_path.with_suffix('.md')

        # Préparer le contenu Markdown
        md_content = format_brands_as_markdown(brands_data)

        # Sauvegarder le fichier Markdown
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"✅ Fichier Markdown des marques généré: {md_file}")
        return str(md_file)

    except Exception as e:
        print(f"❌ Erreur lors de la génération du fichier Markdown des marques: {e}")
        return None

def format_brands_as_markdown(brands_data):
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
        md_content += f"**Généré par** : AutoScout24 Scraper v3.3\n"
        md_content += f"**Date de génération** : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n"

        return md_content

    except Exception as e:
        print(f"❌ Erreur lors du formatage Markdown des marques: {e}")
        return f"# 🚗 AutoScout24 - Liste des Marques\n\n**Erreur lors du formatage :** {e}\n"

def main():
    print("🚀 Génération du fichier Markdown des marques...")

    # Charger les données existantes
    brands_file = Path('data/as24_brands_for_scraping.json')
    if brands_file.exists():
        with open(brands_file, 'r', encoding='utf-8') as f:
            brands_data = json.load(f)

        print(f"📋 Marques chargées: {len(brands_data['brands'])}")

        # Générer la version Markdown
        md_file = generate_brands_markdown(brands_data, str(brands_file))

        if md_file:
            print(f"🎉 SUCCÈS! Fichier Markdown généré: {md_file}")
        else:
            print("❌ Échec de la génération du Markdown")
    else:
        print("❌ Fichier as24_brands_for_scraping.json non trouvé")

if __name__ == "__main__":
    main()