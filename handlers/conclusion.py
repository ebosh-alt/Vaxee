from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from data.config import bonus_system, bot, db, COUNT_REFERRAL, AMOUNT_REFERRAL_KING, COIN_REFERRAL_KING, AMOUNT_INVEST, \
    AMOUNT_PROFIT_INVEST, COIN_PROFIT_INVEST, channel, COIN_FOLLOW_NEWS, AMOUNT_FOLLOW_NEWS, usdt_requisites, \
    LIMIT_CONCLUSION_USDT, admin
from service.GetMessage import get_mes, get_text
from service.keyboards import Keyboards as kb
from service.keyboards import Builder
from service.states import Form

router = Router()


@router.callback_query(F.data == "cash_out_usdt")
async def cash_out_usdt(message: CallbackQuery, state: FSMContext):
    id = message.from_user.id
    await bot.send_message(chat_id=id,
                           text=get_mes("conclusion"),
                           reply_markup=kb.conclusion_usdt_kb)
    await state.clear()


@router.callback_query(
    F.data.in_(["conclusion_usdt_network_TRC_20", "conclusion_usdt_network_BNB", "conclusion_usdt_network_Toncoin"]))
async def conclusion_usdt_network(message: CallbackQuery, state: FSMContext):
    id = message.from_user.id
    requisites = usdt_requisites.get_requisites(id)
    user = db.get_profile(id)
    await state.set_state(Form.conclusion_usdt)
    await state.update_data(network=message.data.replace("conclusion_usdt_network_", ""))
    if message.data == "conclusion_usdt_network_TRC_20":
        text = get_text(get_mes("conclusion_trc_20", requisites=requisites.trc_20, amount=user[6]))

    elif message.data == "conclusion_usdt_network_BNB":
        text = get_text(get_mes("conclusion_bnb", requisites=requisites.bnb, amount=user[6]))
    else:
        text = get_text(get_mes("conclusion_toncoin", requisites=requisites.toncoin, amount=user[6]))

    await bot.send_message(chat_id=id,
                           text=text,
                           reply_markup=kb.conclusion_kb,
                           parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(F.data == "conclusion_usdt_network")
async def conclusion_usdt_network_s(message: CallbackQuery, state: FSMContext):
    id = message.from_user.id
    data = await state.get_data()
    network = data["network"]
    requisites = usdt_requisites.get_requisites(id)
    await state.set_state(Form.input_amount_usdt)
    await state.update_data(network=network)
    if network == "TRC_20":
        if requisites.trc_20 == "":
            await bot.answer_callback_query(callback_query_id=message.id,
                                            text="Вы не вввели адрес сети")
        else:
            await message.message.answer(text="♻️ Введите сумму вывода:",
                                         reply_markup=kb.cancel_change_requisites_usdt_network_kb)
    elif network == "BNB":
        if requisites.bnb == "":
            await bot.answer_callback_query(callback_query_id=message.id,
                                            text="Вы не вввели адрес сети")
        else:
            await message.message.answer(text="♻️ Введите сумму вывода:",
                                         reply_markup=kb.cancel_change_requisites_usdt_network_kb)
    elif network == "Toncoin":
        if requisites.toncoin == "":
            await bot.answer_callback_query(callback_query_id=message.id,
                                            text="Вы не вввели адрес сети")
        else:
            await message.message.answer(text="♻️ Введите сумму вывода:",
                                         reply_markup=kb.cancel_change_requisites_usdt_network_kb)


@router.message(Form.input_amount_usdt)
async def input_amount(message: Message, state: FSMContext):
    id = message.from_user.id
    data = await state.get_data()
    network = data["network"]
    try:
        user = db.get_profile(id)
        amount = float(message.text)
        requisites = usdt_requisites.get_requisites(id)
        if network == "TRC_20":
            requisite = requisites.trc_20
        elif network == "BNB":
            requisite = requisites.bnb
        else:
            requisite = requisites.toncoin
        if amount < LIMIT_CONCLUSION_USDT:
            await bot.send_message(chat_id=id,
                                   text="❌ Сумма вывода должна быть больше " + str(LIMIT_CONCLUSION_USDT) + " рублей",
                                   reply_markup=kb.cancel_change_requisites_usdt_network_kb)
        elif float(user[6]) < amount:
            await bot.send_message(chat_id=id,
                                   text="❌ Недостаточно средств",
                                   reply_markup=kb.cancel_change_requisites_usdt_network_kb)
        else:
            db.take_vivodBalance(id, amount)
            keyboard = Builder.create_keyboard({"Оплатить": f"confirm_conclusion {id}"})
            await bot.send_message(chat_id=message.from_user.id, text='✅ Заявка на вывод успешно создана')
            await bot.send_message(chat_id=admin,
                                   text=f'🆔 <code>{message.from_user.id}</code> запросил выплату в размере "{amount}" на адрес:'
                                        f'{network}\n<code>{requisite}</code>',
                                   reply_markup=keyboard,
                                   parse_mode='HTML')
            await state.clear()
    except:
        await bot.send_message(chat_id=id,
                               text="❌ Введено неверное значение!",
                               reply_markup=kb.cancel_change_requisites_usdt_network_kb)


@router.callback_query(F.data.contains("confirm_conclusion"))
async def confirm_conclusion(message: CallbackQuery):
    user_id = message.data.split(' ')[1]
    print(user_id)
    row1 = [InlineKeyboardButton(text='✅ Отзывы', url='https://t.me/vaxeeotz/8')]
    keyboard1 = InlineKeyboardMarkup(inline_keyboard=[row1])
    await bot.send_message(chat_id=user_id,
                           text='♻|Ваша заявка обрабатывается.\n\n🗯 Оставьте отзыв после поступления средств',
                           reply_markup=keyboard1)
    await bot.send_message(chat_id=message.from_user.id, text='Успешно!')


@router.callback_query(F.data == "change_requisites_usdt_network")
async def change_requisites_usdt_network(message: CallbackQuery, state: FSMContext):
    id = message.from_user.id
    data = await state.get_data()
    network = data["network"]
    await state.set_state(Form.change_requisites_usdt_network)
    await state.update_data(network=network)
    await bot.send_message(chat_id=id,
                           text="💳 Введите новый адрес:",
                           reply_markup=kb.cancel_change_requisites_usdt_network_kb)


@router.message(Form.change_requisites_usdt_network)
async def change_requisites_usdt_network(message: Message, state: FSMContext):
    id = message.from_user.id
    data = await state.get_data()
    network = data["network"]
    user = db.get_profile(id)
    if network == "TRC_20":
        usdt_requisites.update_trc_20(id, message.text)
        requisites = usdt_requisites.get_requisites(id)
        text = get_text(get_mes("conclusion_trc_20", requisites=requisites.trc_20, amount=user[6]))

    elif network == "BNB":
        usdt_requisites.update_bnb(id, message.text)
        requisites = usdt_requisites.get_requisites(id)
        text = get_text(get_mes("conclusion_bnb", requisites=requisites.bnb, amount=user[6]))

    else:
        usdt_requisites.update_toncoin(id, message.text)
        requisites = usdt_requisites.get_requisites(id)
        text = get_text(get_mes("conclusion_toncoin", requisites=requisites.toncoin, amount=user[6]))
    await bot.send_message(chat_id=id,
                           text="Адрес успешно изменен!")
    await bot.send_message(chat_id=id,
                           text=text,
                           reply_markup=kb.conclusion_kb,
                           parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(Form.conclusion_usdt)
    await state.update_data(network=network)

conclusion_rt = router
