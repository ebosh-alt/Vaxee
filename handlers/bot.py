import json
import random
import string

import requests
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton, WebAppInfo
from yoomoney import Client
from yoomoney import Quickpay
import logging
from data.config import *
from entity.database import Transaction
from service.GetMessage import get_mes, get_text
from service.states import Form
from service.keyboards import Keyboards as kb

logger = logging.getLogger(__name__)
router = Router()


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for _ in range(length))
    return rand_string


@router.message(Command('start'))
async def reg_step1(message: Message):
    User = db.is_register(message.from_user.id)
    if not bonus_system.in_(message.from_user.id):
        bonus_system.create_entity(message.from_user.id)
    if not usdt_requisites.in_(message.from_user.id):
        usdt_requisites.create_entity(message.from_user.id)
    user_channel_status = await bot.get_chat_member(chat_id=f'{channel}', user_id=message.from_user.id)
    logger.info(f"user {message.from_user.id} channel status: {user_channel_status.status}")
    row1 = [KeyboardButton(text='📈 Инвестиции')]
    row2 = [KeyboardButton(text='👨‍💻 Мой профиль')]
    row3 = [KeyboardButton(text='💸 Кошелёк'), KeyboardButton(text='📊 Статистика')]
    row4 = [KeyboardButton(text='📠 Калькулятор'), KeyboardButton(text='❓ Информация')]
    # row5 = [KeyboardButton(text="🗒️ Задания")]
    rows = [row1, row2, row3, row4]
    keyboard_menu = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    if User is None:
        db.new_user(message.from_user.id, message.from_user.username)
        if len(message.text.split(' ')) == 2:
            db.set_referral(message.from_user.id, int(message.text.split(' ')[1]))
        row1 = [InlineKeyboardButton(text='📰 Новостной канал', url=f't.me/{channel[1:]}')]
        row2 = [InlineKeyboardButton(text='✅ Проверить', callback_data='check-subscribe')]
        rows = [row1, row2]
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer(text='Для продолжения подпишитесь на наш новостной канал:', reply_markup=keyboard)
    elif user_channel_status.status != 'left':
        return await message.answer('Вы уже зарегистрированы!', reply_markup=keyboard_menu)
    elif user_channel_status.status == 'left':
        row1 = [InlineKeyboardButton(text='📰 Новостной канал', url=f't.me/{channel[1:]}')]
        row2 = [InlineKeyboardButton(text='✅ Проверить', callback_data='check-subscribe')]
        rows = [row1, row2]
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer(text='Для продолжения подпишитесь на наш новостной канал:', reply_markup=keyboard)
    else:
        await message.answer('Вы успешно зарегистрировались!', reply_markup=keyboard_menu)
        user = db.get_profile(message.from_user.id)
        db.update_referal(message.from_user.id, user["referal"])
        # if len(message.text.split(' ')) == 2:
        #     db.update_referal(message.from_user.id, user['referal_id'])
        if user[9] != 0:
            refPrize = db.get_refPrize()
            await bot.send_message(chat_id=user['referal_id'],
                                   text=f'✅ Вам начислен бонус за нового реферала\n\n💵 <b>{refPrize[0]}₽</b> на баланс для инвестиций\n💸 <b>5 VaxCoin</b>',
                                   parse_mode='HTML')


@router.callback_query(F.data.in_(['check-subscribe']))
async def reg_step2(callback: CallbackQuery):
    user_channel_status = await bot.get_chat_member(chat_id=f'{channel}', user_id=callback.from_user.id)
    user_id = callback.from_user.id
    if user_channel_status.status != 'left':
        await callback.message.delete()
        row1 = [KeyboardButton(text='📈 Инвестиции')]
        row2 = [KeyboardButton(text='👨‍💻 Мой профиль')]
        row3 = [KeyboardButton(text='💸 Кошелёк'), KeyboardButton(text='📊 Статистика')]
        row4 = [KeyboardButton(text='📠 Калькулятор'), KeyboardButton(text='❓ Информация')]
        # row5 = [KeyboardButton(text='🗒️ Задания')]
        rows = [row1, row2, row3, row4]
        keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
        await bot.send_message(chat_id=callback.from_user.id, text='Вы успешно зарегистрировались!',
                               reply_markup=keyboard)
        logger.info(user_id)
        user = db.get_profile(user_id)
        # if len(ca.text.split(' ')) == 2:
        if user[9] != 0:
            refPrize = db.get_refPrize()
            db.update_referal(callback.from_user.id, user["referal"])
            await bot.send_message(chat_id=user[9],
                                   text=f'✅ Вам начислен бонус за нового реферала\n\n💵 <b>{refPrize[0]}₽</b> на баланс для инвестиций\n💸 <b>5 VaxCoin</b>',
                                   parse_mode='HTML')

    else:
        await callback.answer('❎ Вы еще не подписались на новостной канал!', show_alert=True)


@router.message(F.text == '📈 Инвестиции')
async def invest(message: Message, state: FSMContext):
    await state.clear()
    info = db.get_investINFO(message.from_user.id)
    msg = f'📈 Инвестируй и получай <b>стабильную прибыль:</b>\n\n📠 Процент от вклада: <b>{info[0]}%</b>\n💸 Ваш вклад: <b>{info[1]} RUB</b>\n📤 Баланс для вывода: <b>{info[2]} RUB</b> <a href="https://habrastorage.org/webt/jf/64/r-/jf64r-bemwiu__rsdx2spu3chte.png">⠀</a>'
    row = [InlineKeyboardButton(text='➕ Инвестировать', callback_data='invest')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await message.answer(text=msg, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.in_(['cash-in']))
async def cash_in(callback: CallbackQuery):
    row1 = [InlineKeyboardButton(text='➕ Keksik', web_app=WebAppInfo(url='https://tg.keksik.io/@Vaxee_bot'))]
    row2 = [InlineKeyboardButton(text='➕ Пополнить через администратора', callback_data='cash-inADMIN')]
    # row3 = [InlineKeyboardButton(text='➕ Yoomoney', callback_data='cash_inSITE-card')]
    # row4 = [InlineKeyboardButton(text='➕ Freekasssa', callback_data='cash_in_freekassa')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='💸 Выберите способ пополнения <a href="https://habrastorage.org/webt/kz/bx/11/kzbx11ebx15rp8kij6rfytgk0xg.png">⠀</a>',
                           reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.in_(['cash-inADMIN']))
async def cash_inADMIN(callback: CallbackQuery):
    # InlineKeyboardButton(text='➕ ETHEREUM', callback_data='cash_inADMIN-eth')
    row1 = [InlineKeyboardButton(text='➕ USDT', callback_data='cash_inADMIN-usdt')]
    row2 = [InlineKeyboardButton(text='➕ TON', callback_data='cash_inADMIN-ton')]
    row3 = [InlineKeyboardButton(text='➕ BITCOIN', callback_data='cash_inADMIN-btc'),
            InlineKeyboardButton(text='➕ LTC', callback_data='cash_inADMIN-ltc')]
    row4 = [InlineKeyboardButton(text='➕ ATOM', callback_data='cash_inADMIN-atom'),
            InlineKeyboardButton(text='➕ SOL', callback_data='cash_inADMIN-sol')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4])
    await bot.send_message(chat_id=callback.from_user.id, text='💸 Выберите удобный способ оплаты',
                           reply_markup=keyboard)


@router.callback_query(F.data.in_(['cash_inADMIN-usdt']))
async def cash_inADMIN_card(callback: CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,
                           text=get_mes("replenishment_usdt"),
                           disable_web_page_preview=True,
                           reply_markup=kb.usdt_network_kb)


@router.callback_query(F.data.in_(['usdt_network_trc_20', "usdt_network_bep_20", "usdt_network_ton"]))
async def usdt_network(message: CallbackQuery):
    id = message.from_user.id
    if message.data == "usdt_network_trc_20":
        text = get_text(get_mes("usdt_trc20"))
    elif message.data == "usdt_network_bep_20":
        text = get_text(get_mes("usdt_bep20"))
    else:
        text = get_text(get_mes("usdt_ton"))
    row = [InlineKeyboardButton(text='✅ Оплатил', callback_data='cash_inADMIN-card-usdt')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=id,
                           text=text,
                           reply_markup=keyboard,
                           parse_mode=ParseMode.MARKDOWN_V2,
                           disable_web_page_preview=True
                           )


