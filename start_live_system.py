#!/usr/bin/env python3
"""
Start script for live data collection system
Runs both the study program and dashboard
"""
import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def start_study_program():
    """Start the study program"""
    study_dir = Path(__file__).resolve().parent.parent / "facial-trust-study"
    
    if not study_dir.exists():
        print("❌ Study program directory not found!")
        print(f"Expected: {study_dir}")
        return None
    
    print("🚀 Starting study program...")
    print(f"Directory: {study_dir}")
    
    try:
        # Change to study program directory and start
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=study_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        if process.poll() is None:
            print("✅ Study program started successfully")
            print(f"PID: {process.pid}")
            print("URL: http://localhost:5001")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Study program failed to start")
            print(f"Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting study program: {e}")
        return None

def start_dashboard():
    """Start the dashboard"""
    print("🚀 Starting dashboard...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "dashboard_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        if process.poll() is None:
            print("✅ Dashboard started successfully")
            print(f"PID: {process.pid}")
            print("URL: http://localhost:5000")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Dashboard failed to start")
            print(f"Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return None

def monitor_processes(study_process, dashboard_process):
    """Monitor running processes"""
    try:
        while True:
            # Check if processes are still running
            if study_process and study_process.poll() is not None:
                print("❌ Study program stopped unexpectedly")
                break
                
            if dashboard_process and dashboard_process.poll() is not None:
                print("❌ Dashboard stopped unexpectedly")
                break
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if study_process:
            study_process.terminate()
        if dashboard_process:
            dashboard_process.terminate()
        print("✅ Services stopped")

def main():
    """Main function to start the live data collection system"""
    print("🔧 Starting Live Data Collection System")
    print("=" * 50)
    
    # First, run the setup
    print("📋 Running setup...")
    subprocess.run([sys.executable, "setup_live_data.py"])
    print()
    
    # Start study program
    study_process = start_study_program()
    if not study_process:
        print("❌ Failed to start study program. Exiting.")
        return
    
    # Wait a moment for study program to fully start
    time.sleep(3)
    
    # Start dashboard
    dashboard_process = start_dashboard()
    if not dashboard_process:
        print("❌ Failed to start dashboard. Stopping study program.")
        study_process.terminate()
        return
    
    print("\n🎉 Live Data Collection System is running!")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:5000")
    print("🔬 Study Program: http://localhost:5001")
    print("📋 Press Ctrl+C to stop both services")
    print("=" * 50)
    
    # Monitor processes
    monitor_processes(study_process, dashboard_process)

if __name__ == "__main__":
    main()
