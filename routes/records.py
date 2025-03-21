from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from config.database import engine
from models.auth import User
from models.records import Record
from services.auth import get_current_active_user
from services.upload import upload_file_to_bucket
from services.algorand import create_asa, opt_in_to_asa, revoke_asa, transfer_asa
from services.crypto import decrypt_data

recordsRouter = APIRouter(prefix="/records")


# POST Create Land deed Records
@recordsRouter.post("/create-record")
async def create_record(
    current_user: Annotated[User, Depends(get_current_active_user)],
    location: str,
    file: UploadFile = File(...),
):
    """
    Create Land record. This endpoint is supposed to create an unverified
    record. Steps:
    1. User sends land record (pdf) with metadata (name, location, etc)
    2. Save user info. Save status of verified to false
    3. If saved successfully, save the pdf document in AWS S3 bucket
    """

    # Upload object to S3 bucket
    try:
        file_url = upload_file_to_bucket(file_obj=file)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file to S3 bucket. {e}",
        )

    # Save record to database
    save_file = Record(
        location=location,
        file_url=file_url,
        verified=False,
        user_id=str(current_user.id),
    )

    user = engine.find_one(User, User.id == current_user.id)
    if user:
        user.file_id = str(save_file.id)
        await engine.save(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error saving record. Please try again.",
        )
    return save_file


# GET Fetch all unverified land deeds
@recordsRouter.get("/fetch-unverified-records")
async def fetch_all_unverified_records(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Fetch all unverified land records
    1. Check user is token issuer
    2. Fetch all unverified users
    """
    if current_user.role != "token_issuer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorised to access this resource.",
        )

    records = await engine.find(Record, Record.verified == False)
    return records


# GET Fetch record
@recordsRouter.get("/fetch-record")
async def fetch_all_records(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Fetch a single record
    1. Check user is token issuer
    2. Fetch record
    """
    if current_user.role != "token_issuer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorised to access this resource.",
        )

    record = await engine.find(Record)
    return record


# POST Verify land record and create NFT on Algorand blockcahin
@recordsRouter.post("/issue-record", status_code=status.HTTP_201_CREATED)
async def issue_digital_land_record(
    current_user: Annotated[User, Depends(get_current_active_user)], land_holder_id: str
):
    """
    Verify and Create tokenised version of land record.
    1. Check user is token issuer
    2. Once checked, create ASA representing land record
    3. Land Holder opts-in to ASA
    4. Transfer ASA to land holder
    """
    if current_user.role != "token_issuer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorised to access this resource.",
        )

    land_holder = await engine.find_one(User, User.id == land_holder_id)
    if not land_holder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land holder not found.",
        )

    land_holder_record = await engine.find_one(Record, Record.user_id == land_holder_id)
    if not land_holder_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land holder record not found.",
        )

    # Create ASA
    asset_id = create_asa(
        private_key=decrypt_data(current_user.algorand_encrypted_private_key.encode()),
        creator_address=current_user.algorand_address,
        asset_name=f"{land_holder.first_name}_{land_holder.surname}_{land_holder_record.location}",
        unit_name=f"{land_holder.first_name}_{land_holder.surname}_{land_holder_record.location}",
        total=1,  # Algorand configiration for NFT
        decimals=0,  # Algorand configuration for NFT
        url=land_holder_record.file_url,
    )

    # Land owner opts-in to ASA
    opt_in_to_asa(
        private_key=decrypt_data(land_holder.algorand_encrypted_private_key.encode()),
        address=land_holder.algorand_address,
        asset_id=asset_id,
    )

    # Transfer ASA to land holder
    transaction_id = transfer_asa(
        private_key=decrypt_data(current_user.algorand_encrypted_private_key.encode()),
        sender_address=current_user.algorand_address,
        receiver_address=land_holder.algorand_address,
        asset_id=asset_id,
        amount=1,
    )

    # save transaction id to Record document
    land_holder_record.transaction_id = transaction_id
    land_holder_record.verified = True
    await engine.save(land_holder_record)

    return land_holder_record


# POST Revoke Land record token
@recordsRouter.get("/revoke-token", status_code=status.HTTP_200_OK)
async def revoke_token(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_id: str,
):
    """
    Revoke user's ASA representaiton of land record.
    1. Check user is token issuer.
    2. Token issuer initiates a clawback transaction.
    """
    if current_user.role != "token_issuer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorised to access this resource.",
        )

    land_holder = await engine.find_one(User, User.id == user_id)

    if not land_holder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land holder not found.",
        )

    land_holder_record = await engine.find_one(Record, Record.user_id == user_id)
    if not land_holder_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land holder record not found.",
        )

    # Revoke ASA
    revoke_txid = revoke_asa(
        private_key=decrypt_data(current_user.algorand_encrypted_private_key.encode()),
        clawback_address=current_user.algorand_address,
        asset_id=land_holder_record.asset_id,
        holder_address=land_holder.algorand_address,
        amount=1,
    )

    # save revoke transaction id to Record document
    land_holder_record.revoke_transaction_id = revoke_txid
    land_holder_record.is_land_revoked = True
    await engine.save(land_holder_record)

    return {"detail": "Asset Revoked", "transaction_id": revoke_txid}
