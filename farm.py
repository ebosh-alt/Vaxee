import datetime
import asyncio
from entity.database import database

db = database("data/users.db")


async def sleep_until_next_minute():
    now = datetime.datetime.now()
    next_minute = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
    sleep_seconds = (next_minute - now).total_seconds()
    await asyncio.sleep(sleep_seconds)


async def accruing():
    while True:
        await sleep_until_next_minute()  # Спим до начала следующей минуты
        current_date = datetime.datetime.now().strftime('%M')
        if current_date == '00':
            users = db.get_accruing()
            if users:
                for userId, doxod in users:
                    db.accruing(userId, round(float(doxod) / 24, 2))
            await asyncio.sleep(600)  # 10 минут
        else:
            await asyncio.sleep(30)  # проверка каждые 30 секунд


def run_accruing():
    asyncio.run(accruing())

