from enum import Enum

from odmantic import Model
from pydantic import BaseModel


class VerifyUser(BaseModel):
    first_name: str
    surname: str
    company_name: str
    email: str
    national_id: int


class ThirdPartyUser(Model):
    pass
