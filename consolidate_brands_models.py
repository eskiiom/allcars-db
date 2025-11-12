#!/usr/bin/env python3
"""
Brand/Model Consolidation Script v2.0
Consolidates automotive brands and models from AS24, CarGurus, and Auto-Data sources
Supports incremental addition only - no deletions allowed
Outputs both JSON (for scripts) and Markdown (for humans)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_data_sources():
    """Load all available data sources."""
    data_sources = {}
    data_dir = Path("data")
    
    # Load AS24 data if available
    as24_files = list(data_dir.glob("*as24*scraped_models*.json"))
    if as24_files:
        # Get the most recent AS24 file
        as24_files.sort()
        latest_as24 = as24_files[-1]
        with open(latest_as24, 'r', encoding='utf-8') as f:
            as24_data = json.load(f)
        data_sources['AS24'] = {
            'file': str(latest_as24),
            'data': as24_data,
            'brands_models': as24_data.get('brands_models', {})
        }
        print(f"Loaded AS24 data from: {latest_as24}")
    
    # Load CarGurus data if available
    cguru_files = list(data_dir.glob("*cargurus*scraped_models*.json"))
    if cguru_files:
        # Get the most recent CarGurus file
        cguru_files.sort()
        latest_cguru = cguru_files[-1]
        with open(latest_cguru, 'r', encoding='utf-8') as f:
            cguru_data = json.load(f)
        data_sources['CarGurus'] = {
            'file': str(latest_cguru),
            'data': cguru_data,
            'brands_models': cguru_data.get('brands_models', {})
        }
        print(f"Loaded CarGurus data from: {latest_cguru}")
    
    # Load Auto-Data data if available
    autodata_files = list(data_dir.glob("*autodata*scraped_models*.json"))
    if autodata_files:
        # Get the most recent Auto-Data file
        autodata_files.sort()
        latest_autodata = autodata_files[-1]
        with open(latest_autodata, 'r', encoding='utf-8') as f:
            autodata_data = json.load(f)
        data_sources['Auto-Data'] = {
            'file': str(latest_autodata),
            'data': autodata_data,
            'brands_models': autodata_data.get('brands_models', {})
        }
        print(f"Loaded Auto-Data data from: {latest_autodata}")
    
    return data_sources

def consolidate_brands_models(data_sources):
    """Consolidate brands and models with additive approach only."""
    consolidated = {}
    stats = {
        'total_brands': 0,
        'total_models': 0,
        'brands_only_as24': 0,
        'brands_only_cguru': 0,
        'brands_only_autodata': 0,
        'brands_both': 0,
        'brands_all_three': 0,
        'new_models_added': 0,
        'unique_combinations': 0
    }
    
    # Process each brand from all sources
    all_brands = set()
    for source_name, source_info in data_sources.items():
        all_brands.update(source_info['brands_models'].keys())
    
    print(f"Processing {len(all_brands)} unique brands...")
    
    for brand in sorted(all_brands):
        brand_info = {
            'sources': [],
            'models': set()
        }
        
        # Check which sources have this brand
        for source_name, source_info in data_sources.items():
            if brand in source_info['brands_models']:
                brand_info['sources'].append(source_name)
                models = source_info['brands_models'][brand]
                if isinstance(models, list):
                    for model in models:
                        if model and model.strip():
                            brand_info['models'].add(model.strip())
        
        # Convert models set to sorted list
        brand_info['models'] = sorted(list(brand_info['models']))
        
        # Store in consolidated structure
        consolidated[brand] = {
            'sources': brand_info['sources'],
            'models': brand_info['models'],
            'model_count': len(brand_info['models'])
        }
        
        # Update statistics
        stats['total_brands'] += 1
        stats['total_models'] += len(brand_info['models'])
        
        if len(brand_info['sources']) == 1:
            if 'AS24' in brand_info['sources']:
                stats['brands_only_as24'] += 1
            elif 'CarGurus' in brand_info['sources']:
                stats['brands_only_cguru'] += 1
            elif 'Auto-Data' in brand_info['sources']:
                stats['brands_only_autodata'] += 1
        elif len(brand_info['sources']) == 2:
            stats['brands_both'] += 1
            # Count new models that appear in both sources
            for model in brand_info['models']:
                stats['unique_combinations'] += 1
        elif len(brand_info['sources']) == 3:
            stats['brands_all_three'] += 1
            # Count new models that appear in all three sources
            for model in brand_info['models']:
                stats['unique_combinations'] += 1
    
    return consolidated, stats

def save_json_output(consolidated_data, stats, data_sources):
    """Save consolidated data to JSON format."""
    output_data = {
        'metadata': {
            'consolidated_at': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            'consolidation_version': 'v2.0',
            'data_sources': data_sources,
            'statistics': stats,
            'description': 'Consolidated automotive brands and models from AS24, CarGurus, and Auto-Data - ADDITIVE ONLY'
        },
        'consolidated_brands_models': consolidated_data,
        'brands_list': sorted(consolidated_data.keys())
    }
    
    output_file = Path("data/consolidated_brands_models.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"JSON output saved: {output_file}")
    return str(output_file)

def generate_markdown_output(consolidated_data, stats, data_sources):
    """Generate readable Markdown output."""
    md_content = f"""# Consolidated Automotive Brands & Models (3 Sources)

**Consolidation Date** : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Version** : v2.0
**Method** : Additive consolidation (no deletions)

## Global Statistics

