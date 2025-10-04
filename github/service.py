from github.types import GithubCommit, GithubCommitDetail, GithubCommitList, GithubPRChanged
import requests
from unidiff import PatchSet

def get_pr_latest_commit_diff(pr: GithubPRChanged) -> str:
    """
    Get the latest commit diff using GitHub API (more accurate than PR diff)
    """
    if not pr or not pr.pull_request:
        raise ValueError("Invalid pull request data provided")
    
    commits_url = pr.pull_request.commits_url
    if not commits_url:
        raise ValueError("Pull request commits URL not found")

    response = requests.get(commits_url)
    response.raise_for_status()  # Raise an exception for bad status codes

    commit_list = GithubCommitList(response.json())

    if not commit_list.root:
        raise ValueError("No commits found in the pull request")
    latest_commit = commit_list.root[-1]
    if not latest_commit or not latest_commit.sha:
        raise ValueError("Latest commit data is invalid")

    # Get the detailed commit with file changes using the GitHub API
    commit_detail_url = f"https://api.github.com/repos/{pr.repository.full_name}/commits/{latest_commit.sha}"
    response = requests.get(commit_detail_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    commit_detail = GithubCommitDetail(**response.json())
    
    # Create patch from the files' patch data
    patch_text = ""
    for file in commit_detail.files:
        if file.patch:
            patch_text += file.patch + "\n"
    
    if not patch_text:
        return "No patch data available for this commit"
    
    patch = PatchSet(patch_text)
    pr_line_data = ""

    for patched_file in patch:
        pr_line_data += f"File: {patched_file.path}\n"
        for hunk in patched_file:
            for line in hunk:
                pr_line_data += f"{line.line_type}: {line.value.strip()}\n"
    
    print(f"PR Lines: {pr_line_data}")
    return pr_line_data

def get_pr_diff(pr: GithubPRChanged) -> str:
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

def get_pr_comments(pr: GithubPRChanged) -> str:
    if not pr or not pr.pull_request:
        raise ValueError("Invalid pull request data provided")
    
    review_comments_url = pr.pull_request.review_comments_url
    if not review_comments_url:
        raise ValueError("Pull request review comments URL not found")

    response = requests.get(review_comments_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    patch = PatchSet(response.text)
    pr_line_data = ""

    for patched_file in patch:
        pr_line_data += f"File: {patched_file.path}\n"
        for hunk in patched_file:
            for line in hunk:
                pr_line_data += f"{line.line_type}: {line.value.strip()}\n"
    return pr_line_data
