"""Cryptographic utilities for OAuth 2.1 implementation."""

import secrets
import hashlib
import base64
from typing import Tuple


def generate_secure_token() -> str:
    """Generate cryptographically secure bearer token."""
    random_bytes = secrets.token_bytes(32)
    token = base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')
    return f"oauth_{token}"


def generate_authorization_code() -> str:
    """Generate cryptographically secure authorization code."""
    random_bytes = secrets.token_bytes(24)
    code = base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')
    return f"code_{code}"


def generate_pkce_verifier() -> str:
    """Generate PKCE code verifier (43-128 characters)."""
    random_bytes = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')


def generate_pkce_challenge(verifier: str, method: str = "S256") -> str:
    """Generate PKCE code challenge from verifier."""
    if method == "S256":
        digest = hashlib.sha256(verifier.encode('ascii')).digest()
        return base64.urlsafe_b64encode(digest).decode('ascii').rstrip('=')
    elif method == "plain":
        return verifier
    else:
        raise ValueError(f"Unsupported PKCE method: {method}")


def verify_pkce_challenge(code_verifier: str, code_challenge: str, method: str = "S256") -> bool:
    """Verify PKCE code challenge against verifier."""
    try:
        expected_challenge = generate_pkce_challenge(code_verifier, method)
        return secrets.compare_digest(expected_challenge, code_challenge)
    except Exception:
        return False


def generate_state_parameter() -> str:
    """Generate state parameter for OAuth flow."""
    random_bytes = secrets.token_bytes(16)
    return base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')


def simple_encrypt(plaintext: str, key: str) -> str:
    """Simple XOR encryption for storing API keys (not production-grade)."""
    # This is a simple obfuscation for the PoC - in production use proper encryption
    key_bytes = key.encode('utf-8')
    plaintext_bytes = plaintext.encode('utf-8')
    
    # Repeat key to match plaintext length
    extended_key = (key_bytes * ((len(plaintext_bytes) // len(key_bytes)) + 1))[:len(plaintext_bytes)]
    
    # XOR encryption
    encrypted_bytes = bytes(a ^ b for a, b in zip(plaintext_bytes, extended_key))
    return base64.b64encode(encrypted_bytes).decode('ascii')


def simple_decrypt(encrypted: str, key: str) -> str:
    """Simple XOR decryption for stored API keys."""
    try:
        encrypted_bytes = base64.b64decode(encrypted.encode('ascii'))
        key_bytes = key.encode('utf-8')
        
        # Repeat key to match encrypted length
        extended_key = (key_bytes * ((len(encrypted_bytes) // len(key_bytes)) + 1))[:len(encrypted_bytes)]
        
        # XOR decryption
        decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, extended_key))
        return decrypted_bytes.decode('utf-8')
    except Exception:
        # If decryption fails, assume it's not encrypted (backwards compatibility)
        return encrypted