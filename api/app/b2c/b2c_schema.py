from pydantic import Field, field_validator, field_serializer, BaseModel, AnyUrl

from ..default_schema import AccountSignInSchema


class UserSignInSchema(AccountSignInSchema):
    pass


class RawUserSignUpSchema(UserSignInSchema):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=120)

    avatar_url: AnyUrl | None = Field(max_length=350, default=None)

    class Other(BaseModel):
        age: int = Field(ge=0, le=100)
        country: str = Field(min_length=2, max_length=2)

        @field_validator("country")
        @classmethod
        def validate_country(cls, country: str) -> str:
            return country.upper()

    other: Other = Field()


class UserSignUpSchema(UserSignInSchema):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=120)

    avatar_url: AnyUrl | None = Field(max_length=350, default=None)

    user_age: int = Field(ge=0, le=100)
    user_country: str = Field(min_length=2, max_length=2)

    @classmethod
    def create_from_raw(cls, raw: RawUserSignUpSchema):
        data = raw.model_dump(exclude={'password', 'other'})
        data['password'] = raw.password.get_secret_value()
        data['user_age'] = raw.other.age
        data['user_country'] = raw.other.country
        return cls.model_validate(data)

    @field_serializer("avatar_url")
    @classmethod
    def serialize_avatar_url(cls, v: AnyUrl | None):
        return str(v) if v else ""


class UserSchema(UserSignUpSchema):
    id: int = Field(ge=1)
