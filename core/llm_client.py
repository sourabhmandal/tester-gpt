import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from testergpt.settings import settings
from core.types import PRReviewResponse

def get_llm(model="gemini-2.5-pro", temperature=0.2):
    """Return a LangChain LLM instance with proper error handling"""
    if not settings.GPT_API_KEY or settings.GPT_API_KEY == "sk-YourAIKeyHere":
        raise ValueError("Google API key is not configured. Please set GPT_API_KEY in your .env file")
    
    try:
        return ChatGoogleGenerativeAI(
            model=model, 
            temperature=temperature, 
            google_api_key=settings.GPT_API_KEY,
            convert_system_message_to_human=True,
        )
    except Exception as e:
        logging.error(f"Failed to initialize LLM client: {e}")
        raise

def review_diff(diff: str, model="gemini-2.5-pro") -> PRReviewResponse:
    """Send a diff to LLM and return structured JSON response"""
    if not diff or not diff.strip():
        raise ValueError("Diff content is empty or invalid")
    
    try:
        llm = get_llm(model)
        
        # Create structured output LLM
        structured_llm = llm.with_structured_output(PRReviewResponse)

        template = """
        You are an AI code reviewer. Analyze the provided git diff and provide feedback.
        
        Diff:
        ```diff
        {diff}
        ```
        
        Instructions:
        - Only analyze lines starting with '+' or '-' (added/removed code)
        - Ignore metadata lines (diff --git, index, ---, +++)
        - Look for potential issues in:
          * Correctness and logic errors
          * Code readability and maintainability  
          * Security vulnerabilities
          * Performance concerns
          * Best practices violations
        
        For each issue found, specify:
        - type: "error", "warning", or "suggestion"
        - line: line number or range where the issue occurs  
        - message: clear description of the issue
        - severity: "high", "medium", or "low"
        - file: the file path from the diff (look for lines starting with '+++' or 'diff --git')
        
        IMPORTANT: Extract the file path from diff headers like:
        - "diff --git a/path/to/file.py b/path/to/file.py"
        - "+++ b/path/to/file.py"
        
        Provide an overall summary of the changes and any recommendations.
        """

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | structured_llm
        response = chain.invoke({"diff": diff})
        
        if not response:
            raise RuntimeError("Empty response from LLM")
        
        # Response is already a PRReviewResponse object from structured output
        return response
        
    except Exception as e:
        logging.error(f"Error in review_diff: {e}")
        # Return a fallback response with proper structure
        fallback_response = PRReviewResponse(
            issues=[],
            summary=f"Error occurred during code review: {str(e)}"
        )
        return fallback_response
