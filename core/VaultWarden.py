import os
import frontmatter
from datetime import datetime
import json
from .Utils import CONFIG
from .sources import build_knowledge_source

class VaultWarden:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or CONFIG["CLEANED_DATA_PATH"]
        self.source = build_knowledge_source(
            CONFIG.get("KNOWLEDGE_SOURCE_BACKEND", "localfs"),
            self.vault_path,
        )

    def audit_and_index(self):
        """Scans the vault and generates a master index file."""
        print("🛡️ Vault Warden: Commencing Audit...")
        
        index_data = {} # department -> [doc_info]
        
        for department in self.source.list_departments():
            if department not in index_data:
                index_data[department] = []
            dept_root = os.path.join(self.vault_path, department)
            for file_path in self.source.iter_markdown_files(department):
                file = os.path.basename(file_path)
                try:
                    post = frontmatter.load(file_path)
                    rel_path = os.path.relpath(file_path, dept_root).replace("\\", "/")
                    index_data[department].append({
                        "title": post.get("title", file),
                        "doc_id": post.get("doc_id", "N/A"),
                        "category": post.get("category", "General"),
                        "path": rel_path, # relative to dept
                        "tags": post.get("tags", []),
                        "summary": post.get("summary", "")
                    })
                except Exception:
                    continue

        self._write_master_index(index_data)
        self._write_search_cache(index_data)
        return index_data

    def _write_search_cache(self, data):
        """Writes a machine-readable JSON cache for fast searching."""
        cache_path = self.source.cache_path()
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

        save_path = self.source.master_index_path()
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"✅ Master Index updated at: {save_path}")
