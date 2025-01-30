from .b2b_model import BusinessModel
from .b2b_schema import BusinessSignUpSchema
from ..database import AccountORM


class BusinessORM(AccountORM):
    model = BusinessModel

    @classmethod
    async def create_business(cls, business: BusinessSignUpSchema) -> int:
        return await cls.create_account(**business.model_dump())
