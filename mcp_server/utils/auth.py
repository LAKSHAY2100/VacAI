import os

import jwt
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken, TokenVerifier


class Auth0TokenVerifier(TokenVerifier):
    """Verifies Auth0-issued JWT access tokens using Auth0's JWKS."""

    def __init__(self, domain: str, audience: str):
        self.domain = domain
        self.audience = audience
        self.issuer = f"https://{domain}/"
        self.jwks_client = PyJWKClient(f"https://{domain}/.well-known/jwks.json")

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
        except jwt.PyJWTError:
            return None

        return AccessToken(
            token=token,
            client_id=claims.get("azp", claims.get("sub", "")),
            scopes=claims.get("scope", "").split(),
            expires_at=claims.get("exp"),
            subject=claims.get("sub"),
            claims=claims,
        )


def create_auth0_verifier() -> Auth0TokenVerifier:
    domain = os.getenv("AUTH0_DOMAIN")
    audience = os.getenv("RESOURCE_SERVER_URL")

    if not domain:
        raise ValueError("AUTH0_DOMAIN environment variable is required")
    if not audience:
        raise ValueError("RESOURCE_SERVER_URL environment variable is required")

    return Auth0TokenVerifier(domain=domain, audience=audience)
