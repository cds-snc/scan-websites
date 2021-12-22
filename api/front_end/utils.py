from os import getenv
from urllib.parse import urljoin, urlparse


# Only allow redirects to the same domain to prevent open Redirect vulnerabilities
def is_safe_redirect_url(target):
    host = getenv("DOMAIN_NAME", "localhost:8000")
    host_url = urlparse(f"http://{host}")
    redirect_url = urlparse(urljoin(host, target))
    return (
        redirect_url.scheme in ("http", "https")
        and host_url.netloc == redirect_url.netloc
    )
