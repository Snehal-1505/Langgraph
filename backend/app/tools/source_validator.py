import ipaddress
import re
import socket
from urllib.parse import urlparse
from typing import Tuple, Optional


# Blocked IP ranges (RFC 1918, Loopback, Link-Local, etc.)
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local
    ipaddress.ip_network("0.0.0.0/8"),        # This network
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]


def is_safe_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a URL is safe to fetch and protects against SSRF attacks.
    Returns (is_safe, error_reason).
    """
    if not url or not isinstance(url, str):
        return False, "Empty or invalid URL"

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL parsing: {str(e)}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported scheme: {parsed.scheme}. Only HTTP/HTTPS are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL lacks a valid hostname."

    hostname_lower = hostname.lower()
    if hostname_lower in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return False, "Access to localhost or loopback is blocked."

    if hostname_lower.endswith(".internal") or hostname_lower.endswith(".local"):
        return False, "Access to local domain is blocked."

    # Resolve hostname to verify IP
    try:
        ip_addresses = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in ip_addresses:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            for network in BLOCKED_IP_NETWORKS:
                if ip_obj in network:
                    return False, f"Destination IP {ip_str} is within private/restricted network."
    except socket.gaierror:
        # Hostname cannot be resolved
        return False, f"Hostname {hostname} could not be resolved."
    except Exception as e:
        return False, f"Resolution error: {str(e)}"

    return True, None


def sanitize_web_content(content: str, max_chars: int = 15000) -> str:
    """
    Sanitize fetched web content to prevent prompt injection and bound token usage.
    """
    if not content:
        return ""

    # Truncate to maximum characters
    text = content[:max_chars]

    # Neutralize common prompt injection attempt patterns
    injection_patterns = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
        r"(?i)<system>.*?</system>",
        r"(?i)system\s+prompt:",
        r"(?i)print\s+environment\s+variables",
        r"(?i)disregard\s+the\s+above",
    ]

    for pattern in injection_patterns:
        text = re.sub(pattern, "[FILTERED_SUSPICIOUS_CONTENT]", text)

    # Normalize excessive newlines and whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
