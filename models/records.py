from enum import Enum
from typing import Optional

from fastapi import File, UploadFile
from odmantic import Model
from pydantic import BaseModel


class Record(Model):
    location: str
    file_url: str
    verified: bool
    user_id: str
    transaction_id: Optional[str] = None
    asset_id: Optional[int] = None
    revoke_transaction_id: Optional[str] = None
    is_land_revoked: bool = False
