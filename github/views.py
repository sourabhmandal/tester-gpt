
"""
Github related integrations
"""
from rest_framework.decorators import api_view, permission_classes
import json
from rest_framework.permissions import AllowAny
from github.utils import verify_signature
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok"}, status=200, headers={"ngrok-skip-browser-warning": "<>"})

@api_view(['POST'])
@permission_classes([AllowAny])
def github_webhook(request):
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.body, sig):
        return Response({"error": "Invalid signature"}, status=401)

    event = request.headers.get("X-GitHub-Event", "unknown")
    delivery = request.headers.get("X-GitHub-Delivery", "unknown")
    try:
        payload = request.data
    except Exception:
        payload = None

    # handle events
    print(f"Received event={event} delivery={delivery}")
    if event == "ping":
        return {"msg": "pong"}, 200
    if event in ["opened", "synchronize"]:
        print(json.dumps(payload, indent=2))

    return "", 204
