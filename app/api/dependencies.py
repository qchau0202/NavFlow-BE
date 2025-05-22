"""
Common dependencies for API endpoints
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Generator

async def verify_api_key(x_api_key: str = Header(None)):
    """
    Verify API key for protected endpoints
    In production, implement proper API key validation
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    # TODO: Implement proper API key validation
    return x_api_key 