import concurrent.futures
import json
from .Utils import LLMInterface, extract_json, CONFIG, NotificationManager
from .SearchWorker import SearchWorker
import time

class RAGOrchestrator:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or CONFIG["CLEANED_DATA_PATH"]
        self.ai = LLMInterface.get_client()
        self.worker = SearchWorker(self.vault_path)
        self.notifier = NotificationManager()
        self.max_bots = 2 # Industrial Sweet Spot for API Stability
        self.failure_count = 0

    def generate_keywords(self, query):
        """AI Call 1: Strictly generates keywords from the command to save API costs."""
        system_instruction = """
        You are the 'RAG-Destroyer Keyword Swarm'.
        Convert the user command into 3-4 professional search keywords (English).
        Format: Return a JSON list of strings only.
        """
        raw = self.ai.call(query, system_instruction=system_instruction, json_mode=True)
        try:
            return json.loads(extract_json(raw))
        except:
            return [query]

    def execute_search(self, keywords, allowed_subsets):
        """Spawns parallel search workers for each keyword."""
        all_results = []
        
        # Parallel execution of SearchWorker for each keyword
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_bots) as executor:
            future_to_kw = {executor.submit(self.worker.search, kw, allowed_subsets): kw for kw in keywords}
            for future in concurrent.futures.as_completed(future_to_kw):
                kw = future_to_kw[future]
                try:
                    res = future.result()
                    all_results.append({"keyword": kw, "hits": res})
                except Exception as e:
                    print(f"Worker for '{kw}' failed: {e}")
        
        return all_results

    def calculate_best_subset(self, search_results):
        """
        Calculates the best subset of documents.
        Logic: Documents that appear in multiple keyword searches get higher priority.
        """
        doc_map = {} # path -> {doc_info, count}
        
        for item in search_results:
            for hit in item["hits"]:
                path = hit["path"]
                if path not in doc_map:
                    doc_map[path] = hit
                    doc_map[path]["hit_count"] = 1
                else:
                    # Boost relevance if found by multiple keywords
                    doc_map[path]["relevance"] += hit["relevance"]
                    doc_map[path]["hit_count"] += 1

        # Sort by hit_count (intersections) first, then relevance
        sorted_docs = sorted(doc_map.values(), key=lambda x: (x["hit_count"], x["relevance"]), reverse=True)
        return sorted_docs[:5] # Top 5 documents

    def final_synthesis(self, query, context_docs, scope_name):
        """Final GURU synthesis using authorized expert reasoning."""
        if not context_docs:
            return f"I apologize, as the GURU for {scope_name}, I could not find the information you requested within my authorized scope."

        # Prepare context text with token efficiency
        context_text = ""
        for i, doc in enumerate(context_docs):
            try:
                doc_summary = doc.get("summary", "No summary available.")
                content = ""
                with open(doc["path"], 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 3000:
                        content = content[:3000] + "... [Content truncated for cost efficiency]"
                
                context_text += f"\n--- SOURCE {i+1}: {doc['title']} (ID: {doc.get('doc_id', 'N/A')}) ---\n"
                context_text += f"DEPARTMENT/SCOPE: {doc.get('department', 'N/A')}\n"
                context_text += f"CONTENT: {content}\n"
            except: continue

        system_instruction = f"""
        You are the 'Global Enterprise GURU' for {scope_name}.
        You are a high-level Senior Executive Advisor who knows every detail within your authorized scope.
        
        GURU Operational Rules:
        1. GLOBAL LANGUAGE: Answer strictly in English with an international professional standard.
        2. SCOPE INTEGRITY: Answer ONLY using the provided source documents. If the answer isn't there, state clearly that it is outside your authorized knowledge.
        3. AUTHORITY: Speak with confidence, wisdom, and professional poise. Do not just summarize; provide actionable 'Executive Insights'.
        4. CITATION: You MUST cite the source ID or Title for every factual claim (e.g., [HRA-001]). Use square brackets.
        5. REASONING: Connect the dots across silos. If Source A mentions a policy and Source B mentions an implementation, explain the synergy.
        6. NO HALLUCINATION: Zero tolerance for guessing. Accuracy is your primary KPI.
        """
        
        prompt = f"Expert Query: {query}\n\nAuthorized Knowledge Context:\n{context_text}"
        
        # Call AI for initial synthesis
        report = self.ai.call(prompt, system_instruction=system_instruction)
        
        # Linguistic Guard: Refine the tone to ensure it meets 'Senior Executive Advisor' standards
        guard_instruction = "Refine the provided response to ensure it sounds like a world-class Senior Executive Advisor. Ensure citations are preserved and the language is polished. Ensure the tone is strictly professional English."
        refined_report = self.ai.call(report, system_instruction=guard_instruction)
        
        return refined_report

    def handle_request(self, query, authorized_scope):
        """Main Pipeline: AI (Keywords) -> Code (Parallel Search/Subset) -> AI (GURU Synthesis)."""
        # Refresh client in case of provider switch in UI
        self.ai = LLMInterface.get_client()
        
        scope_name = "your department" if authorized_scope != "ALL" else "the entire organization"
        if isinstance(authorized_scope, str) and authorized_scope != "ALL":
             scope_name = f"the {authorized_scope} scope"

        print(f"🧠 GURU processing: '{query}' within {scope_name}")
        
        # 1. AI Call 1: Generate Keywords
        keywords = self.generate_keywords(query)
        
        # Determine subsets based on security context (Individual or Department)
        if isinstance(authorized_scope, list) or authorized_scope == "ALL":
            actual_subsets = authorized_scope
        else:
            actual_subsets = [authorized_scope]

        print(f"🔑 Search Strategy: {keywords}")
        
        # 2. Local Code Execution: Parallel Search (Silo-Restricted)
        search_results = self.execute_search(keywords, actual_subsets)
        
        # 3. Local Code Execution: Expert Subset Selection
        best_context = self.calculate_best_subset(search_results)
        print(f"📊 GURU found {len(best_context)} key references.")
        
        # 4. AI Call 2: Final GURU Expert Synthesis
        try:
            report = self.final_synthesis(query, best_context, scope_name)
            self.failure_count = 0 # Reset on success
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= 2:
                self.notifier.send_line(f"🛡️ SAFETY CUT: Orchestrator encountered multiple failures. Cool-down activated.")
                return {
                    "answer": "I apologize. The system is currently in cool-down mode to maintain stability. Please try again later.",
                    "sources": [],
                    "keywords": keywords,
                    "guru_scope": scope_name
                }
            raise e
        
        return {
            "answer": report,
            "sources": best_context,
            "keywords": keywords,
            "guru_scope": scope_name
        }
