from github.types import GithubPRChanged
import requests
from unidiff import PatchSet

def get_pr_content(pr: GithubPRChanged) -> str:
    diff_url = pr.pull_request.diff_url
    response = requests.get(diff_url)
    patch = PatchSet(response.text)
    pr_line_data = ""

    for patched_file in patch:
        pr_line_data += f"File: {patched_file.path}\n"
        for hunk in patched_file:
            for line in hunk:
                pr_line_data += f"{line.line_type}: {line.value.strip()}\n"
    return pr_line_data
