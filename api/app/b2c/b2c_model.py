from ..database import AccountModel, Mapped, mapped_column, String, Integer


class UserModel(AccountModel):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(100))
    surname: Mapped[str] = mapped_column(String(120))

    avatar_url: Mapped[str] = mapped_column(String(350))

    user_age: Mapped[int] = mapped_column(Integer)
    user_country: Mapped[str] = mapped_column(String(2))
