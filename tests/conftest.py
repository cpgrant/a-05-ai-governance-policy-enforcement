from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


@pytest.fixture
def agent_token(tmp_path, monkeypatch):
    private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    public_path = tmp_path / "public.pem"
    public_path.write_bytes(public_pem)

    monkeypatch.setenv(
        "A05_JWT_PUBLIC_KEY",
        str(public_path),
    )

    def create_token(subject="finance-agent", roles=None):
        now = datetime.now(timezone.utc)

        return jwt.encode(
            {
                "sub": subject,
                "iss": "ai-a05-dev-issuer",
                "aud": "ai-a05-governance",
                "iat": now,
                "exp": now + timedelta(minutes=5),
                "jti": str(uuid4()),
                "roles": ["finance"] if roles is None else roles,
            },
            private,
            algorithm="RS256",
        )

    return create_token
