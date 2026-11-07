from dataclasses import dataclass
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError


class AgentAuthenticationError(Exception):
    """Agent authentication failed."""


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    roles: tuple[str, ...]
    issuer: str
    token_id: str


class JWTAgentVerifier:
    def __init__(
        self,
        public_key: str,
        issuer: str = "ai-a05-dev-issuer",
        audience: str = "ai-a05-governance",
    ):
        self.public_key = public_key
        self.issuer = issuer
        self.audience = audience

    def verify(self, token: str) -> AgentIdentity:
        if not token or not isinstance(token, str):
            raise AgentAuthenticationError("Missing token")

        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "require": [
                        "sub",
                        "iss",
                        "aud",
                        "exp",
                        "iat",
                        "jti",
                    ],
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                },
                leeway=0,
            )

            agent_id = claims["sub"]
            roles = claims.get("roles", [])
            token_id = claims["jti"]

            if not isinstance(agent_id, str) or not agent_id:
                raise ValueError("Invalid agent identity")

            if not isinstance(token_id, str) or not token_id:
                raise ValueError("Invalid token ID")

            if (
                not isinstance(roles, list)
                or not all(
                    isinstance(role, str) and bool(role)
                    for role in roles
                )
            ):
                raise ValueError("Invalid roles")

            return AgentIdentity(
                agent_id=agent_id,
                roles=tuple(roles),
                issuer=claims["iss"],
                token_id=token_id,
            )

        except (InvalidTokenError, ValueError, TypeError) as exc:
            raise AgentAuthenticationError(
                "Invalid agent authentication"
            ) from exc
