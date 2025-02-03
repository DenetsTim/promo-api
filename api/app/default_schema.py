from pydantic import BaseModel, Field, EmailStr, SecretStr, AnyUrl, field_serializer, field_validator, model_validator
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
import bcrypt
from datetime import date

from fastapi import HTTPException


class AccountSignInSchema(BaseModel):
    email: EmailStr = Field(min_length=8, max_length=120)

    password: SecretStr = Field(min_length=8, max_length=60)

    @field_serializer("password")
    def dump_password(self, v: SecretStr):
        return bcrypt.hashpw(v.get_secret_value().encode('utf-8'), bcrypt.gensalt())

    @field_validator("password")
    @classmethod
    def check_password(cls, value: SecretStr):
        v = value.get_secret_value()
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v) or not any(c in punctuation for c in v) or any(c not in ascii_lowercase + ascii_uppercase + digits + punctuation for c in v):
            raise HTTPException(
                400, {"status": "error", "message": "Пароль должен содержать латинские буквы, хотя бы одну заглавную, одну строчную, одну цифру и специальные символы."})
        return value


class TargetSchema(BaseModel):
    age_from: int = Field(ge=0, le=100, default=0)
    age_until: int = Field(ge=0, le=100, default=100)
    country: str = Field(min_length=2, max_length=2, default="")
    categories: list[str] = Field(max_length=20, default=[])

    @model_validator(mode="after")
    def check_age(self):
        if self.age_until < self.age_from:
            raise HTTPException(
                400, {"status": "error", "message": "Дата окончания меньше даты начала"})
        return self


class PromoCreateSchema(BaseModel):
    description: str = Field(min_length=10, max_length=300)
    image_url: AnyUrl | None = Field(max_length=350, default=None)

    target_age_from: int = Field(ge=0, le=100, default=0)
    target_age_until: int = Field(ge=0, le=100, default=100)
    target_country: str = Field(max_length=2, default="")
    target_categories: list[str] = Field(max_length=20, default=[])

    max_count: int = Field(ge=0, le=100000000)
    active_from: date = Field(default=date.min)
    active_until: date = Field(default=date.max)

    mode: str = Field(min_length=6, max_length=6)
    promo_common: str = Field(max_length=30, default="")
    promo_unique: list[str] = Field(max_length=5000, default=[])

    @model_validator(mode="before")
    @classmethod
    def fill_target_data(cls, values):
        if values.get("target") is None:
            raise HTTPException(
                400, {"status": "error", "message": "Отсутствует таргет"})

        return values | {"target_" + k: v for k, v in TargetSchema.model_validate(values.get("target")).model_dump().items()}

    @model_validator(mode="after")
    def check_promo(self):
        if (self.mode != "COMMON" and self.mode != "UNIQUE") or (self.mode == "COMMON" and (self.promo_unique or not self.promo_common)) or (self.mode == "UNIQUE" and (self.promo_common or not self.promo_unique)):
            raise HTTPException(
                400, {"status": "error", "message": "Некорректный тип промокода"})
        if self.mode == "UNIQUE":
            self.max_count = 1
        return self

    @field_serializer("image_url")
    @classmethod
    def serialize_avatar_url(cls, v: AnyUrl | None):
        return str(v) if v else ""
