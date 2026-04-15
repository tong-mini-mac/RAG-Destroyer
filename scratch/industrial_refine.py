import concurrent.futures
from core.Refinery import DataRefinery
from core.VaultWarden import VaultWarden
import os

def industrial_refine():
    print("🚀 Industrial Batch Refinement ACTIVE.")
    refinery = DataRefinery()
    warden = VaultWarden()
    
    # Get first 30 files from raw_data
    raw_files = [f for f in os.listdir("raw_data") if not f.startswith(".")][:30]
    full_paths = [os.path.join("raw_data", f) for f in raw_files]
    
    print(f"📦 Processing Golden Batch: {len(full_paths)} files...")
    
    # Parallel processing (4 workers to avoid rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(refinery.process_file, path) for path in full_paths]
        concurrent.futures.wait(futures)
    
    print("🛡️ Building Master Index...")
    warden.audit_and_index()
    print("✅ Vault Initialized.")

if __name__ == "__main__":
    industrial_refine()
