# reviewer/services/review_engine.py
import json
from .llm_client import review_diff

def review_pr_file(filename: str, diff: str) -> dict:
    """
    Runs LLM review on a file diff and returns structured JSON:
    {
      "comments": [
        {"body": "....", "line": 12, "side": "RIGHT"}
      ],
      "summary": "..."
    }
    """
    try:
        result = review_diff(filename, diff)
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}
