from app.database.models import async_session, User, Item, Basket, Category, Card
from sqlalchemy import select, update, delete

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            return False
    return True if user.name else False

async def get_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def update_user(tg_id, name, phone_number):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(name=name, phone_number=phone_number))
        await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_cards_by_category(category_id):
    async with async_session() as session:
        return await session.scalars(select(Card).where(Card.category == category_id))

async def get_card(card_id):
    async with async_session() as session:
        return await session.scalar(select(Card).where(Card.id == card_id))

async def add_item_to_basket(tg_id, card_id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.card == card_id, Item.in_basket == False, Item.bought == False))
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(Basket(user=user.id, item=item.id))
        item.in_basket = True
        await session.commit()
