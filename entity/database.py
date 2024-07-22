import sqlite3

from pydantic import BaseModel

from service.sqsnip import database as db


class Statuses(BaseModel):
    referral_king: bool
    profit_invest: bool
    follow_news: bool


class Requisites(BaseModel):
    trc_20: str
    bnb: str
    toncoin: str


class BonusSystem:
    @staticmethod
    def create():
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()

        sql.execute(f"""CREATE TABLE IF NOT EXISTS bonus_system (
                                id integer primary key autoincrement not null,
                                user_id integer,
                                referral_king boolean default false,
                                profit_invest boolean default false,
                                follow_news boolean default false
                            )""")
        conn.commit()
        conn.close()

    @staticmethod
    def in_(user_id: int) -> bool:
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""SELECT user_id FROM bonus_system WHERE user_id = {user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        if result is None:
            return False
        elif len(result) == 0:
            return False
        else:
            return True

    @staticmethod
    def create_entity(user_id: int):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()

        sql.execute(f"""INSERT INTO bonus_system (user_id) VALUES ({user_id})""")
        conn.commit()
        conn.close()

    @staticmethod
    def get_statuses(user_id) -> Statuses:
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()

        sql.execute(f"""SELECT referral_king, profit_invest, follow_news from bonus_system 
                                                                where user_id = {user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return Statuses(
            referral_king=result[0],
            profit_invest=result[1],
            follow_news=result[2])

    @staticmethod
    def update_referral_king(user_id):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE bonus_system SET referral_king=true WHERE user_id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def update_profit_invest(user_id):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE bonus_system SET profit_invest=true WHERE user_id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def update_follow_news(user_id):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE bonus_system SET follow_news=true WHERE user_id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def award(user_id, amount, coin):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE users SET invest_bal={amount}, coins={coin} WHERE id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result


class Transaction:
    @staticmethod
    def replenishment(user_id, amount):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE users SET invest_bal={amount} WHERE id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result


class UsdtRequisites:
    @staticmethod
    def create():
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()

        sql.execute(f"""CREATE TABLE IF NOT EXISTS usdt_requisites (
                                id integer primary key autoincrement not null,
                                user_id integer,
                                trc_20 varchar(200) default '',
                                bnb varchar(200) default '',
                                toncoin varchar(200) default ''
                            )""")
        conn.commit()
        conn.close()

    @staticmethod
    def create_entity(user_id: int):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()

        sql.execute(f"""INSERT INTO usdt_requisites (user_id) VALUES ({user_id})""")
        conn.commit()
        conn.close()

    @staticmethod
    def in_(user_id: int) -> bool:
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""SELECT user_id FROM usdt_requisites WHERE user_id = {user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        if result is None:
            return False
        elif len(result) == 0:
            return False
        else:
            return True

    @staticmethod
    def get_requisites(user_id) -> Requisites:
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()

        sql.execute(f"""SELECT trc_20, bnb, toncoin from usdt_requisites 
                                                                where user_id = {user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return Requisites(
            trc_20=result[0],
            bnb=result[1],
            toncoin=result[2])

    @staticmethod
    def update_trc_20(user_id, requisites):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE usdt_requisites SET trc_20='{requisites}' WHERE user_id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def update_bnb(user_id, requisites):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE usdt_requisites SET bnb='{requisites}' WHERE user_id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def update_toncoin(user_id, requisites):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE usdt_requisites SET toncoin='{requisites}' WHERE user_id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result


class database:
    def __init__(self, db_name: str):
        self.users = db(db_name, "users", """
            id INTEGER,
            doxodbyREF TEXT,
            referals INTEGER,
            vip INTEGER,
            percent_doxod INTEGER,
            in_invest TEXT,
            vivod_bal TEXT,
            invest_bal TEXT,
            doxod TEXT,
            referal INTEGER,
            username TEXT,
            coins INT,
            rekvizitiCARD TEXT,
            rekvizitiSBP TEXT,
            rekvizitiYOOMONEY TEXT
        """)

        self.bot = db(db_name, "bot_settings", """
            newid INT,
            popolnili TEXT,
            viveli TEXT,
            referalPrize TEXT,
            karta TEXT,
            btc TEXT,
            eth TEXT,
            ltc TEXT,
            ton TEXT,
            atom TEXT,
            sol TEXT
        """)

        self.promocode = db(db_name, "promocodes", """
            name TEXT,
            nagrada TEXT,
            activates INT,
            used TEXT
        """)

        check = self.bot.select('*', {'newid': 0}, True)
        if len(check) == 0:
            self.bot.insert([0, '0.00', '0.00', '3', '', '', '', '', '', '', ''])

    def new_user(self, user_id: int, username: str):
        return self.users.insert(
            [user_id, '0.00', 0, 0, 2, '0.00', '0.00', '0.00', '0.00', 0, username, 0, 'не указаны', 'не указаны',
             'не указаны'])

    def update_popolnili(self, amount: float):
        cur_popolnili = self.bot.select('popolnili', {'newid': 0}, False)
        self.bot.update({'popolnili': float(cur_popolnili[0]) + amount}, {'newid': 0})

    def update_userRekvCARD(self, user_id: int, rekv: str):
        self.users.update({'rekvizitiCARD': rekv}, {'id': user_id})

    def get_userRekvCARD(self, user_id: int):
        return self.users.select('rekvizitiCARD', {'id': user_id}, False)

    def update_userRekvSBP(self, user_id: int, rekv: str):
        self.users.update({'rekvizitiSBP': rekv}, {'id': user_id})

    def get_userRekvSBP(self, user_id: int):
        return self.users.select('rekvizitiSBP', {'id': user_id}, False)

    def update_userRekvYOOMONEY(self, user_id: int, rekv: str):
        self.users.update({'rekvizitiYOOMONEY': rekv}, {'id': user_id})

    def get_userRekvYOOMONEY(self, user_id: int):
        return self.users.select('rekvizitiYOOMONEY', {'id': user_id}, False)

    def update_viveli(self, amount: float):
        cur_viveli = self.bot.select('viveli', {'newid': 0}, False)
        self.bot.update({'viveli': float(cur_viveli[0]) + amount}, {'newid': 0})

    def get_ref(self, user_id: int):
        return self.users.select('referal', {'id': user_id}, False)

    def update_refDoxod(self, user_id: int, amount: float):
        cur_doxod = self.users.select('doxodbyRef', {'id': user_id}, False)
        self.users.update({'doxodbyRef': float(cur_doxod[0]) + amount}, {'id': user_id})

    def get_accruing(self):
        return self.users.select('id, doxod', 'id != 0', True)

    def give_vivodBalance(self, user_id: int, summa: float):
        cur_balance = self.users.select('vivod_bal', {'id': user_id}, False)
        self.users.update({'vivod_bal': str(float(cur_balance[0]) + summa)}, {'id': user_id})

    def get_rekviziti(self, name: str):
        return self.bot.select(f'{name}', {'newid': 0}, False)

    def take_vivodBalance(self, user_id: int, summa: float):
        cur_balance = self.users.select('vivod_bal', {'id': user_id}, False)
        if float(cur_balance[0]) - summa >= 0:
            self.users.update({'vivod_bal': str(float(cur_balance[0]) - summa)}, {'id': user_id})
        else:
            self.users.update({'vivod_bal': '0.00'}, {'id': user_id})

    def give_investBalance(self, user_id: int, summa: float):
        cur_balance = self.users.select('invest_bal', {'id': user_id}, False)
        self.users.update({'invest_bal': str(float(cur_balance[0]) + summa)}, {'id': user_id})

    def take_investBalance(self, user_id: int, summa: float):
        cur_balance = self.users.select('invest_bal', {'id': user_id}, False)
        if float(cur_balance[0]) - summa >= 0:
            self.users.update({'invest_bal': str(float(cur_balance[0]) - summa)}, {'id': user_id})
        else:
            self.users.update({'invest_bal': '0.00'}, {'id': user_id})

    def take_inInvestBalance(self, user_id: int, summa: float):
        cur_balance = self.users.select('in_invest, vip', {'id': user_id}, False)
        if float(cur_balance[0]) - summa >= 0:
            match cur_balance[1]:
                case 0:
                    doxod = 0.02
                case 1:
                    doxod = 0.05
                case 2:
                    doxod = 0.1
            self.users.update(
                {'doxod': (float(cur_balance[0]) - summa) * doxod, 'in_invest': str(float(cur_balance[0]) - summa)},
                {'id': user_id})
        else:
            self.users.update({'in_invest': '0.00', 'doxod': '0.00'}, {'id': user_id})

    def change_vip(self, user_id: int, vip: int):
        self.users.update({'vip': vip}, {'id': user_id})
        user_invest = self.users.select('in_invest', {'id': user_id}, False)
        match vip:
            case 0:
                doxod = 0.02
                percent_doxod = 2
            case 1:
                doxod = 0.05
                percent_doxod = 5
            case 2:
                doxod = 0.1
                percent_doxod = 10
        self.users.update({'doxod': float(user_invest[0]) * doxod, 'percent_doxod': percent_doxod}, {'id': user_id})

    def new_karta(self, karta):
        self.bot.update({'karta': karta}, {'newid': 0})

    def new_btc(self, btc):
        self.bot.update({'btc': btc}, {'newid': 0})

    def new_eth(self, eth):
        self.bot.update({'eth': eth}, {'newid': 0})

    def new_ltc(self, ltc):
        self.bot.update({'ltc': ltc}, {'newid': 0})

    def new_ton(self, ton):
        self.bot.update({'ton': ton}, {'newid': 0})

    def new_atom(self, atom):
        self.bot.update({'atom': atom}, {'newid': 0})

    def new_sol(self, sol):
        self.bot.update({'sol': sol}, {'newid': 0})

    def accruing(self, user_id: int, doxod: float):
        user_info = self.users.select('vivod_bal, vip, in_invest, coins', {'id': user_id}, False)
        self.users.update({'vivod_bal': float(user_info[0]) + float(doxod)}, {'id': user_id})
        match user_info[1]:
            case 0:
                doxodCoins = 0.01
            case 1:
                doxodCoins = 0.025
            case 2:
                doxodCoins = 0.05
        self.users.update({'coins': round(float(user_info[3]) + ((float(user_info[2]) * doxodCoins) / 24), 2)},
                          {'id': user_id})

    def use_promo(self, user_id: int, name: str):
        promo = self.promocode.select('nagrada, activates, used', {'name': str(name)}, False)
        used = promo[2].split(' ')
        if str(user_id) in used:
            return False
        if int(promo[1]) != 0:
            balance = self.users.select('invest_bal', {'id': user_id}, False)
            self.users.update({'invest_bal': float(balance[0]) + float(promo[0])}, {'id': user_id})
            new_used = str(promo[2]) + f' {user_id}'
            self.promocode.update({'activates': int(promo[1]) - 1, 'used': new_used}, {'name': str(name)})
            return True
        return False

    def get_promo(self, user_id: int, name: str):
        promo = self.promocode.select('name, nagrada', {'name': str(name)}, False)
        return promo

    def get_allUsers(self):
        return self.users.select('id', 'id != 0', True)

    def newpromo(self, name: str, nagrada: float, activates: int):
        self.promocode.insert([name, nagrada, activates, ''])

    def update_refPrize(self, summa: float):
        return self.bot.update({'referalPrize': str(summa)}, {'newid': 0})

    def get_refPrize(self):
        return self.bot.select('referalPrize', {'newid': 0})

    def new_invest(self, user_id: int, summa: float):
        cur_invest = self.users.select('in_invest', {'id': user_id}, False)
        new_invest = float(cur_invest[0]) + summa
        self.users.update({'in_invest': new_invest}, {'id': user_id})
        vip = self.users.select('vip', {'id': user_id}, False)
        match int(vip[0]):
            case 0:
                percent = 0.02
            case 1:
                percent = 0.05
            case 2:
                percent = 0.10
        self.users.update({'doxod': new_invest * percent}, {'id': user_id})
        cur_balance = self.users.select('invest_bal', {'id': user_id}, False)
        self.users.update({'invest_bal': float(cur_balance[0]) - summa}, {'id': user_id})

    def is_register(self, user_id: int):
        user = self.users.select('id', {'id': user_id}, False)
        return user

    def get_investINFO(self, user_id: int):
        sql = self.users.select('percent_doxod, in_invest, vivod_bal, invest_bal', {'id': user_id}, False)
        data = list(sql)
        data[2] = round(float(data[2]), 2)
        return data

    def get_coins(self, user_id: int):
        return self.users.select('coins, vip, in_invest', {'id': user_id}, False)

    def get_balance(self, user_id: int):
        sql = self.users.select('invest_bal, vivod_bal', {'id': user_id}, False)
        balance = list(sql)
        balance[1] = round(float(balance[1]), 2)
        return balance

    def update_referal(self, user_id: int, ref: int):
        self.users.update({'referal': ref}, {'id': user_id})
        referals = self.users.select('referals', {'id': ref}, False)
        referals = int(referals[0]) + 1
        self.users.update({'referals': referals}, {'id': ref})
        balance = self.users.select('invest_bal', {'id': ref}, False)
        refPrize = self.bot.select('referalPrize', {'newid': 0}, False)
        balance = float(balance[0]) + float(refPrize[0])
        self.users.update({'invest_bal': str(balance)}, {'id': ref})
        coins = self.users.select('coins', {'id': ref}, False)
        coins = float(coins[0]) + 5.0
        return self.users.update({'coins': str(coins)}, {'id': ref})

    def get_topInvestors(self):
        investors = self.users.select('username, in_invest', "id != 0", True)
        sorted_investors = sorted(investors, key=lambda x: float(x[1]), reverse=True)
        if len(sorted_investors) > 10:
            return sorted_investors[:10]
        return sorted_investors

    def get_topCoins(self):
        peoples = self.users.select('username, coins', "id != 0", True)
        sorted_peoples = sorted(peoples, key=lambda x: float(x[1]), reverse=True)
        if len(sorted_peoples) > 10:
            return sorted_peoples[:10]
        return sorted_peoples

    def get_referals(self, user_id: int):
        info = self.users.select('referals, doxodbyREF', {'id': user_id}, False)
        return info

    def get_topReferals(self):
        referals = self.users.select('username, referals', "id != 0", True)
        sorted_referals = sorted(referals, key=lambda x: int(x[1]), reverse=True)
        if len(sorted_referals) > 10:
            return sorted_referals[:10]
        return sorted_referals

    def get_BotStats(self):
        users = len(self.users.select('*', 'id != 0', True))
        info = self.bot.select('popolnili, viveli', {'newid': 0}, False)
        return users, info[0], info[1]

    def get_doxod(self, user_id: int):
        vip = self.users.select('vip', {'id': user_id}, False)
        percent = self.users.select('percent_doxod', {'id': user_id}, False)
        doxod = None
        match vip[0]:
            case 0:
                doxod = 0.02
            case 1:
                doxod = 0.05
            case 2:
                doxod = 0.10

        return percent[0], doxod

    @staticmethod
    def set_referral(user_id, referral_id):
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""UPDATE users SET referal={referral_id} WHERE user_id={user_id}""")
        result = sql.fetchone()
        conn.commit()
        conn.close()
        return result

    def get_profile(self, user_id: int):
        return self.users.select('*', {'id': user_id}, False)

    @staticmethod
    def get_all_promo():
        conn = sqlite3.connect("data/users.db", check_same_thread=False)
        sql = conn.cursor()
        sql.execute(f"""SELECT name FROM promocodes""")
        result = sql.fetchall()
        conn.commit()
        conn.close()
        return result

    def close(self):
        self.db.close()
