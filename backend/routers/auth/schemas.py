from typing import Optional, Union, List
from pydantic import BaseModel


class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload model"""
    sub: Optional[int] = None


class TokenData(BaseModel):
    """Token data model"""
    username: Union[str, None] = None


class TokenDataScope(TokenData):
    """Token data model with scope"""
    scopes: List[str] = []


class Message(BaseModel):
    msg: str
