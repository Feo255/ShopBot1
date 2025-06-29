import os

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, async_session

from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(url=os.getenv('DB_URL'),
                             echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name:  Mapped[str] =  mapped_column(String(25), nullable=True)
    phone_number:  Mapped[str] = mapped_column(String(25), nullable=True)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))

class Card(Base):
    __tablename__ = 'cards'

    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[str] = mapped_column(String(256))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(256))
    price: Mapped[int]
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))

class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    card: Mapped[int] = mapped_column(ForeignKey('cards.id'))
    in_basket: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    bought: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    data: Mapped[str] = mapped_column(String(1024))

class Basket(Base):
    __tablename__ = 'baskets'

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int]= mapped_column(ForeignKey('users.id'))
    item: Mapped[int] = mapped_column(ForeignKey('items.id'))
    card: Mapped[int] = mapped_column(ForeignKey('cards.id'))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




