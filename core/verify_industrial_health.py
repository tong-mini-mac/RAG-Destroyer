import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.Utils import NotificationManager, CONFIG
from core.Monitor import BackgroundMonitor
from core.Orchestrator import RAGOrchestrator

def test_notifications():
    print("--- Testing Notifications ---")
    notifier = NotificationManager()
    success = notifier.send_line("🛠️ RAG-Destroyer: Industrial Health Check")
    if success:
        print("✅ LINE Notify: Sent successfully.")
    else:
        print("⚠️ LINE Notify: Skipped or Failed (Check Token).")

def test_pid_management():
    print("\n--- Testing PID Management ---")
    monitor1 = BackgroundMonitor()
    monitor1.write_pid()
    pid_file = monitor1.pid_file
    
    if os.path.exists(pid_file):
        print(f"✅ PID file created: {pid_file}")
        with open(pid_file, "r") as f:
            print(f"📄 PID content: {f.read()}")
    else:
        print("❌ PID file NOT created.")

    # Test Zombie Cleanup
    print("Testing Zombie Cleanup logic...")
    monitor2 = BackgroundMonitor()
    # This should find the existing PID and handle it (mocking or real)
    # We won't kill our own process in a test unless planned, 
    # but we can verify the function exists.
    if hasattr(monitor2, 'cleanup_old_processes'):
        print("✅ Cleanup logic found.")

def test_orchestrator_config():
    print("\n--- Testing Orchestrator Config ---")
    orc = RAGOrchestrator()
    print(f"🤖 Max Bots: {orc.max_bots} (Target: 2)")
    if orc.max_bots == 2:
        print("✅ Parallel optimization applied.")
    else:
        print("❌ Bot count mismatch.")

if __name__ == "__main__":
    print("🚀 Starting Industrial Health Audit for RAG-Destroyer...")
    test_notifications()
    test_pid_management()
    test_orchestrator_config()
    print("\n🏁 Health Check Complete.")
