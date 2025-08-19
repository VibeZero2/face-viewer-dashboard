#!/usr/bin/env python3
"""
Setup script for live data collection between study program and dashboard
"""
import os
import shutil
from pathlib import Path

def setup_shared_data_directory():
    """Set up shared data directory between study program and dashboard"""
    
    # Get current directory
    dashboard_dir = Path(__file__).resolve().parent
    study_program_dir = dashboard_dir.parent / "facial-trust-study"
    
    print("🔧 Setting up live data collection...")
    print(f"Dashboard directory: {dashboard_dir}")
    print(f"Study program directory: {study_program_dir}")
    
    # Check if study program exists
    if not study_program_dir.exists():
        print("❌ Study program directory not found!")
        print(f"Expected location: {study_program_dir}")
        print("Please ensure the facial-trust-study repository is in the parent directory.")
        return False
    
    # Create data directories
    dashboard_data_dir = dashboard_dir / "data" / "responses"
    study_data_dir = study_program_dir / "data" / "responses"
    
    dashboard_data_dir.mkdir(parents=True, exist_ok=True)
    study_data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Dashboard data directory: {dashboard_data_dir}")
    print(f"✅ Study program data directory: {study_data_dir}")
    
    # Check if we should copy existing data
    dashboard_files = list(dashboard_data_dir.glob("*.csv"))
    study_files = list(study_data_dir.glob("*.csv"))
    
    print(f"📊 Dashboard has {len(dashboard_files)} CSV files")
    print(f"📊 Study program has {len(study_files)} CSV files")
    
    # Copy study program data to dashboard if dashboard is empty
    if len(dashboard_files) == 0 and len(study_files) > 0:
        print("📋 Copying study program data to dashboard...")
        for file_path in study_files:
            dest_path = dashboard_data_dir / file_path.name
            if not dest_path.exists():
                shutil.copy2(file_path, dest_path)
                print(f"  ✅ Copied: {file_path.name}")
    
    # Create symbolic link for live data sharing (Windows)
    if os.name == 'nt':  # Windows
        try:
            # Create a junction point (Windows equivalent of symlink)
            if not dashboard_data_dir.exists():
                os.system(f'mklink /J "{dashboard_data_dir}" "{study_data_dir}"')
                print(f"🔗 Created junction point: {dashboard_data_dir} -> {study_data_dir}")
        except Exception as e:
            print(f"⚠️ Could not create junction point: {e}")
            print("Data will be copied manually. You may need to run this script periodically.")
    
    # Create .gitkeep files to ensure directories are tracked
    (dashboard_data_dir / ".gitkeep").touch(exist_ok=True)
    (study_data_dir / ".gitkeep").touch(exist_ok=True)
    
    print("\n✅ Live data collection setup complete!")
    print("\n📋 Next steps:")
    print("1. Start the study program: cd ../facial-trust-study && python app.py")
    print("2. Start the dashboard: python dashboard_app.py")
    print("3. The dashboard will automatically detect new data files")
    print("4. Use the API endpoints for live monitoring:")
    print("   - GET /api/data_status - Check current data status")
    print("   - POST /api/refresh_data - Manually refresh data")
    print("   - GET /api/live_updates - Get recent data updates")
    
    return True

def check_ports():
    """Check if ports are available"""
    import socket
    
    ports_to_check = {
        5000: "Dashboard",
        5001: "Study Program"
    }
    
    print("\n🔍 Checking port availability...")
    
    for port, service in ports_to_check.items():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                print(f"✅ Port {port} ({service}) is available")
        except OSError:
            print(f"❌ Port {port} ({service}) is already in use")
    
    print("\n💡 If ports are in use, you can:")
    print("1. Stop the existing services")
    print("2. Change the port in the configuration")
    print("3. Use different ports for each service")

if __name__ == "__main__":
    setup_shared_data_directory()
    check_ports()