@router.callback_query(F.data.in_(['cash_inADMIN-btc']))
async def cash_inADMIN_btc(callback: CallbackQuery):
    row = [InlineKeyboardButton(text='✅ Оплатил', callback_data='cash_inADMIN-btc-check')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    name = db.get_rekviziti('btc')
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'💸 Переведите нужную сумму и <b>сохраните скриншот оплаты</b>\n\n💵 <b>Деньги зачисляться после проверки платежа администратором</b>\n\n<b>♻Конвертация производится по нынешнему курсу</b>\n\n\n▪ BITCOIN: <code>{name[0]}</code>\n\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)


@router.callback_query(F.data.in_(['cash_inADMIN-eth']))
async def cash_inADMIN_eth(callback: CallbackQuery):
    row = [InlineKeyboardButton(text='✅ Оплатил', callback_data='cash_inADMIN-eth-check')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    name = db.get_rekviziti('eth')
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'💸 Переведите нужную сумму и <b>сохраните скриншот оплаты</b>\n\n💵 <b>Деньги зачисляться после проверки платежа администратором</b>\n\n<b>♻Конвертация производится по нынешнему курсу</b>\n\n\n▪ ETHEREUM: <code>{name[0]}</code>\n\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)


@router.callback_query(F.data.in_(['cash_inADMIN-ltc']))
async def cash_inADMIN_ltc(callback: CallbackQuery):
    row = [InlineKeyboardButton(text='✅ Оплатил', callback_data='cash_inADMIN-ltc-check')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    name = db.get_rekviziti('ltc')
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'💸 Переведите нужную сумму и <b>сохраните скриншот оплаты</b>\n\n💵 <b>Деньги зачисляться после проверки платежа администратором</b>\n\n<b>♻Конвертация производится по нынешнему курсу</b>\n\n\n▪ LTC: <code>{name[0]}</code>\n\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)


@router.callback_query(F.data.in_(['cash_inADMIN-ton']))
async def cash_inADMIN_ton(callback: CallbackQuery):
    row = [InlineKeyboardButton(text='✅ Оплатил', callback_data='cash_inADMIN-ton-check')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    name = db.get_rekviziti('ton')
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'❗️ Отправляйте на этот адрес только\n\n<b>Toncoin TON</b> и токены в сети <b>TON</b>, иначе вы можете потерять свои средства.\n\n💵 Отправьте нужную сумму и подтвердите оплату\n\n<b>♻️ Сохраните скриншот оплаты для подтверждения платежа</b>\n\n\n TON: <code>{name[0]}</code>\n\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)


@router.callback_query(F.data.in_(['cash_inADMIN-atom']))
async def cash_inADMIN_atom(callback: CallbackQuery):
    row = [InlineKeyboardButton(text='✅ Оплатил', callback_data='cash_inADMIN-atom-check')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    name = db.get_rekviziti('atom')
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'💸 Переведите нужную сумму и <b>сохраните скриншот оплаты</b>\n\n💵 <b>Деньги зачисляться после проверки платежа администратором</b>\n\n<b>♻Конвертация производится по нынешнему курсу</b>\n\n\n▪ ATOM: <code>{name[0]}</code>\n\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)


@router.callback_query(F.data.in_(['cash_inADMIN-sol']))
async def cash_inADMIN_sol(callback: CallbackQuery):
    row = [InlineKeyboardButton(text='✅ Оплатил', callback_data='cash_inADMIN-sol-check')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    name = db.get_rekviziti('sol')
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'💸 Переведите нужную сумму и <b>сохраните скриншот оплаты</b>\n\n💵 <b>Деньги зачисляться после проверки платежа администратором</b>\n\n<b>♻Конвертация производится по нынешнему курсу</b>\n\n\n▪ SOL: <code>{name[0]}</code>\n\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)


@router.callback_query(F.data.in_(['cash_inADMIN-card-usdt']))
async def checkpaymentADMIN_card(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_usdt)


@router.callback_query(F.data.in_(['cash_inADMIN-card-check']))
async def checkpaymentADMIN_card(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_card)


@router.callback_query(F.data.in_(['cash_inADMIN-btc-check']))
async def checkpaymentADMIN_btc(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_btc)


@router.callback_query(F.data.in_(['cash_inADMIN-eth-check']))
async def checkpaymentADMIN_eth(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_eth)


@router.callback_query(F.data.in_(['cash_inADMIN-ltc-check']))
async def checkpaymentADMIN_ltc(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_ltc)


@router.callback_query(F.data.in_(['cash_inADMIN-ton-check']))
async def checkpaymentADMIN_ton(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_ton)


@router.callback_query(F.data.in_(['cash_inADMIN-atom-check']))
async def checkpaymentADMIN_atom(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_atom)


@router.callback_query(F.data.in_(['cash_inADMIN-sol-check']))
async def checkpaymentADMIN_sol(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=callback.from_user.id, text='📎 Отправьте скриншот оплаты.')
    await state.set_state(Form.cash_inADMIN_sol)


@router.message(Form.cash_inADMIN_usdt)
async def checkAdmin_card(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-usdt {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-usdt {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_card=message)
    await state.set_state(Form.cash_inADMIN_card)
    await state.clear()


@router.message(Form.cash_inADMIN_card)
async def checkAdmin_card(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-card {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-card {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_card=message)
    await state.set_state(Form.cash_inADMIN_card)
    await state.clear()


@router.message(Form.adminVvod_card)
async def adminVvod_card(message: Message, state: FSMContext):
    try:
        info = message.text.split(', ')
        userId = info[0]
        summa = float(info[1])
        db.give_investBalance(userId, summa)
        db.update_popolnili(summa)
        ref = db.get_ref(userId)
        if ref[0] != 0:
            db.give_investBalance(ref[0], summa * 0.05)
            db.update_refDoxod(ref[0], summa * 0.05)
        await message.answer(f'Средства зачислены на счет {userId}')
        await bot.send_message(chat_id=userId, text='✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                               parse_mode='HTML')
        await state.update_data(adminVvod_card=message.text)
        await state.set_state(Form.adminVvod_card)
        await state.clear()
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.message(Form.cash_inADMIN_btc)
async def checkAdmin_btc(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-btc {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-btc {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_btc=message)
    await state.set_state(Form.cash_inADMIN_btc)
    await state.clear()


@router.message(Form.adminVvod_btc)
async def adminVvod_btc(message: Message, state: FSMContext):
    try:
        info = message.text.split(', ')
        userId = info[0]
        summa = float(info[1])
        db.give_investBalance(userId, summa)
        db.update_popolnili(summa)
        ref = db.get_ref(userId)
        if ref[0] != 0:
            db.give_investBalance(ref[0], summa * 0.05)
            db.update_refDoxod(ref[0], summa * 0.05)
        await message.answer(f'Средства зачислены на счет {userId}')
        await bot.send_message(chat_id=userId, text='✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                               parse_mode='HTML')
        await state.update_data(adminVvod_btc=message.text)
        await state.set_state(Form.adminVvod_btc)
        await state.clear()
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.message(Form.cash_inADMIN_eth)
async def checkAdmin_eth(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-eth {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-eth {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_eth=message)
    await state.set_state(Form.cash_inADMIN_eth)
    await state.clear()


@router.message(Form.adminVvod_eth)
async def adminVvod_eth(message: Message, state: FSMContext):
    try:
        info = message.text.split(', ')
        userId = info[0]
        summa = float(info[1])
        db.give_investBalance(userId, summa)
        db.update_popolnili(summa)
        ref = db.get_ref(userId)
        if ref[0] != 0:
            db.give_investBalance(ref[0], summa * 0.05)
            db.update_refDoxod(ref[0], summa * 0.05)
        await message.answer(f'Средства зачислены на счет {userId}')
        await bot.send_message(chat_id=userId, text='✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                               parse_mode='HTML')
        await state.update_data(adminVvod_eth=message.text)
        await state.set_state(Form.adminVvod_eth)
        await state.clear()
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.message(Form.cash_inADMIN_ltc)
async def checkAdmin_ltc(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-ltc {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-ltc {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_ltc=message)
    await state.set_state(Form.cash_inADMIN_ltc)
    await state.clear()


@router.message(Form.adminVvod_ltc)
async def adminVvod_ltc(message: Message, state: FSMContext):
    try:
        info = message.text.split(', ')
        userId = info[0]
        summa = float(info[1])
        db.give_investBalance(userId, summa)
        db.update_popolnili(summa)
        ref = db.get_ref(userId)
        if ref[0] != 0:
            db.give_investBalance(ref[0], summa * 0.05)
            db.update_refDoxod(ref[0], summa * 0.05)
        await message.answer(f'Средства зачислены на счет {userId}')
        await bot.send_message(chat_id=userId, text='✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                               parse_mode='HTML')
        await state.update_data(adminVvod_ltc=message.text)
        await state.set_state(Form.adminVvod_ltc)
        await state.clear()
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.message(Form.cash_inADMIN_ton)
async def checkAdmin_ton(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-ton {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-ton {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_ton=message)
    await state.set_state(Form.cash_inADMIN_ton)
    await state.clear()


@router.message(Form.adminVvod_ton)
async def adminVvod_ton(message: Message, state: FSMContext):
    try:
        info = message.text.split(', ')
        userId = info[0]
        summa = float(info[1])
        db.give_investBalance(userId, summa)
        db.update_popolnili(summa)
        ref = db.get_ref(userId)
        if ref[0] != 0:
            db.give_investBalance(ref[0], summa * 0.05)
            db.update_refDoxod(ref[0], summa * 0.05)
        await message.answer(f'Средства зачислены на счет {userId}')
        await bot.send_message(chat_id=userId, text='✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                               parse_mode='HTML')
        await state.update_data(adminVvod_ton=message.text)
        await state.set_state(Form.adminVvod_ton)
        await state.clear()
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.message(Form.cash_inADMIN_atom)
async def checkAdmin_atom(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-atom {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-atom {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_atom=message)
    await state.set_state(Form.cash_inADMIN_atom)
    await state.clear()


@router.message(Form.adminVvod_atom)
async def adminVvod_atom(message: Message, state: FSMContext):
    try:
        info = message.text.split(', ')
        userId = info[0]
        summa = float(info[1])
        db.give_investBalance(userId, summa)
        db.update_popolnili(summa)
        ref = db.get_ref(userId)
        if ref[0] != 0:
            db.give_investBalance(ref[0], summa * 0.05)
            db.update_refDoxod(ref[0], summa * 0.05)
        await message.answer(f'Средства зачислены на счет {userId}')
        await bot.send_message(chat_id=userId, text='✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                               parse_mode='HTML')
        await state.update_data(adminVvod_atom=message.text)
        await state.set_state(Form.adminVvod_atom)
        await state.clear()
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.message(Form.cash_inADMIN_sol)
async def checkAdmin_sol(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Начислить', callback_data=f'admin-vvod-sol {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-sol {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение зачисления',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(cash_inADMIN_sol=message)
    await state.set_state(Form.cash_inADMIN_sol)
    await state.clear()


@router.message(Form.adminVvod_sol)
async def adminVvod_sol(message: Message, state: FSMContext):
    try:
        info = message.text.split(', ')
        userId = info[0]
        summa = float(info[1])
        db.give_investBalance(userId, summa)
        db.update_popolnili(summa)
        ref = db.get_ref(userId)
        if ref[0] != 0:
            db.give_investBalance(ref[0], summa * 0.05)
            db.update_refDoxod(ref[0], summa * 0.05)
        await message.answer(f'Средства зачислены на счет {userId}')
        await bot.send_message(chat_id=userId, text='✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                               parse_mode='HTML')
        await state.update_data(adminVvod_sol=message.text)
        await state.set_state(Form.adminVvod_sol)
        await state.clear()
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


# @router.callback_query(F.data.in_(['cash_inSITE-card']))
# async def cash_inSITE_card(callback: CallbackQuery, state: FSMContext):
#    row = [InlineKeyboardButton(text='⭕ Отменить ввод', callback_data='cash-inSITE')]
#    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
#    await bot.send_message(chat_id=callback.from_user.id,
#                           text='▪ <b>Минимальная сумма пополнения - 200₽</b>\n\nВведите сумму оплаты:',
#                           parse_mode='HTML', reply_markup=keyboard)
#    await state.set_state(Form.cash_inSITE_card)


# @router.message(Form.cash_inSITE_card)
# async def cash_inSITE_card_oplata(message: Message, state: FSMContext):
#    try:
#        summa = int(message.text)
#        if summa >= 200:
#            label = generate_random_string(12)
#            quickpay = Quickpay(
#                receiver="4100118701003387",
#                quickpay_form="shop",
#                targets="PREMIUM Статус",
#                paymentType="SB",
#                sum=summa,
#                label=label
#            )
#            row1 = [InlineKeyboardButton(text='💳 Оплатить', url=quickpay.redirected_url)]
#            row2 = [InlineKeyboardButton(text='✅ Проверить оплату', callback_data=f'cash_inSITE-card-check {label}')]
#            keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
#            msg = f'💸 Сумма для оплаты <b>{summa}₽</b>\n\n💵 <b>Деньги будут зачислены после нажатия на кнопку «Проверить оплату»</b>\n\n✅ <b>На всякий случай, сохраните скриншот</b>\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>'
#            await message.answer(text=msg, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
#            await state.update_data(cash_inSITE_card=int(message.text))
#            await state.set_state(Form.cash_inSITE_card)
#            await state.clear()
#        else:
#            await message.answer('❗ Сумма не может быть меньше <b>200₽</b>', parse_mode='HTML')
#    except Exception as E:
#        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
#        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
#        print(E)
#        await message.answer('❌ Неверно введена сумма, попробуйте еще раз!', reply_markup=keyboard)


@router.callback_query(F.data.in_(['invest']))
async def vklad(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    info = db.get_investINFO(callback.from_user.id)
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    msg = f'📈 Вы можете инвестировать: {info[3]}₽\n\n💸 Введите сумму для инвестиции:'
    await bot.send_message(chat_id=callback.from_user.id, text=msg, reply_markup=keyboard)
    await state.set_state(Form.invest)


@router.message(Form.invest)
async def new_invest(message: Message, state: FSMContext):
    try:
        invest = float(message.text)
        balance = db.get_balance(message.from_user.id)
        balance = float(balance[0])
        if balance >= invest:
            db.new_invest(message.from_user.id, invest)
            row = [InlineKeyboardButton(text='👨‍💻 Мой профиль', callback_data='profile')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer(f'✅ Вы инвестировали: {invest}₽', reply_markup=keyboard)
            await state.clear()
        else:
            row = [InlineKeyboardButton(text='💸 Пополнить баланс', callback_data='cash-in')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств на балансе.', reply_markup=keyboard)
            await state.update_data(calc=float(message.text))
            await state.set_state(Form.calc)
            await state.clear()

    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неверная сумма, попробуйте еще раз!', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin']))
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    row1 = [InlineKeyboardButton(text='Инвест.баланс', callback_data='admin_invest-bal'),
            InlineKeyboardButton(text='Вывод.баланс', callback_data='admin_vivod-bal')]
    row2 = [InlineKeyboardButton(text='Выдать статус', callback_data='admin_give-status'),
            InlineKeyboardButton(text='Забрать статус', callback_data='admin_take-status')]
    row3 = [InlineKeyboardButton(text='Создать промокод', callback_data='admin_newpromo'),
            InlineKeyboardButton(text='Рассылка', callback_data='admin_rassilka')]
    row4 = [InlineKeyboardButton(text='Реквизиты', callback_data='admin_rekviziti'),
            InlineKeyboardButton(text='Изменить реф.награду', callback_data='admin_change-ref')]
    rows = [row1, row2, row3, row4]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    await bot.send_message(chat_id=callback.from_user.id, text='<b>👔 Админ панель</b>\n\nВыберите один из пунктов:',
                           parse_mode='HTML', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin_vivod-bal']))
async def vivod_balSELECT(callback: CallbackQuery):
    await callback.message.delete()
    row1 = [InlineKeyboardButton(text='Выдать', callback_data='admin_give-vivod-bal'),
            InlineKeyboardButton(text='Списать', callback_data='admin_take-vivod-bal')]
    row2 = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=callback.from_user.id, text='🌐 Выберите необходимый пункт:', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin_take-vivod-bal']))
async def select_take_vivod(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_vivod-bal')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🆔 Введите ID и сумму через запятую!\nНапример: 123456, 100', reply_markup=keyboard)
    await state.set_state(Form.take_vivod)


@router.message(Form.take_vivod)
async def take_vivod_bal(message: Message, state: FSMContext):
    try:
        msg_info = message.text.split(', ')
        userId = msg_info[0]
        summa = float(msg_info[1])
        user_info = db.get_profile(userId)
        if user_info:
            db.take_vivodBalance(userId, summa)
            await message.answer(f'✅ {summa} RUB списаны с баланса для вывода пользователя {userId}')
            await state.update_data(take_vivod=message.text)
            await state.set_state(Form.take_vivod)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.callback_query(F.data.in_(['admin_give-vivod-bal']))
async def select_give_vivod(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_vivod-bal')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🆔 Введите ID и сумму через запятую!\nНапример: 123456, 100', reply_markup=keyboard)
    await state.set_state(Form.give_vivod)


@router.message(Form.give_vivod)
async def give_vivod_bal(message: Message, state: FSMContext):
    try:
        msg_info = message.text.split(', ')
        userId = msg_info[0]
        summa = float(msg_info[1])
        user_info = db.get_profile(userId)
        if user_info:
            db.give_vivodBalance(userId, summa)
            await message.answer(f'✅ {summa} RUB выданы на баланс для вывода пользователя {userId}')
            await state.update_data(give_vivod=message.text)
            await state.set_state(Form.give_vivod)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.callback_query(F.data.in_(['admin_invest-bal']))
async def invest_balSELECT(callback: CallbackQuery):
    await callback.message.delete()
    row1 = [InlineKeyboardButton(text='Выдать', callback_data='admin_give-invest-bal'),
            InlineKeyboardButton(text='Списать', callback_data='admin_take-invest-bal')]
    row2 = [InlineKeyboardButton(text='Списать инвестированное', callback_data='adimn_take-in-invest'),
            InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=callback.from_user.id, text='🌐 Выберите необходимый пункт:', reply_markup=keyboard)


@router.callback_query(F.data.in_(['adimn_take-in-invest']))
async def select_invest_bal(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_invest-bal')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🆔 Введите ID и сумму через запятую!\nНапример: 123456, 100', reply_markup=keyboard)
    await state.set_state(Form.take_inInvest)


@router.message(Form.take_inInvest)
async def give_invest_bal(message: Message, state: FSMContext):
    try:
        msg_info = message.text.split(', ')
        userId = msg_info[0]
        summa = float(msg_info[1])
        user_info = db.get_profile(userId)
        if user_info:
            db.take_inInvestBalance(userId, summa)
            await message.answer(f'✅ {summa} RUB списаны с инвестированного баланса пользователя {userId}')
            await state.update_data(take_inInvest=message.text)
            await state.set_state(Form.take_inInvest)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.callback_query(F.data.in_(['admin_take-invest-bal']))
async def select_invest_bal(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_invest-bal')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🆔 Введите ID и сумму через запятую!\nНапример: 123456, 100', reply_markup=keyboard)
    await state.set_state(Form.take_invest)


@router.message(Form.take_invest)
async def give_invest_bal(message: Message, state: FSMContext):
    try:
        msg_info = message.text.split(', ')
        userId = msg_info[0]
        summa = float(msg_info[1])
        user_info = db.get_profile(userId)
        if user_info:
            db.take_investBalance(userId, summa)
            await message.answer(f'✅ {summa} RUB списаны с инвестиционного баланса пользователя {userId}')
            await state.update_data(take_invest=message.text)
            await state.set_state(Form.take_invest)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.callback_query(F.data.in_(['admin_give-invest-bal']))
async def select_invest_bal(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_invest-bal')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🆔 Введите ID и сумму через запятую!\nНапример: 123456, 100', reply_markup=keyboard)
    await state.set_state(Form.give_invest)


@router.message(Form.give_invest)
async def give_invest_bal(message: Message, state: FSMContext):
    try:
        msg_info = message.text.split(', ')
        userId = msg_info[0]
        summa = float(msg_info[1])
        user_info = db.get_profile(userId)
        if user_info:
            db.give_investBalance(userId, summa)
            await message.answer(f'✅ {summa} RUB выданы на инвестиционный баланс пользователя {userId}')
            await state.update_data(give_invest=message.text)
            await state.set_state(Form.give_invest)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        await message.answer('❌ Неправильный формат, попробуйте еще раз!')


@router.callback_query(F.data.in_(['admin_take-status']))
async def status_selectUSER(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='🆔 Введите ID пользователя для снятия статуса:',
                           reply_markup=keyboard)
    await state.set_state(Form.user)


@router.message(Form.user)
async def status_giveUSER(message: Message, state: FSMContext):
    try:
        userId = int(message.text)
        user = db.get_profile(userId)
        if user:
            db.change_vip(userId, 0)
            await message.answer('✅ Статус успешно снят!')
            await state.update_data(user=message.text)
            await state.set_state(Form.user)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неверно введен ID, попробуйте еще раз!', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin_give-status']))
async def status_select(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    row1 = [InlineKeyboardButton(text='💸 VIP', callback_data='admin-giveVIP'),
            InlineKeyboardButton(text='👑 PREMIUM', callback_data='admin-givePREMIUM')]
    row2 = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=callback.from_user.id, text='⚜ Выберите статус для выдачи:', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin-giveVIP']))
async def status_selectVIP(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_give-status')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='🆔 Введите ID пользователя для выдачи VIP:',
                           reply_markup=keyboard)
    await state.set_state(Form.vip)


@router.message(Form.vip)
async def status_giveVIP(message: Message, state: FSMContext):
    try:
        userId = int(message.text)
        user = db.get_profile(userId)
        if user:
            db.change_vip(userId, 1)
            await message.answer('✅ VIP статус успешно выдан!')
            await state.update_data(vip=message.text)
            await state.set_state(Form.vip)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неверно введен ID, попробуйте еще раз!', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin-givePREMIUM']))
async def status_selectPREMIUM(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_give-status')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='🆔 Введите ID пользователя для выдачи PREMIUM:',
                           reply_markup=keyboard)
    await state.set_state(Form.premium)


@router.message(Form.premium)
async def status_givePREMIUM(message: Message, state: FSMContext):
    try:
        userId = int(message.text)
        user = db.get_profile(userId)
        if user:
            db.change_vip(userId, 2)
            await message.answer('✅ PREMIUM статус успешно выдан!')
            await state.update_data(premium=message.text)
            await state.set_state(Form.premium)
            await state.clear()
        else:
            await message.answer('❌ Данный профиль не найден, попробуйте еще раз!')
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неверно введен ID, попробуйте еще раз!', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin_rekviziti']))
async def change_rekviziti(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    row1 = [InlineKeyboardButton(text='Карта', callback_data='edit-karta'),
            InlineKeyboardButton(text='BITCOIN', callback_data='edit-btc')]
    row2 = [InlineKeyboardButton(text='ETHEREUM', callback_data='edit-eth'),
            InlineKeyboardButton(text='LTC', callback_data='edit-ltc')]
    row3 = [InlineKeyboardButton(text='TON', callback_data='edit-ton'),
            InlineKeyboardButton(text='ATOM', callback_data='edit-atom')]
    row4 = [InlineKeyboardButton(text='SOL', callback_data='edit-sol'),
            InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4])
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите метод оплаты для изменения реквизитов:',
                           reply_markup=keyboard)


@router.callback_query(F.data.in_(['edit-karta']))
async def edit_karta(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_rekviziti')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новые реквизиты:', reply_markup=keyboard)
    await state.set_state(Form.karta)


@router.message(Form.karta)
async def new_karta(message: Message, state: FSMContext):
    db.new_karta(message.text)
    await state.update_data(karta=message.text)
    await state.set_state(Form.karta)
    await state.clear()
    await message.answer(f'Новые реквизиты "Карта": {message.text}')


@router.callback_query(F.data.in_(['edit-btc']))
async def edit_karta(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_rekviziti')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новые реквизиты:', reply_markup=keyboard)
    await state.set_state(Form.btc)


@router.message(Form.btc)
async def new_karta(message: Message, state: FSMContext):
    db.new_btc(message.text)
    await state.update_data(btc=message.text)
    await state.set_state(Form.btc)
    await state.clear()
    await message.answer(f'Новые реквизиты "BITCOIN": {message.text}')


@router.callback_query(F.data.in_(['edit-eth']))
async def edit_karta(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_rekviziti')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новые реквизиты:', reply_markup=keyboard)
    await state.set_state(Form.eth)


@router.message(Form.eth)
async def new_karta(message: Message, state: FSMContext):
    db.new_eth(message.text)
    await state.update_data(eth=message.text)
    await state.set_state(Form.eth)
    await state.clear()
    await message.answer(f'Новые реквизиты "ETHEREUM": {message.text}')


@router.callback_query(F.data.in_(['edit-ltc']))
async def edit_karta(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_rekviziti')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новые реквизиты:', reply_markup=keyboard)
    await state.set_state(Form.ltc)


@router.message(Form.ltc)
async def new_karta(message: Message, state: FSMContext):
    db.new_ltc(message.text)
    await state.update_data(ltc=message.text)
    await state.set_state(Form.ltc)
    await state.clear()
    await message.answer(f'Новые реквизиты "LTC": {message.text}')


@router.callback_query(F.data.in_(['edit-ton']))
async def edit_karta(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_rekviziti')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новые реквизиты:', reply_markup=keyboard)
    await state.set_state(Form.ton)


@router.message(Form.ton)
async def new_karta(message: Message, state: FSMContext):
    db.new_ton(message.text)
    await state.update_data(ton=message.text)
    await state.set_state(Form.ton)
    await state.clear()
    await message.answer(f'Новые реквизиты "TON": {message.text}')


@router.callback_query(F.data.in_(['edit-atom']))
async def edit_karta(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_rekviziti')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новые реквизиты:', reply_markup=keyboard)
    await state.set_state(Form.atom)


@router.message(Form.atom)
async def new_karta(message: Message, state: FSMContext):
    db.new_atom(message.text)
    await state.update_data(atom=message.text)
    await state.set_state(Form.atom)
    await state.clear()
    await message.answer(f'Новые реквизиты "ATOM": {message.text}')


@router.callback_query(F.data.in_(['edit-sol']))
async def edit_karta(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin_rekviziti')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новые реквизиты:', reply_markup=keyboard)
    await state.set_state(Form.sol)


@router.message(Form.sol)
async def new_karta(message: Message, state: FSMContext):
    db.new_sol(message.text)
    await state.update_data(sol=message.text)
    await state.set_state(Form.sol)
    await state.clear()
    await message.answer(f'Новые реквизиты "SOL": {message.text}')


@router.callback_query(F.data.in_(['admin_change-ref']))
async def change_ref(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    cur_refPrize = db.get_refPrize()
    msg = f'💳 Текущая награда за реферала: <b>{cur_refPrize[0]}₽</b>\n\nВведите сумму для изменения:'
    await bot.send_message(chat_id=callback.from_user.id, text=msg, reply_markup=keyboard, parse_mode='HTML')
    await state.set_state(Form.ref)


@router.callback_query(F.data.in_(['admin_newpromo']))
async def newpromo(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🔰 Введите промкод в формате: название, награда, кол-во активаций\n\nНапример: промокод, 100, 5',
                           reply_markup=keyboard)
    await state.set_state(Form.promo)


@router.message(Form.promo)
async def new_promo(message: Message, state: FSMContext):
    try:
        promo = message.text.split(', ')
        name = promo[0]
        prize = float(promo[1])
        activate = int(promo[2])
        db.newpromo(name, prize, activate)
        await message.answer(f'🔰 Создан новый промокод "{name}"\n🏆 Награда: {prize} RUB\n👁‍🗨 Активаций: {activate}')
        await state.update_data(promo=message.text)
        await state.set_state(Form.promo)
        await state.clear()
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неверный формат, попробуйте еще раз!', reply_markup=keyboard)


@router.message(Form.ref)
async def changeReferal(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        db.update_refPrize(summa)
        await state.update_data(ref=float(message.text))
        await state.set_state(Form.ref)
        await state.clear()
        await message.answer(f'✅ Новая награда за реферала: <b>{summa}₽</b>', parse_mode='HTML')
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неверная сумма, попробуйте еще раз!', reply_markup=keyboard)


@router.callback_query(F.data.in_(['admin_rassilka']))
async def rassilka(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⬅ Назад', callback_data='admin')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='Отправьте сообщение для рассылки:',
                           reply_markup=keyboard)
    await state.set_state(Form.rassilka)


@router.message(Form.rassilka)
async def start_rassilka(message: Message, state: FSMContext):
    users = db.get_allUsers()
    await message.answer('💬 Рассылка запущена!')
    await state.update_data(rassilka=message)
    await state.set_state(Form.rassilka)
    await state.clear()
    for userId in users:
        try:
            await message.copy_to(chat_id=userId[0])
        except Exception as E:
            print(E)
    await message.answer('✔ Рассылка окончена!')


@router.callback_query(F.data.in_(['profile']))
async def callback_profile(callback: CallbackQuery):
    user = db.get_profile(callback.from_user.id)
    status = user[3]
    match status:
        case 0:
            status = 'Пользователь'
        case 1:
            status = 'VIP'
        case 2:
            status = 'PREMIUM'
    if callback.from_user.id == admin:
        row1 = [InlineKeyboardButton(text='➕ Приобрести статус', callback_data='buyVIP')]
        row2 = [InlineKeyboardButton(text='👥 Реферальная система', callback_data='referal-system')]
        row3 = [InlineKeyboardButton(text='🗒️ Задания', callback_data='tasks')]
        row4 = [InlineKeyboardButton(text='👔 Админ-панель', callback_data='admin')]
        rows = [row1, row2, row3, row4]
    else:
        row1 = [InlineKeyboardButton(text='➕ Приобрести статус', callback_data='buyVIP')]
        row2 = [InlineKeyboardButton(text='👥 Реферальная система', callback_data='referal-system')]
        row3 = [InlineKeyboardButton(text='🗒️ Задания', callback_data='tasks')]

        rows = [row1, row2, row3]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    income = round(float(user[8]), 2)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'🆔 Ваш ID: <code>{callback.from_user.id}</code>\n\n🏦 Доход в сутки: <b>{income} RUB</b>\n💴 Инвестировано: <b>{user[5]} RUB</b>\n💴 Баланс для вывода: <b>{user[6]} RUB</b>\n\n<b>👑 Статус: {status}\n📈 Процент дохода: {user[4]} %</b>\n<b>👥 Рефералов: {user[2]}</b> <a href="https://habrastorage.org/webt/gl/cs/zr/glcszryibrluuxrswulrexyni8s.png">⠀</a>',
                           parse_mode='HTML', reply_markup=keyboard
                           )


@router.callback_query(F.data.in_(['cash-out']))
async def cash_outSELECT(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    row1 = [InlineKeyboardButton(text='➖ Банковская карта (РФ)', callback_data='cash_outCARD')]
    row2 = [InlineKeyboardButton(text='➖ СБП (РФ)', callback_data='cash_outSBP')]
    # row3 = [InlineKeyboardButton(text='➖ Yoomoney (РФ)', callback_data='cash_outYOOMONEY')]
    row4 = [InlineKeyboardButton(text='➖ USDT', callback_data='cash_out_usdt')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2, row4])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='💸 Выберите способ вывода <a href="https://habrastorage.org/webt/_f/mq/xr/_fmqxrxhfmx0mtokoaagz31hqyi.png">⠀</a>',
                           reply_markup=keyboard,
                           parse_mode='HTML')


@router.callback_query(F.data.in_(['cash_outYOOMONEY']))
async def cash_outYOOMONEY(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    rekv = db.get_userRekvYOOMONEY(callback.from_user.id)
    bal = db.get_balance(callback.from_user.id)
    row1 = [InlineKeyboardButton(text='Вывести', callback_data='cash_outYOOMONEY-summa')]
    row2 = [InlineKeyboardButton(text='Изменить реквизиты', callback_data='update-userRekvYOOMONEY')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'♻ Вывод на <b>ЮMoney (РФ)</b>\n\n▪ Комиссия платежной системы: <b>3%</b>\n▪ Минимальная сумма для вывода: <b>100 ₽</b>\n\n👤 <b>Ваши реквизиты</b>: {rekv[0]}\n\n💵 Баланс для вывода: <b>{bal[1]}</b>',
                           reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.in_(['cash_outSBP']))
async def cash_outSBP(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    rekv = db.get_userRekvSBP(callback.from_user.id)
    bal = db.get_balance(callback.from_user.id)
    row1 = [InlineKeyboardButton(text='Вывести', callback_data='cash_outSBP-select')]
    row2 = [InlineKeyboardButton(text='Изменить реквизиты', callback_data='update-userRekvSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'♻ Вывод <b>СБП (РФ)</b>\n\n▪ Комиссия платежной системы: <b>3%</b>\n▪ Минимальная сумма для вывода: <b>100 ₽</b>\n\n👤 <b>Ваши реквизиты</b>: {rekv[0]}\n\n💵 Баланс для вывода: <b>{bal[1]}</b>',
                           reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.in_(['cash_outSBP-select']))
async def selectSBPbank(callback: CallbackQuery):
    rekv = db.get_userRekvSBP(callback.from_user.id)
    if rekv[0] == 'не указаны':
        return await callback.answer(text='📛 Вы не указали реквизиты!', show_alert=True)
    row1 = [InlineKeyboardButton(text='Сбербанк', callback_data='SBP-sber'),
            InlineKeyboardButton(text='ВТБ', callback_data='SBP-vtb')]
    row2 = [InlineKeyboardButton(text='Газпромбанк', callback_data='SBP-gazprombank'),
            InlineKeyboardButton(text='АльфаБанк', callback_data='SBP-alfa')]
    row3 = [InlineKeyboardButton(text='Россельхозбанк', callback_data='SBP-rossselxozbank'),
            InlineKeyboardButton(text='Т-Банк', callback_data='SBP-tbank')]
    row4 = [InlineKeyboardButton(text='Райффайзен банк', callback_data='SBP-raiffbank')]
    row5 = [InlineKeyboardButton(text='➖ Yoomoney (РФ)', callback_data='cash_outYOOMONEY')]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4, row5])
    await bot.send_message(chat_id=callback.from_user.id, text='🏦 Выберите банк:', reply_markup=keyboard)


@router.callback_query(F.data.in_(['SBP-sber']))
async def vvodSumma_sber(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaSber)


@router.callback_query(F.data.in_(['SBP-vtb']))
async def vvodSumma_vtb(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaVtb)


@router.callback_query(F.data.in_(['SBP-gazprombank']))
async def vvodSumma_gazprom(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaGazprom)


@router.callback_query(F.data.in_(['SBP-alfa']))
async def vvodSumma_alfa(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaAlfa)


@router.callback_query(F.data.in_(['SBP-rossselxozbank']))
async def vvodSumma_rossselxozbank(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaRosssel)


@router.callback_query(F.data.in_(['SBP-tbank']))
async def vvodSumma_tbank(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaTink)


@router.callback_query(F.data.in_(['SBP-raiffbank']))
async def vvodSumma_sber(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaRaif)


@router.callback_query(F.data.in_(['cash_outCARD']))
async def cash_outCARD(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    rekv = db.get_userRekvCARD(callback.from_user.id)
    bal = db.get_balance(callback.from_user.id)
    row1 = [InlineKeyboardButton(text='Вывести', callback_data='cash_outCARD-summa')]
    row2 = [InlineKeyboardButton(text='Изменить реквизиты', callback_data='update-userRekvCARD')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'♻ Вывод на <b>банковскую карту (РФ)</b>\n\n▪ Комиссия платежной системы: <b>3% + 50 ₽</b>\n▪ Минимальная сумма для вывода: <b>1100 ₽</b>\n\n👤 <b>Ваши реквизиты</b>: {rekv[0]}\n\n💵 Баланс для вывода: <b>{bal[1]}</b>',
                           reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.in_(['cash_outCARD-summa']))
async def vvodSumma_cashoutCARD(callback: CallbackQuery, state: FSMContext):
    rekv = db.get_userRekvCARD(callback.from_user.id)
    if rekv[0] == 'не указаны':
        return await callback.answer(text='📛 Вы не указали реквизиты!', show_alert=True)
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outCARD')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaCard)


@router.callback_query(F.data.in_(['cash_outYOOMONEY-summa']))
async def vvodSumma_cashoutYOOMONEY(callback: CallbackQuery, state: FSMContext):
    rekv = db.get_userRekvYOOMONEY(callback.from_user.id)
    if rekv[0] == 'не указаны':
        return await callback.answer(text='📛 Вы не указали реквизиты!', show_alert=True)
    await callback.message.delete()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash_outYOOMONEY')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='♻ Введите сумму вывода:', reply_markup=keyboard)
    await state.set_state(Form.summaYOOMONEY)


@router.callback_query(F.data.in_(['update-userRekvCARD']))
async def update_userRekvCARD(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.user_rekvizitiCARD)
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='💳 Введите новые реквизиты:', reply_markup=keyboard)


@router.callback_query(F.data.in_(['update-userRekvSBP']))
async def update_userRekvSBP(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.user_rekvizitiSBP)
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='💳 Введите новые реквизиты:\n♻️ Пример: +77053748287',
                           reply_markup=keyboard)


@router.callback_query(F.data.in_(['update-userRekvYOOMONEY']))
async def update_userRekvYOOMONEY(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.user_rekvizitiYOOMONEY)
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text='▪️ Введите номер кошелька ЮMoney\n♻️ Пример: 4433992266440022', reply_markup=keyboard)


@router.message(Form.user_rekvizitiYOOMONEY)
async def change_userRekvYOOMONEY(message: Message, state: FSMContext):
    await state.clear()
    # data = await state.get_data()
    # print(data)
    db.update_userRekvYOOMONEY(message.from_user.id, message.text)
    await message.answer('✅ Реквизиты успешно изменены!')
    # await state.set_state(Form.summaYOOMONEY)
    rekv = db.get_userRekvYOOMONEY(message.from_user.id)
    bal = db.get_balance(message.from_user.id)
    row1 = [InlineKeyboardButton(text='Вывести', callback_data='cash_outYOOMONEY-summa')]
    row2 = [InlineKeyboardButton(text='Изменить реквизиты', callback_data='update-userRekvYOOMONEY')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'♻ Вывод на <b>ЮMoney (РФ)</b>\n\n▪ Комиссия платежной системы: <b>3%</b>\n▪ Минимальная сумма для вывода: <b>100 ₽</b>\n\n👤 <b>Ваши реквизиты</b>: {rekv[0]}\n\n💵 Баланс для вывода: <b>{bal[1]}</b>',
                           reply_markup=keyboard, parse_mode='HTML')


@router.message(Form.user_rekvizitiSBP)
async def change_userRekvSBP(message: Message, state: FSMContext):
    await state.clear()
    db.update_userRekvSBP(message.from_user.id, message.text)
    await message.answer('✅ Реквизиты успешно изменены!')
    rekv = db.get_userRekvSBP(message.from_user.id)
    bal = db.get_balance(message.from_user.id)
    row1 = [InlineKeyboardButton(text='Вывести', callback_data='cash_outSBP-select')]
    row2 = [InlineKeyboardButton(text='Изменить реквизиты', callback_data='update-userRekvSBP')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'♻ Вывод <b>СБП (РФ)</b>\n\n▪ Комиссия платежной системы: <b>3%</b>\n▪ Минимальная сумма для вывода: <b>100 ₽</b>\n\n👤 <b>Ваши реквизиты</b>: {rekv[0]}\n\n💵 Баланс для вывода: <b>{bal[1]}</b>',
                           reply_markup=keyboard, parse_mode='HTML')


@router.message(Form.user_rekvizitiCARD)
async def change_userRekvCARD(message: Message, state: FSMContext):
    await state.clear()
    db.update_userRekvCARD(message.from_user.id, message.text)
    data = {
        "account": 849,
        "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
        "card_number": message.text
    }
    headers = {
        "Content-type": "application/json"
    }
    resp = requests.post("https://tg.keksik.io/api/1.0/payouts/check-bank-card", json=data, headers=headers)
    json_resp = resp.json()
    if json_resp['status'] == 'not_linked':
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "card-rub",
            "purse": message.text,
            "amount": 110000
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        json_resp = resp.json()
        print(json_resp)
    row = [InlineKeyboardButton(text='Привязать', url=json_resp["link_bank_card"])]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await message.answer(
        '✅ Для активации карты привяжите её по кнопке ниже\n\nОплатите 1₽ для привязки карты\nДеньги вернутся обратно на ваш баланс',
        reply_markup=keyboard)


@router.message(Form.summaYOOMONEY)
async def vvodRekvizitiYOOMONEY(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvYOOMONEY(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOyoomoney {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "ЮMoney {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaSber)
async def vvodRekvizitiSBER(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvSBP(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOsber {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "СБП Сбербанк {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaVtb)
async def vvodRekvizitiVTB(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvSBP(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOvtb {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "СБП ВТБ {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaGazprom)
async def vvodRekvizitigazprom(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvSBP(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOgazprom {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "СБП Газпромбанк {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaAlfa)
async def vvodRekvizitiafla(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvSBP(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOalfa {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "СБП Альфа-Банк {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaRosssel)
async def vvodRekvizitirossel(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvSBP(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOrossel {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "СБП Россельхозбанк {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaTink)
async def vvodRekvizititink(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvSBP(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOtbank {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "СБП Т-Банк {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaRaif)
async def vvodRekvizitiraif(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvSBP(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOraif {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "СБП Райффайзен Банк {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(Form.summaCard)
async def vvodRekviziti(message: Message, state: FSMContext):
    try:
        summa = float(message.text)
        rekv = db.get_userRekvCARD(message.from_user.id)
        balance = db.get_balance(message.from_user.id)
        if float(balance[1]) >= summa:
            if summa >= 1100:
                db.take_vivodBalance(message.from_user.id, summa)
                db.update_viveli(summa)
                await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
                row1 = [InlineKeyboardButton(text='Оплатить (авто)',
                                             callback_data=f'cash-outAUTOCARD {message.from_user.id} {summa}')]
                row2 = [InlineKeyboardButton(text='Оплатить (вручную)',
                                             callback_data=f'cash-outRUCH {message.from_user.id}')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
                await bot.send_message(chat_id=admin,
                                       text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{summa}" на реквизиты: "Банковская карта {rekv[0]}"',
                                       reply_markup=keyboard, parse_mode='HTML')
                await state.clear()
            else:
                row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
                await message.answer('❌ Минимальная сумма для вывода: <b>1100 ₽</b>', reply_markup=keyboard,
                                     parse_mode='HTML')
        else:
            row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
            await message.answer('❌ Недостаточно средств', reply_markup=keyboard)
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='cash-out')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неправильный ввод!', reply_markup=keyboard)


@router.message(F.text == '💸 Кошелёк')
async def balance(message: Message, state: FSMContext):
    await state.clear()
    balance = db.get_balance(message.from_user.id)
    msg = f'🆔 Ваш ID: <code>{message.from_user.id}</code>\n\n💵 Баланс для вывода: <b>{balance[1]} RUB</b>\n💸 Баланс для инвестиций: <b>{balance[0]} RUB</b> <a href="https://habrastorage.org/webt/xw/3r/lw/xw3rlwidbdqxp2hhpppr7tmx8ew.png">⠀</a>'
    row1 = [InlineKeyboardButton(text='➕ Пополнить', callback_data='cash-in'),
            InlineKeyboardButton(text='➖ Вывести', callback_data='cash-out')]
    row2 = [InlineKeyboardButton(text='🏦 VaxeeWallet', url='https://t.me/VaxeeWalletBot?start=VaxeeBot')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await message.answer(text=msg, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == '❓ Информация')
async def info(message: Message, state: FSMContext):
    await state.clear()
    row1 = [InlineKeyboardButton(text='💬 Отзывы', url=f't.me/{otzivi_channel[1:]}')]
    row2 = [InlineKeyboardButton(text='⚙️ Тех поддержка', url='t.me/dwmkpl'),
            InlineKeyboardButton(text='📌 Статья', url='https://telegra.ph/Informacionnaya-statya-06-19-4')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    await message.answer(
        text='⁉ Есть вопросы или проблемы?\n\n▪ Прочти информационную статью\n▪ Если нужна помощь напиши нам <a href="https://habrastorage.org/webt/wz/dg/tn/wzdgtnw_9n6ms2xdz8ni24lir18.png">⠀</a>',
        reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.in_(['referal-system']))
async def referals(callback: CallbackQuery):
    info = db.get_referals(callback.from_user.id)
    refPrize = db.get_refPrize()
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'<b>👥 Приглашай и зарабатывай без вложений</b>\n\n🗒 <b>Список наград за реферала:</b>\n▪ <b>{refPrize[0]}₽ на баланс для инвестиций</b>\n▪ <b>5% с пополнений реферала</b>\n▪ <b>5 VaxCoin</b>\n\n💸 Отчислений за пополнения: <b>{info[1]}₽</b>\n👥 Рефералов: <b>{info[0]} чел.</b>\n\n👤 Ваша реф.ссылка: <code>{bot_link}?start={callback.from_user.id}</code> <a href="https://habrastorage.org/webt/g5/5b/on/g55bonelx67lob4vz8uab7koiis.png">⠀</a>',
                           parse_mode='HTML')


@router.message(F.text == '📊 Статистика')
async def bot_stat(message: Message, state: FSMContext):
    await state.clear()
    row1 = [InlineKeyboardButton(text='💸 Топ инвесторов', callback_data='top-invest'),
            InlineKeyboardButton(text='👥 Топ рефоводов', callback_data='top-refs')]
    row2 = [InlineKeyboardButton(text='🏦 Топ по количеству VaxCoin', callback_data='top-coins')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    stats = db.get_BotStats()
    await message.answer(
        text=f'📊 <b>Статистика бота:</b>\n\n👨‍💻 Всего инвесторов: <b>{stats[0]}</b>\n📥 Пополнили: <b>{stats[1]} RUB</b>\n📤 Вывели: <b>{stats[2]} RUB</b> <a href="https://habrastorage.org/webt/ch/tn/qo/chtnqoz0wx0nrjculwqw_k5lhxi.png">⠀</a>',
        parse_mode='HTML', reply_markup=keyboard)


@router.callback_query(F.data.in_(['top-coins']))
async def top_coins(callback: CallbackQuery):
    top = db.get_topCoins()
    smiles = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    msg = '🏦 Топ по VaxCoin:\n'
    iter = -1
    for username, summa in top:
        iter += 1
        msg += f'\n{smiles[iter]} <a href="https://t.me/{username}">{username}</a> VaxCoin ➔ {float(summa):n} 💵'
    await bot.send_message(chat_id=callback.from_user.id, text=msg, parse_mode='HTML', disable_web_page_preview=True)


@router.callback_query(F.data.in_(['top-invest']))
async def top_invest(callback: CallbackQuery):
    top = db.get_topInvestors()
    smiles = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    msg = '🏆 Топ инвесторов:\n'
    iter = -1
    for username, summa in top:
        iter += 1
        msg += f'\n{smiles[iter]} <a href="https://t.me/{username}">{username}</a> вложил ➔ {float(summa):n}₽'
    await bot.send_message(chat_id=callback.from_user.id, text=msg, parse_mode='HTML', disable_web_page_preview=True)


@router.callback_query(F.data.in_(['top-refs']))
async def top_invest(callback: CallbackQuery):
    top = db.get_topReferals()
    smiles = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    msg = '👥 Топ по рефералам:\n'
    iter = -1
    for username, refs in top:
        iter += 1
        msg += f'\n{smiles[iter]} <a href="https://t.me/{username}">{username}</a> пригласил ➔ {refs}'
    await bot.send_message(chat_id=callback.from_user.id, text=msg, parse_mode='HTML', disable_web_page_preview=True)


@router.message(F.text == '📠 Калькулятор')
async def calculator_1(message: Message, state: FSMContext):
    await state.clear()
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await message.answer('<b>▪ Введите сумму, которую хотите рассчитать:</b>', parse_mode='HTML', reply_markup=keyboard)
    await state.set_state(Form.calc)


@router.message(Form.calc)
async def calculator_2(message: Message, state: FSMContext):
    try:
        await state.update_data(calc=float(message.text))
        await state.set_state(Form.calc)
        doxod = db.get_doxod(message.from_user.id)
        day = round(float(message.text) * float(doxod[1]), 2)
        month = round((float(message.text) * float(doxod[1])) * 30, 2)
        year = round((float(message.text) * float(doxod[1])) * 365, 2)
        msg = f'💸 В данном разделе вы можете <b>рассчитать</b> вашу <b>прибыль</b>, от суммы <b>инвестиции</b>:\n\n📈 Ваш процент дохода в сутки: {doxod[0]}%\n💵 Ваша инвестиция: <b>{message.text} RUB</b>\n\n▪ Прибыль в сутки: {day}₽\n▪ Прибыль в месяц: {month}₽\n▪ Прибыль в год: <b>{year}₽</b> <a href="https://habrastorage.org/webt/e4/7u/wp/e47uwpaczcllvou1wvr3erb03y8.png">⠀</a>'
        row1 = [InlineKeyboardButton(text='➕ Рассчитать повторно', callback_data='calculate-again')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row1])
        await message.answer(text=msg, parse_mode='HTML',
                             reply_markup=keyboard)
        await state.clear()
    except Exception as E:
        print(E)
        row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
        await message.answer('❌ Неверно указана сумма, попробуйте еще раз!', reply_markup=keyboard)


@router.callback_query(F.data.in_(['otmena']))
async def otmena_vvoda(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await bot.send_message(chat_id=callback.from_user.id, text='❌ Ввод отменен!')


@router.callback_query(F.data.in_('calculate-again'))
async def calculate_again(callback: CallbackQuery, state: FSMContext):
    row = [InlineKeyboardButton(text='⭕ Отменить', callback_data='otmena')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id, text='<b>▪ Введите сумму, которую хотите рассчитать:</b>',
                           parse_mode='HTML', reply_markup=keyboard)
    await state.set_state(Form.calc)


@router.message(F.text == '👨‍💻 Мой профиль')
async def profile(message: Message, state: FSMContext):
    user = db.get_profile(message.from_user.id)
    await state.clear()
    status = user[3]
    match status:
        case 0:
            status = 'нет статуса'
        case 1:
            status = 'VIP'
        case 2:
            status = 'PREMIUM'
    if message.from_user.id == admin:
        row1 = [InlineKeyboardButton(text='➕ Приобрести статус', callback_data='buyVIP')]
        row2 = [InlineKeyboardButton(text='👥 Реферальная система', callback_data='referal-system')]
        row3 = [InlineKeyboardButton(text='🗒️ Задания', callback_data='tasks')]
        row4 = [InlineKeyboardButton(text='👔 Админ-панель', callback_data='admin')]
        rows = [row1, row2, row3, row4]
    else:
        row1 = [InlineKeyboardButton(text='➕ Приобрести статус', callback_data='buyVIP')]
        row2 = [InlineKeyboardButton(text='👥 Реферальная система', callback_data='referal-system')]
        row3 = [InlineKeyboardButton(text='🗒️ Задания', callback_data='tasks')]
        rows = [row1, row2, row3]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    income = round(float(user[8]), 2)
    await message.answer(
        text=f'🆔 Ваш ID: <code>{message.from_user.id}</code>\n\n🏦 Доход в сутки: <b>{income} RUB</b>\n💴 Инвестировано: <b>{user[5]} RUB</b>\n💴 Баланс для вывода: <b>{user[6]} RUB</b>\n\n<b>👑 Статус: {status}\n📈 Процент дохода: {user[4]} %</b>\n<b>👥 Рефералов: {user[2]}</b> <a href="https://habrastorage.org/webt/gl/cs/zr/glcszryibrluuxrswulrexyni8s.png">⠀</a>',
        parse_mode='HTML', reply_markup=keyboard
    )


@router.callback_query(F.data.in_(['buyVIP']))
async def selectVIP(callback: CallbackQuery):
    await callback.message.delete()
    row1 = [InlineKeyboardButton(text='💸 VIP', callback_data='buy-vip')]
    row2 = [InlineKeyboardButton(text='👑 PREMIUM', callback_data='buy-premium')]
    rows = [row1, row2]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Выберите нужный вам статус: <a href="https://habrastorage.org/webt/hq/sh/u9/hqshu94xurl3n9oetezuxcln4ye.png">⠀</a>',
                           reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.in_(['buy-vip']))
async def buyVIP(callback: CallbackQuery):
    await callback.message.delete()
    row1 = [InlineKeyboardButton(text='💸 Keksik', web_app=WebAppInfo(url='https://tg.keksik.io/@Vaxee_bot'))]
    row2 = [InlineKeyboardButton(text='💸 Оплата через администратора', callback_data='pay-admin-vip')]
    row3 = [InlineKeyboardButton(text='💸 Yoomoney', callback_data='pay-site-vip-card')]
    rows = [row1, row2]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🏵️| VIP\n__________________________________________\n💰 Процент дохода с инвестиций: 5% в сутки\n💰 Процент дохода VaxCoin: 2.5% в сутки\n\n💵 Стоимость: 3000₽\n\n‼ При оплате через Keksik, в комментариях к донату указывайте "VIP", иначе средства будут зачислены на баланс для инвестиций.',
                           reply_markup=keyboard)


@router.callback_query(F.data.in_(['pay-admin-vip']))
async def payAdmin_vip(callback: CallbackQuery):
    row1 = [InlineKeyboardButton(text='➕ Оплата картой', callback_data='payAdmin-vip-card')]
    row2 = [InlineKeyboardButton(text='➕ Криптовалюта', callback_data='payAdmin-vip-crypto')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row2])
    await bot.send_message(chat_id=callback.from_user.id, text='💸 Выберите удобный способ оплаты:',
                           reply_markup=keyboard)


@router.callback_query(F.data.in_(['pay-admin-premium']))
async def payAdmin_vip(callback: CallbackQuery):
    row1 = [InlineKeyboardButton(text='➕ Оплата картой', callback_data='payAdmin-premium-card')]
    row2 = [InlineKeyboardButton(text='➕ Криптовалюта', callback_data='payAdmin-premium-crypto')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row2])
    await bot.send_message(chat_id=callback.from_user.id, text='💸 Выберите удобный способ оплаты:',
                           reply_markup=keyboard)


@router.callback_query(F.data.in_(['payAdmin-vip-card']))
async def payAdminCard_vip(callback: CallbackQuery):
    name = db.get_rekviziti('karta')
    row = [InlineKeyboardButton(text='✅ Оплатил',
                                callback_data=f'pay-admin-vip-card-checkpayment {callback.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'💸 Сумма для оплаты <b>3000₽</b>\n\n💵 <b>Статус будет выдан после проверки платежа</b>\n\n✅ Сохраните скриншот для подтверждения\n\n\n▪ Yoomoney: <code>{name[0]}</code>\n\n\n<code>Контакт администратора:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)


@router.callback_query(F.data.in_(['payAdmin-premium-card']))
async def payAdminCard_vip(callback: CallbackQuery):
    name = db.get_rekviziti('karta')
    row = [InlineKeyboardButton(text='✅ Оплатил',
                                callback_data=f'pay-admin-premium-card-checkpayment {callback.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'💸 Сумма для оплаты <b>8000₽</b>\n\n💵 <b>Статус будет выдан после проверки платежа</b>\n\n✅ Сохраните скриншот для подтверждения\n\n\n▪ Yoomoney: <code>{name[0]}</code>\n\n\n<code>Контакт администратора:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)


@router.callback_query(F.data.in_(['payAdmin-vip-crypto', 'payAdmin-premium-crypto']))
async def vipCrypto(callback: CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,
                           text='💸 Для оплаты криптовалютой свяжитесь с администратором\n\n<code>Контакт администратора:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                           parse_mode='HTML', disable_web_page_preview=True)


@router.callback_query(F.data.in_(['buy-premium']))
async def buyPREMIUM(callback: CallbackQuery):
    row1 = [InlineKeyboardButton(text='💸 Keksik', web_app=WebAppInfo(url='https://tg.keksik.io/@Vaxee_bot'))]
    row2 = [InlineKeyboardButton(text='💸 Оплата через администратора', callback_data='pay-admin-premium')]
    row3 = [InlineKeyboardButton(text='💸 Yoomoney', callback_data='pay-site-premium-card')]
    rows = [row1, row2]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    await bot.send_message(chat_id=callback.from_user.id,
                           text='🏵️| PREMIUM\n__________________________________________\n💰 Процент дохода с инвестиций: 10% в сутки\n💰 Процент дохода VaxCoin: 5% в сутки\n\n💵 Стоимость: 8000₽\n\n‼ При оплате через Keksik, в комментариях к донату указывайте "PREMIUM", иначе средства будут зачислены на баланс для инвестиций.',
                           reply_markup=keyboard)


@router.callback_query(F.data.in_(['pay-site-vip-card']))
async def paySite_premium(callback: CallbackQuery):
    label = generate_random_string(12)
    quickpay = Quickpay(
        receiver="4100118701003387",
        quickpay_form="shop",
        targets="VIP Статус",
        paymentType="SB",
        sum=3000,
        label=label
    )
    row1 = [InlineKeyboardButton(text='💳 Оплатить', url=quickpay.redirected_url)]
    row2 = [InlineKeyboardButton(text='✅ Проверить оплату', callback_data=f'pay-site-vip-card-checkpayment {label}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    msg = f'💸 Сумма для оплаты <b>3000₽</b>\n\n💵 <b>Статус будет выдан после нажатия на кнопку «Проверить оплату»</b>\n\n✅ <b>На всякий случай, сохраните скриншот</b>\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>'
    await bot.send_message(chat_id=callback.from_user.id, text=msg, parse_mode='HTML', reply_markup=keyboard,
                           disable_web_page_preview=True)


@router.callback_query(F.data.in_(['pay-site-premium-card']))
async def paySite_premium(callback: CallbackQuery):
    label = generate_random_string(12)
    quickpay = Quickpay(
        receiver="4100118701003387",
        quickpay_form="shop",
        targets="PREMIUM Статус",
        paymentType="SB",
        sum=8000,
        label=label
    )
    row1 = [InlineKeyboardButton(text='💳 Оплатить', url=quickpay.redirected_url)]
    row2 = [
        InlineKeyboardButton(text='✅ Проверить оплату', callback_data=f'pay-site-premium-card-checkpayment {label}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    msg = f'💸 Сумма для оплаты <b>8000₽</b>\n\n💵 <b>Статус будет выдан после нажатия на кнопку «Проверить оплату»</b>\n\n✅ <b>На всякий случай, сохраните скриншот</b>\n\n<code>Контакт администратора для связи:</code> <a href="https://t.me/dwmkpl">@dwmkpl</a>'
    await bot.send_message(chat_id=callback.from_user.id, text=msg, parse_mode='HTML', reply_markup=keyboard,
                           disable_web_page_preview=True)


@router.message(Form.payAdminCard_vip)
async def checkpaymentAdmin_vip(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Принять', callback_data=f'admin-accept-vip {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-vip {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение оплаты VIP',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(payAdminCard_vip=message)
    await state.set_state(Form.payAdminCard_vip)
    await state.clear()


@router.message(Form.payAdminCard_premium)
async def checkpaymentAdmin_premium(message: Message, state: FSMContext):
    await message.copy_to(admin)
    row = [InlineKeyboardButton(text='✅ Принять', callback_data=f'admin-accept-premium {message.from_user.id}'),
           InlineKeyboardButton(text='⛔ Отклонить', callback_data=f'admin-decline-premium {message.from_user.id}')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row])
    await bot.send_message(chat_id=admin,
                           text=f'🆔 <code>{message.from_user.id}</code> запросил подтверждение оплаты PREMIUM',
                           reply_markup=keyboard, parse_mode='HTML')
    await state.update_data(payAdminCard_premium=message)
    await state.set_state(Form.payAdminCard_premium)
    await state.clear()


@router.callback_query(F.data.contains("admin-vvod-usdt"))
async def pay_usdt(message: CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
    await state.set_state(Form.admin_replenishment_usdt)


@router.callback_query(F.data.contains("admin-decline-usdt"))
async def decline_usdt(message: CallbackQuery, state: FSMContext):
    user_id = message.data.split(' ')[1]
    await bot.send_message(chat_id=message.from_user.id,
                           text='<b>Запрос на ввод суммы отклонен</b>', parse_mode='HTML')
    await bot.send_message(chat_id=user_id,
                           text='❌ Ошибка ваш платеж не найден\n\n⁉ Если у вас есть вопросы обратитесь к модератору @dwmkpl')
    await state.clear()


@router.message(Form.admin_replenishment_usdt)
async def replenishment_usdt(message: Message, state: FSMContext):
    data = message.text.split(",")
    user_id = int(data[0].replace(" ", ""))
    amount = float(data[1].replace(" ", ""))
    user = db.get_profile(user_id)
    user_amount = float(user[5]) + amount
    Transaction.replenishment(user_id, user_amount)
    db.update_popolnili(user_amount)
    ref = db.get_ref(user_id)
    if ref[0] != 0:
        db.give_investBalance(ref[0], user_amount * 0.05)
        db.update_refDoxod(ref[0], user_amount * 0.05)
    await bot.send_message(chat_id=user_id,
                           text=f'✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                           parse_mode='HTML')
    await bot.send_message(chat_id=message.from_user.id, text="Баланс пользователя пополнен")
    await state.clear()


@router.callback_query()
async def pay_site_premium_card_chek(callback: CallbackQuery, state: FSMContext):
    if callback.data.split(' ')[0] == 'pay-site-premium-card-checkpayment':
        label = callback.data.split(' ')[1]
        client = Client(yoomoney_token)
        history = client.operation_history(label=label)
        if len(history.operations) == 1:
            await callback.message.delete()
            await bot.send_message(chat_id=callback.from_user.id,
                                   text='✅ <b>Статус выдан ваш процента дохода увеличен</b>', parse_mode='HTML')
            db.change_vip(callback.from_user.id, 2)
        else:
            await callback.answer(
                '❌ Ошибка ваш платеж не найден\n\n⁉ Если у вас есть вопросы обратитесь к модератору @dwmkpl',
                show_alert=True)
    elif callback.data.split(' ')[0] == 'pay-site-vip-card-checkpayment':
        label = callback.data.split(' ')[1]
        client = Client(yoomoney_token)
        history = client.operation_history(label=label)
        if len(history.operations) == 1:
            await callback.message.delete()
            await bot.send_message(chat_id=callback.from_user.id,
                                   text='✅ <b>Статус выдан ваш процента дохода увеличен</b>', parse_mode='HTML')
            db.change_vip(callback.from_user.id, 1)
        else:
            await callback.answer(
                '❌ Ошибка ваш платеж не найден\n\n⁉ Если у вас есть вопросы обратитесь к модератору @dwmkpl',
                show_alert=True)
    elif callback.data.split(' ')[0] == 'cash_inSITE-card-check':
        label = callback.data.split(' ')[1]
        client = Client(yoomoney_token)
        history = client.operation_history(label=label)
        if len(history.operations) == 1:
            await callback.message.delete()
            await bot.send_message(chat_id=callback.from_user.id,
                                   text=f'✅ <b>Средства зачислены на ваш баланс для инвестиций</b>',
                                   parse_mode='HTML')
            db.give_investBalance(callback.from_user.id, history.operations[0].amount)
            db.update_popolnili(history.operations[0].amount)
            ref = db.get_ref(callback.from_user.id)
            if ref[0] != 0:
                db.give_investBalance(ref[0], history.operations[0].amount * 0.05)
                db.update_refDoxod(ref[0], history.operations[0].amount * 0.05)
        else:
            await callback.answer(
                '❌ Ошибка ваш платеж не найден\n\n⁉ Если у вас есть вопросы обратитесь к модератору @dwmkpl',
                show_alert=True)
    elif callback.data.split(' ')[0] == 'pay-admin-vip-card-checkpayment':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=user_id, text='📎 Отправьте скриншот оплаты.')
        await state.set_state(Form.payAdminCard_vip)
    elif callback.data.split(' ')[0] == 'pay-admin-premium-card-checkpayment':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=user_id, text='📎 Отправьте скриншот оплаты.')
        await state.set_state(Form.payAdminCard_premium)
    elif callback.data.split(' ')[0] == 'admin-accept-vip':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='✅ VIP выдана')
        await bot.send_message(chat_id=user_id, text=f'✅ <b>Статус выдан ваш процент дохода увеличен</b>',
                               parse_mode='HTML')
        db.change_vip(user_id, 1)
    elif callback.data.split(' ')[0] == 'admin-accept-premium':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='✅ PREMIUM выдана')
        await bot.send_message(chat_id=user_id, text=f'✅ <b>Статус выдан ваш процент дохода увеличен</b>',
                               parse_mode='HTML')
        db.change_vip(user_id, 2)
    elif callback.data.split(' ')[0] == 'admin-decline-vip':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-decline-premium':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-vvod-card':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
        await state.set_state(Form.adminVvod_card)
    elif callback.data.split(' ')[0] == 'admin-decline-card':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-vvod-btc':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
        await state.set_state(Form.adminVvod_btc)
    elif callback.data.split(' ')[0] == 'admin-decline-btc':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-vvod-eth':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
        await state.set_state(Form.adminVvod_eth)
    elif callback.data.split(' ')[0] == 'admin-decline-eth':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-vvod-ltc':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
        await state.set_state(Form.adminVvod_ltc)
    elif callback.data.split(' ')[0] == 'admin-decline-ltc':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-vvod-ton':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
        await state.set_state(Form.adminVvod_ton)
    elif callback.data.split(' ')[0] == 'admin-decline-ton':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-vvod-atom':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
        await state.set_state(Form.adminVvod_atom)
    elif callback.data.split(' ')[0] == 'admin-decline-atom':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'admin-vvod-sol':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Введите ID и сумму зачисления:\n\nНапример: 123456, 100')
        await state.set_state(Form.adminVvod_sol)
    elif callback.data.split(' ')[0] == 'admin-decline-sol':
        user_id = callback.data.split(' ')[1]
        await bot.send_message(chat_id=admin, text='⛔ Отказано')
        await bot.send_message(chat_id=user_id,
                               text=f'❌ <b>Ошибка ваш платеж не найден</b>\n\n⁉ <b>Если у вас есть вопросы обратитесь к модератору</b> <a href="https://t.me/dwmkpl">@dwmkpl</a>',
                               parse_mode='HTML')
    elif callback.data.split(' ')[0] == 'cash-outRUCH':
        user_id = callback.data.split(' ')[1]
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=callback.from_user.id, text='Успешно!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOCARD':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvCARD(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "card-rub",
            "purse": rekv,
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOsber':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvSBP(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "sbp",
            "purse": rekv,
            "bank": "1enc00000111",
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOvtb':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvSBP(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "sbp",
            "purse": rekv,
            "bank": "1enc00000005",
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOgazprom':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvSBP(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "sbp",
            "purse": rekv,
            "bank": "1enc00000001",
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOalfa':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvSBP(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "sbp",
            "purse": rekv,
            "bank": "1enc00000008",
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOrossel':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvSBP(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "sbp",
            "purse": rekv,
            "bank": "1enc00000020",
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOtbank':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvSBP(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "sbp",
            "purse": rekv,
            "bank": "1enc00000004",
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOraif':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvSBP(user_id)
        rekv = rekv[0]
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "sbp",
            "purse": rekv,
            "bank": "1enc00000007",
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')
    elif callback.data.split(' ')[0] == 'cash-outAUTOyoomoney':
        user_id = callback.data.split(' ')[1]
        summa = float(callback.data.split(' ')[2])
        rekv = db.get_userRekvYOOMONEY(user_id)
        rekv = rekv[0]
        # new_rekv = f"{rekv[0:2]} {rekv[2:5]} {rekv[5:8]} {rekv[8:10]} {rekv[10:12]}"
        data = {
            "account": 849,
            "token": "5be1974b4c0e8f289ac074dad69f1477bfcf4831213ded78f7",
            "system": "yoomoney",
            "purse": rekv,
            "amount": f"{int(summa)}00"
        }
        headers = {
            "Content-type": "application/json"
        }
        resp = requests.post("https://tg.keksik.io/api/1.0/payouts/create", json=data, headers=headers)
        row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
        await bot.send_message(chat_id=user_id,
                               text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                               reply_markup=keyboard1)
        await bot.send_message(chat_id=admin, text='Заявка на вывод создана!')
        json_resp = resp.json()
        if json_resp["success"] == False:
            db.give_vivodBalance(user_id, summa)
            await bot.send_message(chat_id=admin, text='Заявка на вывод отклонена!')


@router.message()
async def check_promo(message: Message):
    # promo = db.get_promo(message.from_user.id, message.text)
    all_promo = db.get_all_promo()
    for promo in all_promo:
        if message.text == promo:
            promo_select = db.get_promo(message.from_user.id, promo)
            res = db.use_promo(message.from_user.id, str(promo_select[0]))
            if res:
                return await message.answer(
                    f'💯 Промокод активирован!\n💲 На инвестиционный баланс зачислено <b>{promo[1]}₽</b>',
                    parse_mode='HTML')

            else:
                return await message.answer(
                    '📛 Активации промокода закончились или вы уже использовали данный промокод!')

    # if promo:
    #     res = db.use_promo(message.from_user.id, str(promo[0]))
    #     if res:
    #         await message.answer(f'💯 Промокод активирован!\n💲 На инвестиционный баланс зачислено <b>{promo[1]}₽</b>',
    #                              parse_mode='HTML')

    await message.answer(f'📛 {message.text} - такого промокода нет!')


bot_router = router
