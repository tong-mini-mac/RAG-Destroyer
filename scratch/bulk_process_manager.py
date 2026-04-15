import os
import sys
import time
from datetime import datetime

# Add core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.Refinery import DataRefinery
from core.Utils import CONFIG

RAW_DIR = "/Users/tong/Documents/MyClaw/RAG-Destroyer/raw_data"
CLEANED_ROOT = CONFIG["CLEANED_DATA_PATH"]
LOG_FILE = "/Users/tong/Documents/MyClaw/RAG-Destroyer/docs/REFINERY_INCIDENT_LOG.md"

def update_log(filename, status, problem="-", symptom="-", fix="-"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dept = filename.split("_")[0] if "_" in filename else "UNK"
    with open(LOG_FILE, "a") as f:
        f.write(f"| {timestamp} | {filename} | {dept} | {status} | {symptom} | {fix} |\n")

def is_already_processed(filename):
    # Check if a file with similar name (stripping prefix and extension) exists in cleaned data
    # Real logic: Refinery saves it based on AI suggestion. 
    # For this test, we check if the doc_id exists in the designated department folder.
    # Since we can't be 100% sure without reading the registry, we'll check by ID.
    parts = filename.split("_")
    if len(parts) < 2: return False
    doc_id = parts[0] + "-" + parts[1] # e.g. CRL-001
    
    # Check all subdirectories in cleaned data
    if not os.path.exists(CLEANED_ROOT):
        return False
        
    for dept_folder in os.listdir(CLEANED_ROOT):
        dept_path = os.path.join(CLEANED_ROOT, dept_folder)
        if not os.path.isdir(dept_path): continue
        for existing_file in os.listdir(dept_path):
            if existing_file.startswith(f"[{doc_id}]"):
                return True
    return False

def run_bulk(batch_size=50):
    refinery = DataRefinery()
    files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith(".txt")])
    to_process = [f for f in files if not is_already_processed(f)]
    
    total = len(to_process)
    print(f"📊 Found {len(files)} total files.")
    print(f"⏭️ Skipping {len(files) - total} already processed files.")
    print(f"🚀 Processing {total} remaining files in batches of {batch_size}...")

    success_count = 0
    start_time_all = time.time()

    for i, filename in enumerate(to_process):
        file_path = os.path.join(RAW_DIR, filename)
        start_time = time.time()
        
        try:
            print(f"[{i+1}/{total}] Processing {filename}...")
            dept_map = {
                "CRL": "Credit & Loans", 
                "OPS": "Operations", 
                "ITD": "IT & Digital", 
                "HRA": "HR & Admin", 
                "RSK": "Risk & Compliance"
            }
            target_dept = dept_map.get(filename.split("_")[0], "General")
            
            success = refinery.process_file(file_path, target_dept)
            
            if success:
                success_count += 1
            else:
                update_log(filename, "FAIL", "Processing logic returned False", "Logic error in Refinery", "Check logs")
                
        except Exception as e:
            update_log(filename, "ERROR", "System Exception", str(e), "Manual Review Required")
            
        # Logging progress summary every 10 files
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time_all
            avg = elapsed / (i + 1)
            remaining = (total - (i + 1)) * avg
            msg = f"Progress: {i+1}/{total} | Avg: {avg:.1f}s | Est. Remaining: {remaining/60:.1f}m"
            print(f"📝 {msg}")
            
        # Standard throttle to respect API
        time.sleep(1.2)

    total_elapsed = time.time() - start_time_all
    summary_msg = f"COMPLETED | Total: {total} | Success: {success_count} | Time: {total_elapsed/60:.1f}m"
    print(f"⭐ {summary_msg}")
    update_log("SUMMARY", "COMPLETED", "-", summary_msg, "-")

if __name__ == "__main__":
    run_bulk()
