from github.types import GithubPRChanged
import requests
from unidiff import PatchSet

def get_pr_content(pr: GithubPRChanged) -> str:
    if not pr or not pr.pull_request:
        raise ValueError("Invalid pull request data provided")
    
    diff_url = pr.pull_request.diff_url
    if not diff_url:
        raise ValueError("Pull request diff URL not found")
    
    response = requests.get(diff_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    patch = PatchSet(response.text)
    pr_line_data = ""

    for patched_file in patch:
        pr_line_data += f"File: {patched_file.path}\n"
        for hunk in patched_file:
            for line in hunk:
                pr_line_data += f"{line.line_type}: {line.value.strip()}\n"
    return pr_line_data
