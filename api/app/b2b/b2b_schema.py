from pydantic import Field

from ..default_schema import AccountSignInSchema


class BusinessSignInSchema(AccountSignInSchema):
    pass


class BusinessSignUpSchema(BusinessSignInSchema):
    name: str = Field(min_length=5, max_length=50)


class BusinessSchema(BusinessSignUpSchema):
    id: int = Field(ge=1)
