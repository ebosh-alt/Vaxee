import locale

from aiogram import Bot, Dispatcher

from entity.database import database, BonusSystem, UsdtRequisites

token = '7217884803:AAHaE-w8B4WhdPBON-AHqx1fux8xlDZmNTU'
admin = 5530586693
channel = '@vaxinvest'
bot_link = 'https://t.me/Vaxee_bot'
# bot_link = 'https://t.me/Vaxee_bot'
otzivi_channel = "@vaxeeotz"
yoomoney_token = ''
bot = Bot(token)
dp = Dispatcher()
db = database("data/users.db")
bonus_system = BonusSystem()
bonus_system.create()
usdt_requisites = UsdtRequisites()
usdt_requisites.create()
locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

COUNT_REFERRAL = 300
AMOUNT_INVEST = 2000

AMOUNT_REFERRAL_KING = 1000
COIN_REFERRAL_KING = 500

AMOUNT_PROFIT_INVEST = 250
COIN_PROFIT_INVEST = 200

AMOUNT_FOLLOW_NEWS = 25
COIN_FOLLOW_NEWS = 50

LIMIT_CONCLUSION_USDT = 2000
