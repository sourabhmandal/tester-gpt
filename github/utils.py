
import hmac
import hashlib
from testergpt.settings import settings

def verify_signature(request_body: bytes, signature_header: str) -> bool:
    """
    Verifies X-Hub-Signature-256 header using HMAC SHA256.
    signature_header example: "sha256=abcdef..."
    """
    if not signature_header:
        return False
    sha_name, signature = signature_header.split("=", 1)
    if sha_name != "sha256":
        return False
    mac = hmac.new(settings.GITHUB_SECRET, msg=request_body, digestmod=hashlib.sha256)
    expected = mac.hexdigest()
    # use hmac.compare_digest to avoid timing attacks
    return hmac.compare_digest(expected, signature)
