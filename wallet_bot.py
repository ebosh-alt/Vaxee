import asyncio

from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from entity.database import database

"""Настройки бота"""
token = '7208034029:AAHMGvFbBnbjyUDm7aDDrQ0uqhrJ6CyP6uQ'
info_link = 'https://telegra.ph/VaxCoin-informaciya-06-19'
""""""

bot = Bot(token)
dp = Dispatcher()
db = database("data/users.db")


@dp.message(Command('start'))
async def start(message: Message):
    user = db.is_register(message.from_user.id)
    if user:
        row1 = [InlineKeyboardButton(text='💸 Баланс VaxCoin', callback_data='balance')]
        row2 = [InlineKeyboardButton(text='💵 Вывести', callback_data='cash_out'),
                InlineKeyboardButton(text='⁉️ Как заработать токены', url=info_link)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
        await message.answer(
            f'💫| Начинай одним из первых зарабатывать токены <b>VaxCoin</b>\n\n💸| Чтобы обменять их после листинга на наш криптотокен и продать на бирже <a href="https://habrastorage.org/webt/1g/ma/ub/1gmaubhrtcfm8t6enwfgvkuypag.jpeg">⠀</a>',
            parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer(f'Вы еще не зарегистрированы в <a href="https://t.me/Vaxee_bot">Vaxee</a>',
                             parse_mode='HTML', disable_web_page_preview=True)


@dp.callback_query(F.data.in_(['menu']))
async def menu(callback: CallbackQuery):
    await callback.message.delete()
    user = db.is_register(callback.from_user.id)
    if user:
        row1 = [InlineKeyboardButton(text='💸 Баланс VaxCoin', callback_data='balance')]
        row2 = [InlineKeyboardButton(text='💵 Вывести', callback_data='cash_out'),
                InlineKeyboardButton(text='⁉️ Как заработать токены', url=info_link)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'💫| Начинай одним из первых зарабатывать токены <b>VaxCoin</b>\n\n💸| Чтобы обменять их после листинга на наш криптотокен и продать на бирже <a href="https://habrastorage.org/webt/1g/ma/ub/1gmaubhrtcfm8t6enwfgvkuypag.jpeg">⠀</a>',
                               parse_mode='HTML', reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'Вы еще не зарегистрированы в <a href="https://t.me/Vaxee_bot">Vaxee</a>',
                               parse_mode='HTML', disable_web_page_preview=True)


@dp.callback_query(F.data.in_(['balance']))
async def balance(callback: CallbackQuery):
    await callback.message.delete()
    balance = db.get_coins(callback.from_user.id)
    match int(balance[1]):
        case 0:
            doxod = 0.01
        case 1:
            doxod = 0.025
        case 2:
            doxod = 0.05
    income = round(float(float(balance[2]) * doxod), 2)
    msg = f'🏦 <b>VaxWallet</b>\n\n💵| <b>Баланс VaxCoin: {balance[0]} Coin</b>\n\n💸| <b>Доход VaxCoin с инвестиций: {income} Coin</b>'
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='menu')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text=msg, parse_mode='HTML', reply_markup=keyboard)


@dp.callback_query(F.data.in_(['cash_out']))
async def cash_out(callback: CallbackQuery):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='menu')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='❎ Вывод <b>VaxCoin</b> пока недоступен',
                           parse_mode='HTML', reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


def run_wallet_bot():
    asyncio.run(main())
