from os import getenv
import datetime

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Date, DateTime, LargeBinary, Integer
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .default_schema import PromoCreateSchema


class BaseModel(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class AccountModel(BaseModel):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(50))

    password: Mapped[str] = mapped_column(LargeBinary(72))


class PromoModel(BaseModel):
    __tablename__ = "promo"
    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("business.id"))

    mode: Mapped[str] = mapped_column(String(6))
    promo_common: Mapped[str] = mapped_column(String(30))
    promo_unique: Mapped[list[str]] = mapped_column(ARRAY(String(30)))

    description: Mapped[str] = mapped_column(String(300))
    image_url: Mapped[str] = mapped_column(String(350))

    max_count: Mapped[int] = mapped_column(Integer)
    active_from: Mapped[datetime.date] = mapped_column(Date)
    active_until: Mapped[datetime.date] = mapped_column(Date)

    target_age_from: Mapped[int] = mapped_column(Integer)
    target_age_until: Mapped[int] = mapped_column(Integer)
    target_country: Mapped[str] = mapped_column(String(2))
    target_categories: Mapped[list[str]] = mapped_column(ARRAY(String(20)))


class BaseORM:
    model = None

    @classmethod
    async def find_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def _add(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance


class AccountORM(BaseORM):
    model = AccountModel

    @classmethod
    async def find_by_id(cls, id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == id)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_by_email(cls, email: str):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.email == email)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def create_account(cls, **values) -> int:
        try:
            account = await cls._add(**values)
            return account.id
        except IntegrityError:
            return -1
        except SQLAlchemyError as e:
            raise e


class PromoORM(BaseORM):
    model = PromoModel

    @classmethod
    async def find_by_id(cls, id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == id)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_by_business_id(cls, business_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.business_id == business_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def create_promo(cls, promoCreateData: PromoCreateSchema, business_id: int) -> int:
        try:
            promo = await cls._add(**promoCreateData.model_dump(), business_id=business_id)
            return promo.id
        except SQLAlchemyError as e:
            raise e


engine = create_async_engine("postgresql+asyncpg:" + ":".join(getenv(
    "POSTGRES_CONN", "postgres://postgres:12345@localhost:5432/postgres").split(":")[1:]))
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
