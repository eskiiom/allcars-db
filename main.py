#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AllCars-DB Main Menu - Central Hub
Complete automotive data management system with statistics and navigation
"""

import json
import logging
import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/main_menu.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AllCarsDBMainMenu:
    """Central menu system for AllCars-DB with comprehensive statistics."""

    def __init__(self):
        self.start_time = None
        self.stats_cache = {}
        self.last_stats_update = 0

    def display_banner(self):
        """Display the main banner with system status."""
        print("🚗" * 25)
        print("🏁 ALLCARS-DB v2.0 - COMPLETE AUTOMOTIVE DATA SYSTEM")
        print("🌍 Multi-Source Data Integration & Management")
        print("🚗" * 25)
        print()

        # Show system status
        self.display_system_status()

    def display_system_status(self):
        """Display current system status and statistics."""
        print("📊 SYSTEM STATUS:")
        print("-" * 50)

        # Data sources status
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        # Brands/Models data
        consolidated_files = list(data_dir.glob("consolidated_brands_models_*.json"))
        if consolidated_files:
            latest = max(consolidated_files, key=lambda x: x.stat().st_mtime)
            brands_count = self.get_brands_count(latest)
            print(f"🏷️ Brands/Models: {brands_count} brands ({latest.name})")
        else:
            print("🏷️ Brands/Models: No data available")

        # Technical specs data
        autodata_files = list(data_dir.glob("autodata_technical_specs_*.json"))
        carfolio_files = list(data_dir.glob("carfolio_technical_specs_*.json"))
        consolidated_tech_files = list(data_dir.glob("consolidated_technical_specs_*.json"))

        if autodata_files:
            latest = max(autodata_files, key=lambda x: x.stat().st_mtime)
            autodata_stats = self.get_technical_stats(latest)
            print(f"🇧🇬 Auto-Data Tech: {autodata_stats['brands']} brands, {autodata_stats['models']} models")
        else:
            print("🇧🇬 Auto-Data Tech: No data available")

        if carfolio_files:
            latest = max(carfolio_files, key=lambda x: x.stat().st_mtime)
            carfolio_stats = self.get_technical_stats(latest)
            print(f"🌍 Carfolio Tech: {carfolio_stats['brands']} brands, {carfolio_stats['models']} models")
        else:
            print("🌍 Carfolio Tech: No data available")

        if consolidated_tech_files:
            latest = max(consolidated_tech_files, key=lambda x: x.stat().st_mtime)
            consolidated_stats = self.get_consolidated_tech_stats(latest)
            print(f"🔄 Consolidated Tech: {consolidated_stats['brands']} brands, {consolidated_stats['conflicts']} conflicts resolved")
        else:
            print("🔄 Consolidated Tech: No data available")

        print("-" * 50)
        print()

    def get_brands_count(self, file_path: Path) -> int:
        """Get brands count from consolidated file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            consolidated = data.get('consolidated_brands_models', data)
            return len(consolidated)
        except:
            return 0

    def get_technical_stats(self, file_path: Path) -> Dict[str, int]:
        """Get technical specs statistics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            brands_data = data.get('brands_technical_data', {})
            total_models = sum(len(brand.get('models', {})) for brand in brands_data.values())

            return {
                'brands': len(brands_data),
                'models': total_models
            }
        except:
            return {'brands': 0, 'models': 0}

    def get_consolidated_tech_stats(self, file_path: Path) -> Dict[str, int]:
        """Get consolidated technical specs statistics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('metadata', {})
            stats = metadata.get('consolidation_stats', {})

            return {
                'brands': stats.get('brands_processed', 0),
                'conflicts': stats.get('total_conflicts_resolved', 0)
            }
        except:
            return {'brands': 0, 'conflicts': 0}

    def display_menu(self):
        """Display the main menu options."""
        print("📋 MAIN MENU - SELECT OPERATION:")
        print("   0. [Default] 🚀 Quick Start: Update ALL data (brands + technical specs)")
        print()
        print("🏷️ BRANDS & MODELS:")
        print("   1. 🌍 Scrape AutoScout24 brands/models")
        print("   2. 🇺🇸 Scrape CarGurus brands/models")
        print("   3. 🌐 Scrape Carfolio brands/models")
        print("   4. 🇧🇬 Scrape Auto-Data brands/models")
        print("   5. 🔄 Consolidate all brands/models (4 sources)")
        print("   5. 📊 Show brands/models statistics")
        print()
        print("🔧 TECHNICAL SPECIFICATIONS:")
        print("   6. 🇧🇬 Scrape Auto-Data technical specs (with years)")
        print("   7. 🌍 Scrape Carfolio technical specs")
        print("   8. 🔄 Consolidate technical specs (conflict resolution)")
        print("   9. 📊 Show technical specs statistics")
        print("  10. ⚖️ Analyze conflicts and resolution")
        print()
        print("🛠️ ADVANCED TOOLS:")
        print("  11. 📁 List all data files")
        print("  12. 🔍 Data validation and integrity check")
        print("  13. 📋 Show system help + documentation")
        print("  14. 🚪 Exit")
        print()

    def run_script_with_progress(self, script_name: str, description: str, expected_duration: int = 300, *args) -> Dict[str, Any]:
        """Run a script with periodic progress messages for long-running tasks."""
        import threading

        print(f"🚀 Starting: {description}")
        start_time = time.time()

        # Expected durations for different scrapers (in seconds)
        duration_messages = {
            'autoscout24': [
                (300, "🌍 AutoScout24: Still working... (~5-10 min remaining)"),
                (600, "🌍 AutoScout24: Processing brands... (~10-20 min remaining)"),
                (1200, "🌍 AutoScout24: Halfway through... (~10-15 min remaining)"),
                (1800, "🌍 AutoScout24: Almost done... (~5 min remaining)")
            ],
            'cargurus': [
                (600, "🇺🇸 CarGurus: Initializing... (~45-50 min remaining)"),
                (1200, "🇺🇸 CarGurus: Processing brands... (~35-40 min remaining)"),
                (1800, "🇺🇸 CarGurus: Still working... (~25-30 min remaining)"),
                (2400, "🇺🇸 CarGurus: Halfway through... (~15-20 min remaining)"),
                (3000, "🇺🇸 CarGurus: Almost done... (~5 min remaining)")
            ],
            'carfolio': [
                (30, "🌐 Carfolio: Quick processing... (~1-2 min remaining)"),
                (60, "🌐 Carfolio: Almost done... (~30 sec remaining)")
            ],
            'autodata': [
                (150, "🇧🇬 Auto-Data: Initializing... (~12-13 min remaining)"),
                (300, "🇧🇬 Auto-Data: Processing brands... (~10-11 min remaining)"),
                (450, "🇧🇬 Auto-Data: Halfway through... (~7-8 min remaining)"),
                (600, "🇧🇬 Auto-Data: Still working... (~4-5 min remaining)"),
                (750, "🇧🇬 Auto-Data: Almost done... (~1-2 min remaining)")
            ]
        }

        # Get progress messages for this scraper
        scraper_key = script_name.lower().replace('_scraper.py', '').replace('car_gurus', 'cargurus')
        progress_messages = duration_messages.get(scraper_key, [])

        # Function to print progress messages
        def print_progress_messages():
            for delay, message in progress_messages:
                time.sleep(delay)
                elapsed = time.time() - start_time
                if elapsed < expected_duration:  # Only print if still running
                    print(f"⏳ {message}")

        # Start progress message thread
        if progress_messages:
            progress_thread = threading.Thread(target=print_progress_messages, daemon=True)
            progress_thread.start()

        try:
            cmd = [sys.executable, script_name] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, encoding='utf-8', errors='replace')

            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"✅ {description} completed in {duration:.1f}s")
                return {
                    'success': True,
                    'duration': duration,
                    'output': result.stdout,
                    'error': None
                }
            else:
                print(f"❌ {description} failed after {duration:.1f}s")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}...")
                return {
                    'success': False,
                    'duration': duration,
                    'output': result.stdout,
                    'error': result.stderr
                }

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out after 1 hour")
            return {
                'success': False,
                'duration': 3600,
                'output': '',
                'error': 'Timeout after 1 hour'
            }
        except Exception as e:
            print(f"💥 {description} failed with exception: {e}")
            return {
                'success': False,
                'duration': 0,
                'output': '',
                'error': str(e)
            }

    def run_script(self, script_name: str, description: str, *args) -> Dict[str, Any]:
        """Run a script with timing and error handling."""
        print(f"🚀 Starting: {description}")
        start_time = time.time()

        try:
            cmd = [sys.executable, script_name] + list(args)

            # Pour les scrapers techniques longs, afficher la sortie en temps réel
            if 'technical' in script_name.lower() or 'autodata' in script_name.lower():
                print(f"📊 {description} - Real-time progress enabled")
                result = subprocess.run(cmd, text=True, timeout=3600, encoding='utf-8', errors='replace')
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, encoding='utf-8', errors='replace')

            duration = time.time() - start_time

            if result.returncode == 0:
                print(f"✅ {description} completed in {duration:.1f}s")
                return {
                    'success': True,
                    'duration': duration,
                    'output': result.stdout if hasattr(result, 'stdout') else '',
                    'error': None
                }
            else:
                print(f"❌ {description} failed after {duration:.1f}s")
                if hasattr(result, 'stderr') and result.stderr:
                    print(f"Error: {result.stderr[:200]}...")
                return {
                    'success': False,
                    'duration': duration,
                    'output': result.stdout if hasattr(result, 'stdout') else '',
                    'error': result.stderr if hasattr(result, 'stderr') else 'Unknown error'
                }

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out after 1 hour")
            return {
                'success': False,
                'duration': 3600,
                'output': '',
                'error': 'Timeout after 1 hour'
            }
        except Exception as e:
            print(f"💥 {description} failed with exception: {e}")
            return {
                'success': False,
                'duration': 0,
                'output': '',
                'error': str(e)
            }

    def run_quick_start(self):
        """Run the complete data update pipeline."""
        print("🚀 QUICK START: Complete data update pipeline")
        print("=" * 60)

        self.start_time = time.time()
        results = {}

        # Step 1: Update brands/models
        print("\n📍 PHASE 1: Updating Brands & Models")
        print("-" * 40)

        # Run individual scrapers with progress feedback
        results['autoscout24'] = self.run_script_with_progress('autoscout24_scraper.py', '🌍 AutoScout24 scraper', 1800)  # ~30 min
        results['cargurus'] = self.run_script_with_progress('car_gurus_scraper.py', '🇺🇸 CarGurus scraper', 3600)  # ~1 hour
        results['carfolio'] = self.run_script_with_progress('carfolio_scraper.py', '🌐 Carfolio scraper', 120)  # ~2 min
        results['autodata'] = self.run_script_with_progress('autodata_scraper.py', '🇧🇬 Auto-Data scraper', 900)  # ~15 min

        # Consolidate brands
        results['consolidate'] = self.run_script('consolidate_brands_models.py', '🔄 Brands consolidation')

        # Step 2: Update technical specs
        print("\n📍 PHASE 2: Updating Technical Specifications")
        print("-" * 40)

        # Run technical scrapers in parallel simulation
        results['autodata_tech'] = self.run_script('autodata_technical_scraper.py', '🇧🇬 Auto-Data technical scraper')
        results['carfolio_tech'] = self.run_script('carfolio_technical_scraper.py', '🌍 Carfolio technical scraper')

        # Consolidate technical specs
        results['tech_consolidate'] = self.run_script('technical_data_orchestrator.py', '🔄 Technical specs consolidation', '--consolidate-only')

        # Summary
        self.display_execution_summary(results)

        return all(r['success'] for r in results.values())

    def display_execution_summary(self, results: Dict[str, Any]):
        """Display execution summary."""
        print("\n" + "=" * 80)
        print("📊 EXECUTION SUMMARY - QUICK START")
        print("=" * 80)

        total_duration = time.time() - self.start_time if self.start_time else 0
        successful = 0
        failed = 0

        print(f"{'Task':<25} | {'Status':<10} | {'Duration':>8} | {'Details'}")
        print("-" * 80)

        for task_name, result in results.items():
            if result:
                status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
                duration = f"{result.get('duration', 0):>6.1f}s"
                details = "OK" if result['success'] else "Check logs"

                if result['success']:
                    successful += 1
                else:
                    failed += 1

                print(f"{task_name:<25} | {status:<10} | {duration:>8} | {details}")

        print("-" * 80)
        print(f"{'TOTAL':<25} | {'COMPLETED':<10} | {total_duration:>6.1f}s | {successful}/{successful+failed} successful")
        print("=" * 80)

    def show_brands_statistics(self):
        """Show comprehensive brands and models statistics."""
        print("📊 BRANDS & MODELS STATISTICS")
        print("=" * 60)

        data_dir = Path("data")
        consolidated_files = list(data_dir.glob("consolidated_brands_models_*.json"))

        if not consolidated_files:
            print("❌ No consolidated brands data found!")
            print("💡 Run option 4 to create consolidated data")
            return

        latest_file = max(consolidated_files, key=lambda x: x.stat().st_mtime)

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('metadata', {})
            stats = metadata.get('statistics', {})

            print(f"📅 Last Update: {metadata.get('consolidated_at', 'Unknown')}")
            print(f"🔄 Consolidation Version: {metadata.get('consolidation_version', 'Unknown')}")
            print()

            # Overall statistics
            print("🌍 OVERALL STATISTICS:")
            print(f"   Total Brands: {stats.get('total_brands', 'N/A')}")
            print(f"   Total Models: {stats.get('total_models', 'N/A')}")
            print(f"   Brands with Models: {stats.get('brands_with_models', 'N/A')}")
            print()

            # Data sources breakdown
            data_sources = metadata.get('data_sources', {})
            print("📄 DATA SOURCES:")
            for source_name, source_info in data_sources.items():
                print(f"   {source_name.upper()}: {source_info.get('brands_count', 'N/A')} brands, {source_info.get('models_count', 'N/A')} models")

            print()
            print("📁 File: " + str(latest_file.name))

        except Exception as e:
            print(f"❌ Error loading statistics: {e}")

        print("=" * 60)

    def show_technical_statistics(self):
        """Show comprehensive technical specifications statistics."""
        print("📊 TECHNICAL SPECIFICATIONS STATISTICS")
        print("=" * 60)

        data_dir = Path("data")

        # Individual source files
        autodata_files = list(data_dir.glob("autodata_technical_specs_*.json"))
        carfolio_files = list(data_dir.glob("carfolio_technical_specs_*.json"))
        consolidated_files = list(data_dir.glob("consolidated_technical_specs_*.json"))

        # Show individual sources
        if autodata_files:
            latest = max(autodata_files, key=lambda x: x.stat().st_mtime)
            stats = self.get_technical_stats(latest)
            print(f"🇧🇬 Auto-Data: {stats['brands']} brands, {stats['models']} models ({latest.name})")

        if carfolio_files:
            latest = max(carfolio_files, key=lambda x: x.stat().st_mtime)
            stats = self.get_technical_stats(latest)
            print(f"🌍 Carfolio: {stats['brands']} brands, {stats['models']} models ({latest.name})")

        # Show consolidated data
        if consolidated_files:
            print()
            latest = max(consolidated_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                metadata = data.get('metadata', {})
                stats = metadata.get('consolidation_stats', {})

                print("🔄 CONSOLIDATED TECHNICAL DATA:")
                print(f"   Last Consolidation: {metadata.get('consolidated_at', 'Unknown')}")
                print(f"   Method: {metadata.get('method', 'Unknown')}")
                print(f"   Brands Processed: {stats.get('brands_processed', 'N/A')}")
                print(f"   Models Consolidated: {stats.get('models_consolidated', 'N/A')}")
                print(f"   Specifications: {stats.get('specs_consolidated', 'N/A')}")
                print(f"   Conflicts Resolved: {stats.get('total_conflicts_resolved', 'N/A')}")
                print(f"   File: {latest.name}")

            except Exception as e:
                print(f"❌ Error loading consolidated stats: {e}")

        if not autodata_files and not carfolio_files and not consolidated_files:
            print("❌ No technical specifications data found!")
            print("💡 Run options 6-8 to scrape and consolidate technical data")

        print("=" * 60)

    def list_data_files(self):
        """List all available data files with details."""
        print("📁 ALL DATA FILES")
        print("=" * 80)

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        # Get all JSON files
        all_files = list(data_dir.glob("*.json"))
        if not all_files:
            print("❌ No data files found in /data directory")
            return

        # Group files by type
        file_groups = {
            'Brands/Models': [],
            'Technical Specs': [],
            'Consolidated': [],
            'Other': []
        }

        for file_path in sorted(all_files, key=lambda x: x.stat().st_mtime, reverse=True):
            filename = file_path.name
            size_mb = file_path.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")

            if 'consolidated_brands' in filename:
                file_groups['Brands/Models'].append((filename, size_mb, mtime))
            elif 'technical_specs' in filename and 'consolidated' not in filename:
                file_groups['Technical Specs'].append((filename, size_mb, mtime))
            elif 'consolidated_technical' in filename:
                file_groups['Consolidated'].append((filename, size_mb, mtime))
            else:
                file_groups['Other'].append((filename, size_mb, mtime))

        # Display each group
        for group_name, files in file_groups.items():
            if files:
                print(f"\n{group_name.upper()}:")
                print("-" * 60)
                for filename, size_mb, mtime in files:
                    print(f"   {filename:<50} {size_mb:>6.2f} MB  {mtime}")

        print("\n" + "=" * 80)

    def show_help(self):
        """Show comprehensive help and documentation."""
        print("📋 ALLCARS-DB HELP & DOCUMENTATION")
        print("=" * 80)
        print("Complete automotive data scraping and consolidation system")
        print()

        print("🏗️ SYSTEM ARCHITECTURE:")
        print("   • 4 Data Sources: AutoScout24, CarGurus, Carfolio, Auto-Data")
        print("   • Phase 1: Brands/Models scraping from all 4 sources")
        print("   • Phase 2: Technical specifications extraction")
        print("   • Multi-source consolidation with conflict resolution")
        print("   • Technical specifications with production years")
        print("   • Real-time statistics and data validation")
        print()

        print("🔄 DATA PIPELINE:")
        print("   1. Individual source scraping (brands & models)")
        print("   2. Data consolidation and deduplication")
        print("   3. Technical specifications extraction")
        print("   4. Multi-source conflict resolution")
        print("   5. Final consolidated database")
        print()

        print("📊 KEY FEATURES:")
        print("   • Smart filtering (only existing brands)")
        print("   • Production year extraction")
        print("   • Priority-based conflict resolution")
        print("   • Comprehensive metadata tracking")
        print("   • Parallel processing capabilities")
        print()

        print("🎯 USE CASES:")
        print("   • Automotive market research")
        print("   • Technical specifications database")
        print("   • Multi-source data integration")
        print("   • Data quality validation")
        print("   • Historical automotive data")
        print()

        print("📁 OUTPUT FILES:")
        print("   • consolidated_brands_models_TIMESTAMP.json")
        print("   • autodata_technical_specs_TIMESTAMP.json")
        print("   • carfolio_technical_specs_TIMESTAMP.json")
        print("   • consolidated_technical_specs_TIMESTAMP.json")
        print()

        print("⚙️ CONFIGURATION:")
        print("   • All settings in individual scraper files")
        print("   • Conflict resolution priorities adjustable")
        print("   • Parallel processing for efficiency")
        print("   • Error handling and retry logic")
        print("=" * 80)

    def run(self):
        """Main execution loop."""
        self.display_banner()

        while True:
            self.display_menu()

            try:
                choice = input("💡 Select option (0-14): ").strip()

                if not choice:
                    choice = "0"  # Default option

                if choice == "0":
                    print("\n🚀 Starting QUICK START - Complete data pipeline...")
                    success = self.run_quick_start()

                elif choice == "1":
                    print("\n🌍 Starting AutoScout24 brands/models scraping...")
                    result = self.run_script_with_progress('autoscout24_scraper.py', 'AutoScout24 scraper', 1800)

                elif choice == "2":
                    print("\n🇺🇸 Starting CarGurus brands/models scraping...")
                    result = self.run_script_with_progress('car_gurus_scraper.py', 'CarGurus scraper', 3600)

                elif choice == "3":
                    print("\n🌐 Starting Carfolio brands/models scraping...")
                    result = self.run_script_with_progress('carfolio_scraper.py', 'Carfolio scraper', 120)

                elif choice == "4":
                    print("\n🇧🇬 Starting Auto-Data brands/models scraping...")
                    result = self.run_script_with_progress('autodata_scraper.py', 'Auto-Data scraper', 900)

                elif choice == "5":
                    print("\n🔄 Starting brands/models consolidation...")
                    result = self.run_script('consolidate_brands_models.py', 'Brands consolidation')

                elif choice == "5":
                    print("\n📊 Showing brands/models statistics...")
                    self.show_brands_statistics()
                    continue

                elif choice == "6":
                    print("\n🇧🇬 Starting Auto-Data technical specs scraping...")
                    result = self.run_script('autodata_technical_scraper.py', 'Auto-Data technical scraper')

                elif choice == "7":
                    print("\n🌍 Starting Carfolio technical specs scraping...")
                    result = self.run_script('carfolio_technical_scraper.py', 'Carfolio technical scraper')

                elif choice == "8":
                    print("\n🔄 Starting technical specs consolidation...")
                    result = self.run_script('technical_data_orchestrator.py', 'Technical data orchestrator')

                elif choice == "9":
                    print("\n📊 Showing technical specs statistics...")
                    self.show_technical_statistics()
                    continue

                elif choice == "10":
                    print("\n⚖️ Starting conflict analysis...")
                    # Note: This would need to be implemented in the orchestrator
                    print("⚠️ Conflict analysis feature coming soon!")
                    continue

                elif choice == "11":
                    print("\n📁 Listing all data files...")
                    self.list_data_files()
                    continue

                elif choice == "12":
                    print("\n🔍 Starting data validation...")
                    result = self.run_script('test_dependencies.py', 'Data validator')

                elif choice == "13":
                    print("\n📋 Showing help and documentation...")
                    self.show_help()
                    continue

                elif choice == "14":
                    print("\n👋 Thanks for using AllCars-DB!")
                    return

                else:
                    print("❌ Invalid option! Please choose 0-14.")
                    continue

                # Display result
                if 'result' in locals() and result:
                    if result['success']:
                        print("🎉 Operation completed successfully!")
                    else:
                        print("⚠️ Operation completed with errors. Check logs.")

                # Ask to continue
                print()
                continue_choice = input("🔄 Continue with another operation? (y/n): ").strip().lower()
                if continue_choice in ['n', 'no', 'non']:
                    break

                # Refresh system status
                print("\n" + "="*60)
                self.display_system_status()

            except KeyboardInterrupt:
                print("\n\n⏹️ Operation cancelled by user.")
                break
            except Exception as e:
                print(f"\n💥 Unexpected error: {e}")
                continue

        print("\n👋 Thanks for using AllCars-DB!")

def main():
    """Main entry point."""
    menu = AllCarsDBMainMenu()
    menu.run()

if __name__ == "__main__":
    main()