import asyncio
import logging
from contextlib import suppress

from data.config import dp, bot
from farm import run_accruing
from handlers.conclusion import conclusion_rt
from handlers.tasks import tasks_router
from service import middleware
from handlers.bot import bot_router
from multiprocessing import Process

from wallet_bot import run_wallet_bot


async def main():
    accruing_processes = Process(target=run_accruing)
    accruing_processes.start()

    wallet_processes = Process(target=run_wallet_bot)
    wallet_processes.start()

    dp.include_routers(tasks_router)
    dp.include_routers(conclusion_rt)
    dp.include_router(bot_router)
    dp.update.middleware(middleware.Logging())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        # filename="log.logging",
        format=u'%(filename)s:%(lineno)d #%(levelname)-3s [%(asctime)s] - %(message)s',
        filemode="w",
        encoding='utf-8')

    with suppress(KeyboardInterrupt):
        asyncio.run(main())
