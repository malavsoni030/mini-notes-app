import os
from pathlib import Path
from typing import Optional
import uuid
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWKClient

# Locate and load the backend/.env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Read SUPABASE_URL from the environment and raise a clear error if missing
SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL environment variable is missing. Please set it in backend/.env"
    )

# Normalize URL by removing any trailing slashes
SUPABASE_URL = SUPABASE_URL.strip().rstrip("/")

# JWKS endpoint and token validation configuration
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
ISSUER = f"{SUPABASE_URL}/auth/v1"
AUDIENCE = "authenticated"
ALGORITHM = "ES256"

# Create the PyJWKClient once and reuse it across requests
jwks_client = PyJWKClient(JWKS_URL)

# HTTPBearer extracts the Bearer token from the Authorization header.
# auto_error=False allows us to return a 401 status code instead of 403 on missing credentials.
security = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> uuid.UUID:
    """
    FastAPI dependency to extract and verify the JWT Bearer token from the Authorization header.
    - Validates signature against Supabase JWKS using ES256 algorithm.
    - Verifies audience ('authenticated'), issuer ({SUPABASE_URL}/auth/v1), and expiration.
    - Returns the token's 'sub' claim as a Python UUID.
    - Returns HTTP 401 if token is missing, invalid, or expired.
    - Never logs or prints tokens for security.
    """
    # 1. Check if token was provided in the Authorization header
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 2. Verify token signature, issuer, audience, and expiration
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
            issuer=ISSUER,
            options={"verify_exp": True},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {type(exc).__name__}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Extract and parse the subject claim ("sub") as a UUID
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing subject claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject claim is not a valid UUID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
