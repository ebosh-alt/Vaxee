import logging

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

logger = logging.getLogger(__name__)


class Builder:
    @staticmethod
    def create_keyboard(name_buttons: list | dict, *sizes: int) -> types.InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        if type(name_buttons) is list:
            for name_button in name_buttons:
                keyboard.button(
                    text=name_button, callback_data=name_button
                )
        elif type(name_buttons) is dict:
            for name_button in name_buttons:
                if "http" in name_buttons[name_button] or "@" in name_buttons[name_button]:
                    keyboard.button(
                        text=name_button, url=name_buttons[name_button]
                    )
                else:
                    keyboard.button(
                        text=name_button, callback_data=name_buttons[name_button]
                    )

        if len(sizes) == 0:
            sizes = (1,)
        keyboard.adjust(*sizes)
        return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def create_reply_keyboard(name_buttons: list = None, one_time_keyboard: bool = False, request_contact: bool = False,
                              *sizes) -> types.ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardBuilder()
        for name_button in name_buttons:
            if name_button is not tuple:
                keyboard.button(
                    text=name_button,
                    request_contact=request_contact
                )
            else:
                keyboard.button(
                    text=name_button,
                    request_contact=request_contact

                )
        if len(sizes) == 0:
            sizes = (1,)
        keyboard.adjust(*sizes)
        return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)

    @staticmethod
    def create_force_reply(text: str):
        return types.ForceReply(input_field_placeholder=text)


class Keyboards:
    task_menu_kb = Builder.create_keyboard({
        "🥇 Реферальный король": "referral_king",
        "🥈 Выгодная инвестиция": "profit_invest",
        "🥉 Слежу за новостями": "follow_news",
    })

    referral_king_receive_kb = Builder.create_keyboard({"✅ Получить бонус": "receive_referral_king"})
    profit_invest_receive_kb = Builder.create_keyboard({"✅ Получить бонус": "receive_profit_invest"})
    follow_news_receive_kb = Builder.create_keyboard({"✅ Получить бонус": "receive_follow_news"})

    received_kb = Builder.create_keyboard({"❌ Бонус уже получен": "received_referral_king"})

    done_kb = Builder.create_keyboard({"✅ Бонус получен и начислен на Ваш баланс": "done_referral_king"})

    no_complete_kb = Builder.create_keyboard({"❌ Вы не выполнили данное задание": "no_complete_referral_king"})

    usdt_network_kb = Builder.create_keyboard({
        "Tron (TRC20)": "usdt_network_trc_20",
        "BNB Smart Chain (BEP20)": "usdt_network_bep_20",
        "Toncoin": "usdt_network_ton"
    })

    conclusion_usdt_kb = Builder.create_keyboard({
        "Tron (TRC20)": "conclusion_usdt_network_TRC_20",
        "BNB Smart Chain (BEP20)": "conclusion_usdt_network_BNB",
        "Toncoin": "conclusion_usdt_network_Toncoin"
    })

    conclusion_kb = Builder.create_keyboard({
        "Вывести": "conclusion_usdt_network",
        "Изменить адрес": "change_requisites_usdt_network",
    })

    cancel_change_requisites_usdt_network_kb = Builder.create_keyboard({
        "⭕️ Отменить": 'cash_out_usdt'
    })

    confirm_conclusion = Builder.create_keyboard({"Оплатить": "confirm_conclusion"})
