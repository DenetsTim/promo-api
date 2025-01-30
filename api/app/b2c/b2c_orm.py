from .b2c_model import UserModel
from .b2c_schema import UserSignUpSchema
from ..database import AccountORM


class UserORM(AccountORM):
    model = UserModel

    @classmethod
    async def create_user(cls, user: UserSignUpSchema) -> int:
        return await cls.create_account(**user.model_dump())
