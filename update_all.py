#!/usr/bin/env python3
"""
Main Orchestrator Script - Automobile Data Update System
Handles parallel execution of AS24 and CarGurus scrapers with consolidation
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime
import concurrent.futures
import threading

class AutoScoutOrchestrator:
    """Main orchestrator for automotive data updates."""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
    
    def display_banner(self):
        """Display the main banner."""
        print("🚗" * 20)
        print("🔄 AUTOMOBILE DATA UPDATE SYSTEM v5.0")
        print("🌍 EU + US Markets | AutoScout24 + CarGurus + Auto-Data")
        print("📊 Consolidation & Analysis")
        print("🚗" * 20)
        print()
    
    def display_menu(self):
        """Display the main menu."""
        print("📋 AVAILABLE OPTIONS:")
        print("   0. [Default] 🔄 Update ALL sources + Consolidate (PARALLEL)")
        print("   1. 🇪🇺 Update AutoScout24 ONLY (EU market)")
        print("   2. 🇺🇸 Update CarGurus ONLY (US market)")
        print("   3. 🇧🇬 Update Auto-Data ONLY (Technical specs)")
        print("   4. 🔄 Update AS24 + CarGurus (NO auto-data)")
        print("   5. 🔄 Update AS24 + Auto-Data (NO car-gurus)")
        print("   6. 🔄 Update CarGurus + Auto-Data (NO as24)")
        print("   7. 🔄 Update ALL THREE sources (NO consolidation)")
        print("   8. 🔗 Consolidate data ONLY")
        print("   9. 📊 Show stored statistics + Quit")
        print()
    
    def run_scraper(self, script_name, description):
        """Run a single scraper with timing - no live output to avoid encoding issues."""
        print(f"🚀 Starting: {description}")
        start_time = time.time()
        
        try:
            # Run the scraper script (no live output to avoid encoding issues)
            result = subprocess.run([
                sys.executable, script_name
            ], capture_output=True, text=True, timeout=3600, encoding='utf-8')
            
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
                    print(f"Error: {result.stderr}")
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
    
    def run_consolidation(self):
        """Run the consolidation script."""
        return self.run_scraper(
            'consolidate_brands_models.py',
            '🔗 Data Consolidation'
        )
    
    def run_as24_only(self):
        """Run only AutoScout24 scraper."""
        return self.run_scraper(
            'autoscout24_scraper.py',
            '🇪🇺 AutoScout24 (EU Market)'
        )
    
    def run_cguru_only(self):
        """Run only CarGurus scraper."""
        return self.run_scraper(
            'car_gurus_scraper.py',
            '🇺🇸 CarGurus (US Market)'
        )
    
    def run_auto_data_only(self):
        """Run only Auto-Data scraper."""
        return self.run_scraper(
            'autodata_scraper.py',
            '🇧🇬 Auto-Data (Technical Specs)'
        )
    
    def run_parallel_scraper(self, script_name, source_name, source_emoji):
        """Run a single scraper and return result with progress tracking via progress files."""
        print(f"🚀 {source_emoji} Starting: {source_name}")
        start_time = time.time()
        
        # Create progress file for this scraper
        progress_file = f"progress_{source_name.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '').lower()}.txt"
        Path(".").mkdir(exist_ok=True)
        
        # Remove old progress file if exists
        if os.path.exists(progress_file):
            os.remove(progress_file)
        
        try:
            # Run the scraper script
            process = subprocess.Popen([
                sys.executable, script_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Monitor progress by reading the progress file
            last_lines = set()
            
            while process.poll() is None:
                try:
                    if os.path.exists(progress_file):
                        with open(progress_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            # Show new progress lines
                            for line in lines:
                                line = line.strip()
                                if line and line not in last_lines:
                                    print(f"  {source_emoji} {line}")
                                    last_lines.add(line)
                    
                    time.sleep(1)  # Check every second
                except Exception:
                    pass  # Ignore any reading errors
                
            # Wait for process to complete
            process.wait()
            duration = time.time() - start_time
            
            # Read final results
            final_output = ""
            if os.path.exists(progress_file):
                try:
                    with open(progress_file, 'r', encoding='utf-8', errors='ignore') as f:
                        final_output = f.read()
                except:
                    pass
            
            if process.returncode == 0:
                print(f"  ✅ {source_name} completed in {duration:.1f}s")
                return {
                    'success': True,
                    'duration': duration,
                    'output': final_output,
                    'error': None
                }
            else:
                print(f"  ❌ {source_name} failed after {duration:.1f}s")
                return {
                    'success': False,
                    'duration': duration,
                    'output': final_output,
                    'error': f"Process exited with code {process.returncode}"
                }
                
        except Exception as e:
            print(f"  💥 {source_name} failed with exception: {e}")
            return {
                'success': False,
                'duration': 0,
                'output': '',
                'error': str(e)
            }
        finally:
            # Clean up progress file
            if os.path.exists(progress_file):
                os.remove(progress_file)
    
    def run_parallel_update(self):
        """Run all three scrapers in parallel, then consolidate."""
        print("🚀 Starting PARALLEL UPDATE (all three sources)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all three scraper jobs
            future_as24 = executor.submit(
                self.run_parallel_scraper,
                'autoscout24_scraper.py',
                'AutoScout24 (EU Market)',
                '🇪🇺'
            )
            future_cguru = executor.submit(
                self.run_parallel_scraper,
                'car_gurus_scraper.py',
                'CarGurus (US Market)',
                '🇺🇸'
            )
            future_autodata = executor.submit(
                self.run_parallel_scraper,
                'autodata_scraper.py',
                'Auto-Data (Technical Specs)',
                '🇧🇬'
            )
            
            print("⚡ Running AS24, CarGurus, and Auto-Data in parallel...")
            print("⏳ Processing... (progress will be shown at the end)")
            
            # Wait for all three to complete
            as24_result = future_as24.result()
            cguru_result = future_cguru.result()
            autodata_result = future_autodata.result()
        
        # Store results
        self.results = {
            'as24': as24_result,
            'cguru': cguru_result,
            'autodata': autodata_result
        }
        
        # Show completion summary
        if as24_result['success'] and cguru_result['success'] and autodata_result['success']:
            print("✅ All three scrapers completed successfully!")
            print("🔄 Starting consolidation...")
            consolidation_result = self.run_consolidation()
            self.results['consolidation'] = consolidation_result
            return True
        else:
            print("❌ One or more scrapers failed!")
            return False
    
    def run_both_no_consolidation(self):
        """Run AS24 and CarGurus without consolidation (old method for backward compatibility)."""
        print("🚀 Starting AS24 + CarGurus update (no consolidation)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_as24 = executor.submit(self.run_as24_only)
            future_cguru = executor.submit(self.run_cguru_only)
            
            print("⚡ Running AS24 and CarGurus in parallel...")
            
            as24_result = future_as24.result()
            cguru_result = future_cguru.result()
        
        self.results = {
            'as24': as24_result,
            'cguru': cguru_result
        }
        
        return as24_result['success'] and cguru_result['success']
    
    def run_as24_autodata_no_consolidation(self):
        """Run AS24 and Auto-Data without consolidation."""
        print("🚀 Starting AS24 + Auto-Data update (no consolidation)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_as24 = executor.submit(self.run_as24_only)
            future_autodata = executor.submit(self.run_auto_data_only)
            
            print("⚡ Running AS24 and Auto-Data in parallel...")
            
            as24_result = future_as24.result()
            autodata_result = future_autodata.result()
        
        self.results = {
            'as24': as24_result,
            'autodata': autodata_result
        }
        
        return as24_result['success'] and autodata_result['success']
    
    def run_cguru_autodata_no_consolidation(self):
        """Run CarGurus and Auto-Data without consolidation."""
        print("🚀 Starting CarGurus + Auto-Data update (no consolidation)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_cguru = executor.submit(self.run_cguru_only)
            future_autodata = executor.submit(self.run_auto_data_only)
            
            print("⚡ Running CarGurus and Auto-Data in parallel...")
            
            cguru_result = future_cguru.result()
            autodata_result = future_autodata.result()
        
        self.results = {
            'cguru': cguru_result,
            'autodata': autodata_result
        }
        
        return cguru_result['success'] and autodata_result['success']
    
    def run_all_three_no_consolidation(self):
        """Run all three scrapers without consolidation."""
        print("🚀 Starting ALL THREE sources update (no consolidation)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_as24 = executor.submit(self.run_as24_only)
            future_cguru = executor.submit(self.run_cguru_only)
            future_autodata = executor.submit(self.run_auto_data_only)
            
            print("⚡ Running AS24, CarGurus, and Auto-Data in parallel...")
            
            as24_result = future_as24.result()
            cguru_result = future_cguru.result()
            autodata_result = future_autodata.result()
        
        self.results = {
            'as24': as24_result,
            'cguru': cguru_result,
            'autodata': autodata_result
        }
        
        return as24_result['success'] and cguru_result['success'] and autodata_result['success']
    
    def show_statistics(self):
        """Display stored statistics from consolidated data."""
        print("📊 LOADING STORED STATISTICS...")
        print("=" * 50)
        
        # Try to load consolidated data
        consolidated_file = Path("data/consolidated_brands_models.json")
        
        if consolidated_file.exists():
            try:
                with open(consolidated_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get('metadata', {})
                stats = metadata.get('statistics', {})
                
                print(f"📅 Last Update: {metadata.get('consolidated_at', 'Unknown')}")
                print(f"🌍 Data Sources: {len(metadata.get('data_sources', {}))}")
                print(f"📋 Total Brands: {stats.get('total_brands', 'N/A')}")
                print(f"🏷️ Total Models: {stats.get('total_models', 'N/A')}")
                print(f"🇪🇺 AS24 Only: {stats.get('brands_only_as24', 'N/A')}")
                print(f"🇺🇸 CarGurus Only: {stats.get('brands_only_cguru', 'N/A')}")
                print(f"🇧🇬 Auto-Data Only: {stats.get('brands_only_autodata', 'N/A')}")
                print(f"🔄 2 Sources: {stats.get('brands_both', 'N/A')}")
                print(f"🌍 All 3 Sources: {stats.get('brands_all_three', 'N/A')}")
                
                # Show data sources details
                data_sources = metadata.get('data_sources', {})
                for source_name, source_info in data_sources.items():
                    print(f"\n📄 {source_name}:")
                    print(f"   File: {Path(source_info['file']).name}")
                
            except Exception as e:
                print(f"❌ Error loading statistics: {e}")
        else:
            print("❌ No consolidated data found!")
            print("💡 Run option 0 or 4 to create consolidated data")
        
        # Show latest individual scraper results
        data_dir = Path("data")
        print(f"\n📁 RECENT DATA FILES:")
        
        # Show recent AS24 files
        as24_files = list(data_dir.glob("as24_scraped_models_*.json"))
        if as24_files:
            latest_as24 = max(as24_files, key=lambda x: x.stat().st_mtime)
            print(f"🇪🇺 Latest AS24: {latest_as24.name}")
        
        # Show recent CarGurus files
        cguru_files = list(data_dir.glob("cargurus_scraped_models_*.json"))
        if cguru_files:
            latest_cguru = max(cguru_files, key=lambda x: x.stat().st_mtime)
            print(f"🇺🇸 Latest CarGurus: {latest_cguru.name}")
        
        # Show recent Auto-Data files
        autodata_files = list(data_dir.glob("autodata_scraped_models_*.json"))
        if autodata_files:
            latest_autodata = max(autodata_files, key=lambda x: x.stat().st_mtime)
            print(f"🇧🇬 Latest Auto-Data: {latest_autodata.name}")
        
        print("=" * 50)
    
    def display_summary(self):
        """Display execution summary."""
        if not self.results:
            return
        
        print("\n" + "=" * 60)
        print("📊 EXECUTION SUMMARY")
        print("=" * 60)
        
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        for task_name, result in self.results.items():
            if result:
                status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
                duration = result.get('duration', 0)
                print(f"{task_name.upper():<15} | {status:<10} | {duration:>6.1f}s")
        
        print("-" * 60)
        print(f"{'TOTAL':<15} | {'COMPLETED':<10} | {total_duration:>6.1f}s")
        print("=" * 60)
    
    def run(self):
        """Main execution loop."""
        self.display_banner()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("💡 Select option (0-4, 9): ").strip()
                
                if not choice:
                    choice = "0"  # Default option
                
                if choice == "0":
                    print("\n🔄 Starting COMPLETE UPDATE (parallel + consolidation)...")
                    self.start_time = time.time()
                    success = self.run_parallel_update()
                    
                elif choice == "1":
                    print("\n🇪🇺 Starting AutoScout24 ONLY update...")
                    self.start_time = time.time()
                    result = self.run_as24_only()
                    success = result['success']
                    
                elif choice == "2":
                    print("\n🇺🇸 Starting CarGurus ONLY update...")
                    self.start_time = time.time()
                    result = self.run_cguru_only()
                    success = result['success']
                    
                elif choice == "3":
                    print("\n🇧🇬 Starting Auto-Data ONLY update...")
                    self.start_time = time.time()
                    result = self.run_auto_data_only()
                    success = result['success']
                    
                elif choice == "4":
                    print("\n🔄 Starting AS24 + CarGurus update (no auto-data)...")
                    self.start_time = time.time()
                    success = self.run_both_no_consolidation()
                    
                elif choice == "5":
                    print("\n🔄 Starting AS24 + Auto-Data update (no car-gurus)...")
                    self.start_time = time.time()
                    success = self.run_as24_autodata_no_consolidation()
                    
                elif choice == "6":
                    print("\n🔄 Starting CarGurus + Auto-Data update (no as24)...")
                    self.start_time = time.time()
                    success = self.run_cguru_autodata_no_consolidation()
                    
                elif choice == "7":
                    print("\n🔄 Starting ALL THREE sources update (no consolidation)...")
                    self.start_time = time.time()
                    success = self.run_all_three_no_consolidation()
                    
                elif choice == "8":
                    print("\n🔗 Starting CONSOLIDATION ONLY...")
                    self.start_time = time.time()
                    result = self.run_consolidation()
                    success = result['success']
                    
                elif choice == "9":
                    print("\n👋 Showing statistics and exiting...")
                    self.show_statistics()
                    return
                    
                else:
                    print("❌ Invalid option! Please choose 0-9.")
                    continue
                
                # Display summary if we had results
                self.display_summary()
                
                if success:
                    print("🎉 Operation completed successfully!")
                else:
                    print("⚠️ Operation completed with errors. Check logs.")
                
                # Ask if user wants to continue
                print()
                continue_choice = input("🔄 Continue with another operation? (y/n): ").strip().lower()
                if continue_choice in ['n', 'no', 'non']:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n⏹️ Operation cancelled by user.")
                break
            except Exception as e:
                print(f"\n💥 Unexpected error: {e}")
                continue
        
        print("\n👋 Thanks for using the AutoScout System!")

def main():
    """Main entry point."""
    orchestrator = AutoScoutOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()