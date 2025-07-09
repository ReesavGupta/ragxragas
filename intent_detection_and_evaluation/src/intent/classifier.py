from typing import Literal, Optional
from src.api.llm_router import LLMRouter

class KeywordIntentClassifier:
    """
    Lightweight keyword-based intent classifier (baseline).
    Returns one of: 'technical_support', 'billing_account', 'feature_request'.
    """
    def __init__(self):
        self.intent_keywords = {
            'technical_support': [
                'error', 'bug', 'issue', 'crash', 'not working', 'fix', 'problem', 'technical', 'code', 'api', 'integration', 'install', 'setup', 'configuration', 'login', 'reset', 'password', 'connect', 'server', 'database', 'timeout', 'fail', 'exception', 'stacktrace', 'debug', 'support'
            ],
            'billing_account': [
                'bill', 'billing', 'invoice', 'payment', 'charge', 'refund', 'subscription', 'account', 'plan', 'price', 'pricing', 'upgrade', 'downgrade', 'cancel', 'renew', 'credit', 'debit', 'card', 'receipt', 'transaction', 'policy', 'tax', 'fee', 'statement', 'balance', 'due', 'overdue', 'discount'
            ],
            'feature_request': [
                'feature', 'request', 'add', 'new', 'suggest', 'improve', 'enhance', 'roadmap', 'future', 'wish', 'would like', 'can you add', 'possible to', 'support for', 'comparison', 'alternative', 'option', 'custom', 'integration', 'expand', 'extend', 'more', 'less', 'change', 'update', 'modify'
            ]
        }

    def classify(self, query: str) -> Literal['technical_support', 'billing_account', 'feature_request']:
        q = query.lower()
        for intent, keywords in self.intent_keywords.items():
            if any(kw in q for kw in keywords):
                return intent  # type: ignore
        return 'technical_support'  # type: Literal['technical_support', 'billing_account', 'feature_request']

class LLMIntentClassifier:
    """
    LLM-based intent classifier using few-shot prompting (Ollama or GROQ via LLMRouter).
    Returns one of: 'technical_support', 'billing_account', 'feature_request'.
    """
    FEWSHOT_EXAMPLES = [
        {"query": "My app is crashing when I try to log in.", "intent": "technical_support"},
        {"query": "How do I update my billing information?", "intent": "billing_account"},
        {"query": "Can you add support for exporting data to Excel?", "intent": "feature_request"},
        {"query": "I was charged twice this month.", "intent": "billing_account"},
        {"query": "The API returns a 500 error.", "intent": "technical_support"},
        {"query": "Is there a plan to add dark mode?", "intent": "feature_request"},
    ]
    SYSTEM_PROMPT = (
        "You are an intent classifier for a SaaS customer support system. "
        "Classify the user's query into one of: technical_support, billing_account, feature_request. "
        "Respond with only the intent label."
    )

    def __init__(self, llm_router: Optional[LLMRouter] = None, backend: Literal['ollama', 'groq'] = "ollama"):
        self.llm_router = llm_router or LLMRouter(backend=backend)
        self.backend = backend

    def classify(self, query: str) -> Literal['technical_support', 'billing_account', 'feature_request']:
        # Compose few-shot prompt
        shots = "\n".join([
            f"Q: {ex['query']}\nIntent: {ex['intent']}" for ex in self.FEWSHOT_EXAMPLES
        ])
        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"{shots}\n"
            f"Q: {query}\nIntent:"
        )
        result = self.llm_router.generate(prompt, backend=self.backend)
        # Normalize and validate
        label = result.strip().lower()
        if "billing" in label:
            return "billing_account"
        if "feature" in label:
            return "feature_request"
        return "technical_support"

class HybridIntentClassifier:
    """
    Hybrid intent classifier: uses both keyword and LLM-based classifiers.
    You can choose 'keyword', 'llm', or 'hybrid' mode.
    """
    def __init__(self, mode: str = "hybrid", backend: Literal['ollama', 'groq'] = "ollama"):
        self.keyword = KeywordIntentClassifier()
        self.llm = LLMIntentClassifier(backend=backend)
        self.mode = mode

    def classify(self, query: str) -> Literal['technical_support', 'billing_account', 'feature_request']:
        if self.mode == "keyword":
            return self.keyword.classify(query)
        elif self.mode == "llm":
            return self.llm.classify(query)
        else:  # hybrid: use keyword, fallback to LLM if ambiguous
            kw_result = self.keyword.classify(query)
            # If keyword classifier is unsure (always returns tech support as fallback), try LLM
            if kw_result == "technical_support" and not any(
                kw in query.lower() for kw in self.keyword.intent_keywords["technical_support"]
            ):
                return self.llm.classify(query)
            return kw_result 