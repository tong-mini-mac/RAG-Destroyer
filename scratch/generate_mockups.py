import os
import random

# Configuration
DEPARTMENTS = {
    "CRL": ["Lending Policy", "Risk Assessment", "Loan Contract", "Appraisal Notes"],
    "OPS": ["Branch Report", "Cash Management", "Incident Log", "Service Standard"],
    "ITD": ["Security Protocol", "System Architecture", "Deployment Plan", "Bug Report"],
    "HRA": ["Payroll Summary", "Welfare Policy", "Training Material", "Performance Review"],
    "RSK": ["Audit Report", "Compliance Check", "Fraud Analysis", "Legal Memo"]
}

OUTPUT_DIR = "/Users/tong/Documents/MyClaw/RAG-Destroyer/raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_sentence(dept):
    topics = {
        "CRL": ["interest rates", "collateral value", "borrower credit score", "default risk"],
        "OPS": ["cash flow", "branch efficiency", "customer wait time", "teller performance"],
        "ITD": ["firewall settings", "database migration", "API latency", "encryption standards"],
        "HRA": ["annual leave", "medical insurance", "bonus structure", "career development"],
        "RSK": ["regulatory changes", "aml detection", "internal control", "legal risks"]
    }
    actions = ["review", "update", "monitor", "optimize", "investigate"]
    context = ["quarterly", "urgently", "standard update", "based on audit", "for strategy 2026"]
    
    return f"We need to {random.choice(actions)} the {random.choice(topics[dept])} {random.choice(context)}."

def generate_unique_doc(dept_code, index):
    type_name = random.choice(DEPARTMENTS[dept_code])
    filename = f"{dept_code}_{index:03d}_{type_name.replace(' ', '_')}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    content = f"Department: {dept_code}\n"
    content += f"Document Type: {type_name}\n"
    content += f"Ref ID: {dept_code}-BATCH-{index:03d}\n"
    content += f"Date: 2026-04-{random.randint(1, 15):02d}\n"
    content += "--- Confidential Bank Document ---\n\n"
    
    for _ in range(5):
        content += generate_sentence(dept_code) + "\n"
        
    with open(filepath, "w") as f:
        f.write(content)
    return filename

if __name__ == "__main__":
    count = 0
    for dept_code in DEPARTMENTS:
        for i in range(1, 101):
            generate_unique_doc(dept_code, i)
            count += 1
    print(f"Total {count} mockups generated in {OUTPUT_DIR}")
