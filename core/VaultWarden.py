import os
import frontmatter
from datetime import datetime
import json
from .Utils import CONFIG

class VaultWarden:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or CONFIG["CLEANED_DATA_PATH"]

    def audit_and_index(self):
        """Scans the vault and generates a master index file."""
        print("🛡️ Vault Warden: Commencing Audit...")
        
        index_data = {} # department -> [doc_info]
        
        for root, dirs, files in os.walk(self.vault_path):
            # Skip the root level files (like the index itself)
            if root == self.vault_path: continue
            
            department = os.path.basename(root)
            if department not in index_data:
                index_data[department] = []

            for file in files:
                if file.endswith(".md") and not file.startswith("_"):
                    file_path = os.path.join(root, file)
                    try:
                        post = frontmatter.load(file_path)
                        index_data[department].append({
                            "title": post.get("title", file),
                            "doc_id": post.get("doc_id", "N/A"),
                            "category": post.get("category", "General"),
                            "path": file, # relative to dept
                            "tags": post.get("tags", []),
                            "summary": post.get("summary", "")
                        })
                    except: continue

        self._write_master_index(index_data)
        self._write_search_cache(index_data)
        return index_data

    def _write_search_cache(self, data):
        """Writes a machine-readable JSON cache for fast searching."""
        cache_path = os.path.join(self.vault_path, "_SEARCH_CACHE.json")
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"⚡ Search Cache updated at: {cache_path}")

    def _write_master_index(self, data):
        """Writes the _MASTER_INDEX.md file."""
        index_content = f"# 🗃️ RAG-Destroyer: Master Document Index\n"
        index_content += f"**Last Index Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        index_content += "---\n\n"

        for dept, docs in data.items():
            index_content += f"## 📂 Department: {dept}\n"
            index_content += "| Doc ID | Document Title | Category | Tags | Summary |\n"
            index_content += "| :--- | :--- | :--- | :--- | :--- |\n"
            
            # Sort docs by ID
            sorted_docs = sorted(docs, key=lambda x: x["doc_id"])
            
            for d in sorted_docs:
                # Obsidian links to files in subfolders
                link = f"[[{dept}/{d['path'].replace('.md', '')}|{d['title']}]]"
                tags = " ".join([f"`{t}`" for t in d["tags"]])
                index_content += f"| `{d['doc_id']}` | {link} | {d['category']} | {tags} | {d['summary']} |\n"
            
            index_content += "\n"

        save_path = os.path.join(self.vault_path, "_MASTER_INDEX.md")
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"✅ Master Index updated at: {save_path}")
