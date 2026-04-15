import json
from .Utils import LLMInterface, extract_json

class AuditJudge:
    """The 'AI Judge' that evaluates the synthesis quality against the source context."""
    def __init__(self):
        self.ai = LLMInterface.get_client()

    def evaluate(self, query, context_docs, answer):
        """Perform a QC check on the answer with 5+5 scoring logic."""
        # Refresh client in case of provider switch
        self.ai = LLMInterface.get_client()
        
        context_text = ""
        for i, doc in enumerate(context_docs):
             context_text += f"\n[SOURCE {i+1}]: {doc.get('title')}\n{doc.get('summary')}\n"

        system_instruction = """
        You are the 'RAG-Destroyer Industrial Audit Judge'.
        Your task is to evaluate an AI Synthesis report using a strict 5+5 dual-scoring system.
        
        Evaluation Metrics:
        1. CONTEXT ACCURACY (0-5 points): 
           - Does the answer strictly follow the provided Source Context?
           - Are the facts accurate based ONLY on the sources?
           - Deduct points for any hallucination or information found outside the authorized subset.
        
        2. LANGUAGE & TONE (0-5 points):
           - Is the English professional and at a 'Senior Executive Advisor' level?
           - Is the phrasing clear, authoritative, and grammatically perfect?
           - Deduct points for poor tone, informal language, or grammatical errors.
        
        LANGUAGE REQUIREMENT: All commentary (critique) must be in professional English.
        
        Output Format:
        Return a JSON object only:
        {
          "accuracy_score": (int 0-5),
          "language_score": (int 0-5),
          "qc_score": (int sum of both, 0-10),
          "critique": "Breakdown of the scores and constructive feedback",
          "hallucination_detected": (bool),
          "tone_grade": "A/B/C/D"
        }
        """
        
        prompt = f"""
        Expert Query: {query}
        
        Reference Context:
        {context_text}
        
        AI Generated Answer:
        {answer}
        """
        
        raw_response = self.ai.call(prompt, system_instruction=system_instruction, json_mode=True)
        try:
            return json.loads(extract_json(raw_response))
        except:
            return {
                "accuracy_score": 0,
                "language_score": 0,
                "qc_score": 0,
                "critique": "Failed to parse QC Judge response.",
                "hallucination_detected": False,
                "tone_grade": "N/A"
            }
