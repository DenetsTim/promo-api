import bcrypt
from fastapi import APIRouter, HTTPException, Depends

from .b2b_schema import BusinessSignInSchema, BusinessSignUpSchema
from .b2b_orm import BusinessORM

from ..database import PromoORM
from ..default_schema import RawPromoCreateSchema, PromoCreateSchema

from ..app import security


router = APIRouter(prefix="/api/business")


@security.set_subject_getter
def get_business_id_from_uid(uid: str) -> str:
    return uid


@router.post("/auth/sign-up")
async def sign_up(signUpData: BusinessSignUpSchema):
    inserted_id = await BusinessORM.create_business(signUpData)

    if inserted_id == -1:
        raise HTTPException(
            409, {"status": "error", "message": "Такой email уже зарегистрирован."})
    else:
        token = security.create_access_token(uid=str(inserted_id))
        return {"token": token, "company_id": inserted_id}


@router.post("/auth/sign-in")
async def sign_in(signInData: BusinessSignInSchema):
    business = await BusinessORM.find_by_email(signInData.email)

    if business and bcrypt.checkpw(signInData.password.get_secret_value().encode('utf-8'), business.password):
        token = security.create_access_token(uid=str(business.id))
        return {"token": token}
    raise HTTPException(
        401, {"status": "error", "message": "Неверный email или пароль."})


@router.post("/promo", dependencies=[Depends(security.access_token_required)])
async def create_promo(rawPromoCreateData: RawPromoCreateSchema, business_id: str | None = Depends(security.get_current_subject)):
    promo_id = await PromoORM.create_promo(PromoCreateSchema.create_from_raw(rawPromoCreateData), int(business_id))
    return {"id": promo_id}


@router.get("/promo")
async def get_promo(business_id: str | None = Depends(security.get_current_subject)):
    return {"id": business_id}
