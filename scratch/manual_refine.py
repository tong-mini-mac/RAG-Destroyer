from core.Refinery import DataRefinery
from core.VaultWarden import VaultWarden
import os

def manual_refine():
    print("💎 Manual Refinery Start...")
    refinery = DataRefinery()
    # Process everything in raw_data/
    refinery.scan_and_refine_all(raw_dir="raw_data", default_dept="General")
    
    print("🛡️ Building Master Index...")
    warden = VaultWarden()
    warden.audit_and_index()
    print("✅ Process Complete.")

if __name__ == "__main__":
    manual_refine()
