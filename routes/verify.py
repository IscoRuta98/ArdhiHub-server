from fastapi import APIRouter

from models.verify import VerifyUser

verifyRouter = APIRouter(prefix="/verify")


# Verify Land Records
@verifyRouter.post("/third-party")
async def verify_land_record(data: VerifyUser):
    """
    Aim of this funciton is to accept verification by third
    party. Steps:
    1. Third party sends data to server
    2. Server fetchs metadata from algorand blockchain
    3. Metadata is decrypted and checked againts third party's data.
    4. If metadata matches
    """
    pass
