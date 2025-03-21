from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models.auth import CreateUser, Token, User
from services.algorand import generate_algorand_keypair
from services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    engine,
    get_current_active_user,
    get_password_hash,
)
from services.crypto import encrypt_data

authRouter = APIRouter(prefix="/auth")


# POST Register new user
@authRouter.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_User(data: CreateUser):

    user_exist = await engine.find_one(User, User.username == data.username)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists."
        )

    # Password hashing
    hash_password = get_password_hash(data.password)

    # Generate Algorand keypair
    private_key, address = generate_algorand_keypair()

    # Encrypt the private key
    encrypted_private_key = encrypt_data(private_key)

    # Create user instance
    save_user = User(
        username=data.username,
        first_name=data.first_name,
        surname=data.surname,
        hash_password=hash_password,
        national_id=data.national_id,
        phone_number=data.phone_number,
        algorand_address=address,
        algorand_encrypted_private_key=encrypted_private_key.decode(),  # Store as string
        role=data.role,
    )

    await engine.save(save_user)
    return save_user


@authRouter.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@authRouter.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


# @userRouter.get(base + "get_user_info", response_model=User)
# async def get_user_info(username: str):
#     current_user = await get_user(username=username)
#     if not current_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )
#     return current_user
