import bcrypt
from fastapi import APIRouter, HTTPException, Depends

from .b2c_schema import UserSignInSchema, UserSignUpSchema, RawUserSignUpSchema
from ..app import security

from .b2c_orm import UserORM


router = APIRouter(prefix="/api/user")


@router.post("/auth/sign-up")
async def sign_up(rawSignUpData: RawUserSignUpSchema):
    inserted_id = await UserORM.create_user(UserSignUpSchema.create_from_raw(rawSignUpData))

    if inserted_id == -1:
        raise HTTPException(
            409, {"status": "error", "message": "Такой email уже зарегистрирован."})
    else:
        token = security.create_access_token(uid=str(inserted_id))
        return {"token": token}


@router.post("/auth/sign-in")
async def sign_in(signInData: UserSignInSchema):
    user = await UserORM.find_by_email(signInData.email)

    if user and bcrypt.checkpw(signInData.password.get_secret_value().encode('utf-8'), user.password):
        token = security.create_access_token(uid=str(user.id))
        return {"token": token}
    raise HTTPException(
        401, {"status": "error", "message": "Неверный email или пароль."})


@router.post("/promo")
async def create_promo(user_id: str | None = Depends(security.get_current_subject)):
    return {"id": user_id}


@router.get("/promo")
async def get_promo(user_id: str | None = Depends(security.get_current_subject)):
    return {"id": user_id}
