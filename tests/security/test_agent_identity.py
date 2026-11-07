from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from src.identity.jwt_verifier import (
    JWTAgentVerifier,
    AgentAuthenticationError,
)


@pytest.fixture
def keys():
    private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem, public_pem


def make_token(private_key, **overrides):
    now = datetime.now(timezone.utc)

    claims = {
        "sub": "finance-agent",
        "iss": "ai-a05-dev-issuer",
        "aud": "ai-a05-governance",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": str(uuid4()),
        "roles": ["finance"],
    }

    claims.update(overrides)

    return jwt.encode(
        claims,
        private_key,
        algorithm="RS256",
    )


def test_valid_agent_identity(keys):
    private, public = keys
    token = make_token(private)

    identity = JWTAgentVerifier(public).verify(token)

    assert identity.agent_id == "finance-agent"
    assert identity.roles == ("finance",)


def test_missing_token_rejected(keys):
    _, public = keys

    with pytest.raises(AgentAuthenticationError):
        JWTAgentVerifier(public).verify("")


def test_expired_token_rejected(keys):
    private, public = keys

    token = make_token(
        private,
        exp=datetime.now(timezone.utc)
        - timedelta(minutes=1),
    )

    with pytest.raises(AgentAuthenticationError):
        JWTAgentVerifier(public).verify(token)


def test_wrong_audience_rejected(keys):
    private, public = keys

    token = make_token(private, aud="another-service")

    with pytest.raises(AgentAuthenticationError):
        JWTAgentVerifier(public).verify(token)


def test_wrong_issuer_rejected(keys):
    private, public = keys

    token = make_token(private, iss="untrusted-issuer")

    with pytest.raises(AgentAuthenticationError):
        JWTAgentVerifier(public).verify(token)


def test_invalid_signature_rejected(keys):
    _, public = keys

    attacker_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    attacker_private = attacker_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    token = make_token(attacker_private)

    with pytest.raises(AgentAuthenticationError):
        JWTAgentVerifier(public).verify(token)


def test_unsigned_token_rejected(keys):
    _, public = keys

    token = jwt.encode(
        {"sub": "finance-agent"},
        key="",
        algorithm="none",
    )

    with pytest.raises(AgentAuthenticationError):
        JWTAgentVerifier(public).verify(token)


def test_invalid_roles_rejected(keys):
    private, public = keys

    token = make_token(private, roles="administrator")

    with pytest.raises(AgentAuthenticationError):
        JWTAgentVerifier(public).verify(token)