- **Total Brands** : {stats['total_brands']}
- **Total Models** : {stats['total_models']}
- **Unique Combinations** : {stats['unique_combinations']}

### Brand Distribution (3 Sources)
- **AS24 Only** : {stats['brands_only_as24']} brands
- **CarGurus Only** : {stats['brands_only_cguru']} brands
- **Auto-Data Only** : {stats['brands_only_autodata']} brands
- **2 Sources** : {stats['brands_both']} brands
- **All 3 Sources** : {stats['brands_all_three']} brands

## Data Sources

"""
    
    for source_name, source_info in data_sources.items():
        md_content += f"### {source_name}\n"
        md_content += f"- **File** : `{Path(source_info['file']).name}`\n"
        md_content += f"- **Brands Count** : {len(source_info['brands_models'])}\n"
        md_content += f"- **Total Models** : {sum(len(models) for models in source_info['brands_models'].values())}\n\n"
    
    md_content += """## Complete Brand List

| Brand | Sources | Model Count | First 3 Models |
|-------|---------|-------------|----------------|

"""
    
    # Generate brand table
    for brand_name, brand_info in sorted(consolidated_data.items()):
        sources_str = " + ".join(brand_info['sources'])
        model_count = brand_info['model_count']
        first_3_models = ", ".join(brand_info['models'][:3])
        if len(brand_info['models']) > 3:
            first_3_models += "..."
        
        md_content += f"| **{brand_name}** | {sources_str} | {model_count} | {first_3_models} |\n"
    
    md_content += f"""

## Analysis

### Top 20 Brands by Model Count

"""
    
    # Top 20 brands by model count
    top_brands = sorted(consolidated_data.items(), key=lambda x: x[1]['model_count'], reverse=True)[:20]
    for i, (brand_name, brand_info) in enumerate(top_brands, 1):
        sources_str = " + ".join(brand_info['sources'])
        md_content += f"{i}. **{brand_name}** ({brand_info['model_count']} models) - {sources_str}\n"
    
    md_content += f"""

### Multi-Source Brand Analysis

"""
    
    # All three sources
    all_three = [(name, info) for name, info in consolidated_data.items() if len(info['sources']) == 3]
    all_three.sort(key=lambda x: x[1]['model_count'], reverse=True)
    
    # Two sources
    both_sources = [(name, info) for name, info in consolidated_data.items() if len(info['sources']) == 2]
    both_sources.sort(key=lambda x: x[1]['model_count'], reverse=True)
    
    if all_three:
        md_content += "#### Brands Available in ALL THREE Sources\n\n"
        md_content += "| Brand | Total Models | Sources |\n"
        md_content += "|-------|-------------|----------|\n"
        
        for brand_name, brand_info in all_three:
            total_count = brand_info['model_count']
            sources_str = " + ".join(brand_info['sources'])
            md_content += f"| {brand_name} | {total_count} | {sources_str} |\n"
        
        md_content += "\n"
    
    if both_sources:
        md_content += "#### Brands Available in TWO Sources\n\n"
        md_content += "| Brand | Total Models | Sources |\n"
        md_content += "|-------|-------------|----------|\n"
        
        for brand_name, brand_info in both_sources:
            total_count = brand_info['model_count']
            sources_str = " + ".join(brand_info['sources'])
            md_content += f"| {brand_name} | {total_count} | {sources_str} |\n"
    
    md_content += f"""

## Usage Instructions

1. **For Scripts** : Use `data/consolidated_brands_models.json`
2. **For Humans** : This Markdown file for browsing
3. **Incremental Updates** : Re-run this script to add new brands/models
4. **No Deletions** : Existing brands and models are never removed

---

**Generated by** : Brand/Model Consolidation Script v2.0
**Data Sources** : AutoScout24 (EU) + CarGurus (US) + Auto-Data (BG)
**Last Updated** : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    output_file = Path("data/consolidated_brands_models.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"MD - Markdown output saved: {output_file}")
    return str(output_file)

def main():
    """Main consolidation process."""
    print("Starting Brand/Model Consolidation...")
    print("Method: Additive only (no deletions)")
    print()
    
    # Load all data sources
    data_sources = load_data_sources()
    
    if not data_sources:
        print("ERROR: No data sources found! Please run AS24, CarGurus, or Auto-Data scrapers first.")
        sys.exit(1)
    
    print(f"Found {len(data_sources)} data sources")
    print()
    
    # Consolidate data
    consolidated_data, stats = consolidate_brands_models(data_sources)
    
    # Save outputs
    json_file = save_json_output(consolidated_data, stats, data_sources)
    md_file = generate_markdown_output(consolidated_data, stats, data_sources)
    
    # Final summary
    print()
    print("CONSOLIDATION COMPLETE!")
    print(f"Total brands: {stats['total_brands']}")
    print(f"Total models: {stats['total_models']}")
    print(f"AS24 only: {stats['brands_only_as24']} brands")
    print(f"CarGurus only: {stats['brands_only_cguru']} brands")
    print(f"Auto-Data only: {stats['brands_only_autodata']} brands")
    print(f"2 sources: {stats['brands_both']} brands")
    print(f"All 3 sources: {stats['brands_all_three']} brands")
    print()
    print(f"JSON: {json_file}")
    print(f"MD: {md_file}")
    print()
    print("Next steps:")
    print("   1. Review the Markdown file for accuracy")
    print("   2. Use JSON file for programmatic access")
    print("   3. Re-run after new scrapes to add data")

if __name__ == "__main__":
    main()