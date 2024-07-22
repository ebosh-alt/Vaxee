from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery

from data.config import bonus_system, bot, db, COUNT_REFERRAL, AMOUNT_REFERRAL_KING, COIN_REFERRAL_KING, AMOUNT_INVEST, \
    AMOUNT_PROFIT_INVEST, COIN_PROFIT_INVEST, channel, COIN_FOLLOW_NEWS, AMOUNT_FOLLOW_NEWS
from service.GetMessage import get_mes
from service.keyboards import Keyboards as kb

router = Router()


@router.message(F.text == "🗒️ Задания")
async def start_task(message: Message):
    await message.answer(
        text="Выполняй задания и зарабатывай",
        reply_markup=kb.task_menu_kb)


@router.callback_query(F.data == "tasks")
async def start_task(message: Message):
    await message.message.answer(
        text="Выполняй задания и зарабатывай",
        reply_markup=kb.task_menu_kb)


@router.callback_query(F.data == "referral_king")
async def referral_king_callback(message: CallbackQuery):
    id = message.from_user.id
    statuses = bonus_system.get_statuses(id)
    keyboard = kb.referral_king_receive_kb
    user = db.get_profile(message.from_user.id)
    count_referral = user[2]
    # if count_referral < COUNT_REFERRAL:
    #     await message.message.answer("✅ Бонус получен и начислен на Ваш баланс")
    # elif statuses.referral_king:
    #     await message.message.answer(text="❌ Бонус уже получен")
    #
    # else:
    await message.message.answer(text=get_mes("referral_king", count=count_referral),
                                 reply_markup=keyboard)


@router.callback_query(F.data == "profit_invest")
async def profit_invest_callback(message: CallbackQuery):
    id = message.from_user.id
    statuses = bonus_system.get_statuses(id)
    keyboard = kb.profit_invest_receive_kb
    user = db.get_profile(message.from_user.id)
    invest = float(user[5])
    # if invest < AMOUNT_INVEST:
    #     await message.message.answer("✅ Бонус получен и начислен на Ваш баланс")
    # elif statuses.profit_invest:
    #     await message.message.answer(text="❌ Бонус уже получен")
    # else:
    await message.message.answer(text=get_mes("profit_invest", invest=invest),
                                 reply_markup=keyboard)


@router.callback_query(F.data == "follow_news")
async def follow_news_callback(message: CallbackQuery):
    id = message.from_user.id
    statuses = bonus_system.get_statuses(id)
    keyboard = kb.follow_news_receive_kb
    user_channel_status = await bot.get_chat_member(chat_id=channel, user_id=id)
    # if user_channel_status.status == "left":
    #     await message.message.answer("✅ Бонус получен и начислен на Ваш баланс")
    #
    # elif statuses.follow_news:
    #     await message.message.answer(text="❌ Бонус уже получен")
    # else:
    await message.message.answer(text=get_mes("follow_news"),
                                 reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data == "receive_referral_king")
async def receive_referral_king(message: CallbackQuery):
    id = message.from_user.id
    user = db.get_profile(message.from_user.id)
    count_referral = int(user[2])
    statuses = bonus_system.get_statuses(id)

    if statuses.referral_king:
        await message.message.answer(text="❌ Бонус уже получен")
        return
    if count_referral >= COUNT_REFERRAL:
        coin = float(user[11]) + COIN_REFERRAL_KING
        amount = float(user[7]) + AMOUNT_REFERRAL_KING
        bonus_system.award(id, amount, coin)
        bonus_system.update_referral_king(id)
        await message.message.answer("✅ Бонус получен и начислен на Ваш баланс")

    else:
        await message.message.answer(text="❌ Вы не выполнили данное задание")


@router.callback_query(F.data == "receive_profit_invest")
async def receive_profit_invest(message: CallbackQuery):
    id = message.from_user.id
    user = db.get_profile(message.from_user.id)
    invest = float(user[5])
    statuses = bonus_system.get_statuses(id)
    if statuses.profit_invest:
        await message.message.answer(text="❌ Бонус уже получен")
        return
    if invest >= AMOUNT_INVEST:
        coin = float(user[11]) + COIN_PROFIT_INVEST
        amount = float(user[7]) + AMOUNT_PROFIT_INVEST
        bonus_system.award(id, amount, coin)
        bonus_system.update_profit_invest(id)
        await message.message.answer("✅ Бонус получен и начислен на Ваш баланс")

    else:
        await message.message.answer(text="❌ Вы не выполнили данное задание")


@router.callback_query(F.data == "receive_follow_news")
async def receive_follow_news(message: CallbackQuery):
    id = message.from_user.id
    user_channel_status = await bot.get_chat_member(chat_id=channel, user_id=id)
    statuses = bonus_system.get_statuses(id)
    if statuses.follow_news:
        await message.message.answer(text="❌ Бонус уже получен")
        return
    if user_channel_status.status != "left":
        user = db.get_profile(message.from_user.id)
        coin = float(user[11]) + COIN_FOLLOW_NEWS
        amount = float(user[7]) + AMOUNT_FOLLOW_NEWS
        bonus_system.award(id, amount, coin)
        bonus_system.update_follow_news(id)
        await message.message.answer("✅ Бонус получен и начислен на Ваш баланс")

    else:
        await message.message.answer(text="❌ Вы не выполнили данное задание")


tasks_router = router
