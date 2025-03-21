from enum import Enum
from typing import Optional

from odmantic import Model
from pydantic import BaseModel


class Role(str, Enum):
    TOKEN_ISSUER = "token_issuer"
    TOKEN_HOLDER = "token_holder"


class User(Model):
    username: str
    hash_password: str
    first_name: str
    surname: str
    national_id: int
    phone_number: str
    algorand_address: str
    algorand_encrypted_private_key: str
    role: Role
    file_id: Optional[str] = None
    disabled: bool = False


class CreateUser(BaseModel):
    username: str
    password: str
    first_name: str
    surname: str
    national_id: int
    phone_number: str
    role: Role


class LoginUser(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None
