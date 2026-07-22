import os
from fastapi import Header, HTTPException, status


def verify_token(x_api_token: str = Header(...)) -> None:
    expected = os.environ.get("ML_API_TOKEN", "")
    if not expected or x_api_token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")
