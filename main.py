import os
import asyncio
import logging
from aiogram import Bot, Dispatcher

from app.database.models import async_main
from app.client import client

from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO,
                    )

async def main():
    
    bot = Bot(token=os.getenv('TG_TOKEN'))

    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    redis_db = os.getenv('REDIS_DB')
    
    redis = await aioredis.from_url(f'redis://{redis_host}:{redis_port}/{redis_db}')
    dp= Dispatcher(storage=RedisStorage(redis))
    dp.include_router(client)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)

async def startup(dispatcher: Dispatcher):
    await async_main()
    logging.info('Bot started up...')
    
async def shutdown(dispatcher: Dispatcher):
    logging.info('Bot is shutting down...')

if __name__ == '__main__':
    try :
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Bot stopped')