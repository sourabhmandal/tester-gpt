
"""
Github related integrations
"""
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from core.llm_client import review_diff
from github.service import get_pr_content
from rest_framework.response import Response
from github.types import GithubPRChanged
from core.types import PRReviewResponse
from github.utils import GITHUB_COMMIT_INLINE_COMMENT_URL_TEMPLATE, generate_jwt, get_installation_token
import requests


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok"}, status=200, headers={"ngrok-skip-browser-warning": "<>"})

@api_view(['POST'])
@permission_classes([AllowAny])
def github_webhook(request):
    event = request.headers.get("X-GitHub-Event", "unknown")
    delivery = request.headers.get("X-GitHub-Delivery", "unknown")
    
    # handle events
    print(f"Received event={event} delivery={delivery}")
    if event == "ping":
        return Response({"msg": "pong"}, status=200)
    
    # Only process pull request related events
    if event == "pull_request" and request.data.get("action") in ["opened", "synchronize"]:
        try:
            payload = GithubPRChanged(**request.data)
            print(f"✅ Successfully parsed webhook payload for PR #{payload.number}: {payload.pull_request.title}")
        except Exception as e:
            print(f"Failed to parse webhook payload: {e}")
            print(f"Request data keys: {list(request.data.keys()) if hasattr(request, 'data') else 'No data'}")
            return Response({"error": "Invalid payload structure"}, status=400)
        
        try:
            print(f"🔍 Fetching diff content for PR #{payload.number}")
            diff_text = get_pr_content(payload)
            print(f"📄 Retrieved diff content ({len(diff_text)} characters)")
            
            # ai
            print(f"🤖 Running AI review on diff...")
            review_response = review_diff(diff=diff_text)
            print(f"📝 AI review completed with {len(review_response.issues) if review_response.issues else 0} issues found")
            
            post_pr_comments(payload, review_response=review_response)
            print(f"✅ Successfully processed PR #{payload.number}")
        except Exception as e:
            print(f"Error processing pull request: {e}")
            return Response({"error": "Failed to process pull request"}, status=500)
    
    return Response("", status=204)

def post_pr_comments(payload: GithubPRChanged, review_response: PRReviewResponse):
    if not review_response.issues:
        print("No issues found in the diff, skipping comment posting")
        return

    if not payload or not payload.pull_request:
        print("Invalid payload data, cannot post comments")
        return

    try:
        # Step 1: Generate JWT
        jwt_token = generate_jwt()

        # Step 2: Exchange for installation token
        installation_id = payload.installation.id
        installation_token = get_installation_token(jwt_token, installation_id)

        # GitHub API endpoint
        url = GITHUB_COMMIT_INLINE_COMMENT_URL_TEMPLATE.format(
            owner=payload.repository.owner.login,
            repo=payload.repository.name,
            pull_number=payload.pull_request.number,
        )

        print(f"Calling PR Comment URL: {url}")

        headers = {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github+json"
        }

        successful_comments = 0
        for issue in review_response.issues:
            emoji = {"error": "🚫", "warning": "⚠️", "suggestion": "💡"}.get(issue.type, "ℹ️")
            comment_body = f"{emoji} **{issue.type.title()}** ({issue.severity} severity)\\n\\n{issue.message}"

            line_num = int(issue.line.split("-")[0]) if "-" in issue.line else int(issue.line)

            api_payload = {
                "body": comment_body,
                "commit_id": payload.pull_request.head.sha,
                "path": issue.file,
                "line": line_num,
                "side": "RIGHT"
            }

            print(f"📝 Posting PR comment to {issue.file}:{line_num}")
            response = requests.post(url, json=api_payload, headers=headers)
            if response.status_code == 201:
                print(f"✅ Posted comment for {issue.file}:{line_num}")
                successful_comments += 1
            else:
                print(f"❌ Failed ({response.status_code}): {response.text}")
        
        print(f"🎯 Posted {successful_comments}/{len(review_response.issues)} comments successfully")
    
    except Exception as e:
        print(f"Error posting PR comments: {e}")
        raise
