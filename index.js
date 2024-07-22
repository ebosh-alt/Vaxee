const sqlite = require('sqlite-sync');
const express = require("express");
const app = express();

app.use(express.json());

const port = 1088;

app.post('/qopgjkqgmksewjhr/', async (req, res) => {
    res.json({status: "ok"});
    let req_body = req.body;
    if (req_body.type === 'new_donate') {
        let user_id = req_body.data.user;
        let amount = req_body.data.amount;
        if (req_body.data.hasOwnProperty('msg')) {
            let msg = req_body.data.msg;
            if (msg.toLowerCase() === 'vip') {
                if (amount == 3000) {
                    sqlite.connect('./users.db');
                    sqlite.run(`UPDATE users SET vip = 1 WHERE id = ${user_id}`)
                    sqlite.run(`UPDATE users SET percent_doxod = 5 WHERE id = ${user_id}`)
                    let user_invest = sqlite.run(`SELECT in_invest FROM users WHERE id = ${user_id}`)
                    user_invest = user_invest[0].in_invest
                    sqlite.run(`UPDATE users SET doxod = '${Number(user_invest) * 0.05}' WHERE id = ${user_id}`)
                    sqlite.close();
                } else {
                    sqlite.connect('./users.db')
                    let cur_balance = sqlite.run(`SELECT invest_bal FROM users WHERE id = ${user_id}`)
                    cur_balance = Number(cur_balance[0].invest_bal)
                    sqlite.run(`UPDATE users SET invest_bal = '${cur_balance + Number(amount)}' WHERE id = ${user_id}`)
                    let cur_popolnili = sqlite.run(`SELECT popolnili FROM bot_settings WHERE newid = 0;`)
                    cur_popolnili = Number(cur_popolnili[0].popolnili)
                    sqlite.run(`UPDATE bot_settings SET popolnili = '${cur_popolnili + amount}'`)
                    let ref = sqlite.run(`SELECT referal FROM users WHERE id = ${user_id}`)
                    ref = ref[0].referal
                    if (ref != 0) {
                        cur_balanceRef = sqlite.run(`SELECT invest_bal FROM users WHERE id = ${ref}`)
                        cur_balanceRef = Number(cur_balanceRef[0].invest_bal)
                        sqlite.run(`UPDATE users SET invest_bal = '${cur_balance + Number(amount) * 0.05}' WHERE id = ${ref}`)
                    }
                    sqlite.close();
                }
            } else if (msg.toLowerCase() === 'premium') {
                if (amount == 8000) {
                    sqlite.connect('./users.db');
                    sqlite.run(`UPDATE users SET vip = 2 WHERE id = ${user_id}`)
                    sqlite.run(`UPDATE users SET percent_doxod = 10 WHERE id = ${user_id}`)
                    let user_invest = sqlite.run(`SELECT in_invest FROM users WHERE id = ${user_id}`)
                    user_invest = user_invest[0].in_invest
                    sqlite.run(`UPDATE users SET doxod = '${Number(user_invest) * 0.1}' WHERE id = ${user_id}`)
                    sqlite.close();
                } else {
                    sqlite.connect('./users.db')
                    sqlite.connect('./users.db')
                    let cur_balance = sqlite.run(`SELECT invest_bal FROM users WHERE id = ${user_id}`)
                    cur_balance = Number(cur_balance[0].invest_bal)
                    sqlite.run(`UPDATE users SET invest_bal = '${cur_balance + Number(amount)}' WHERE id = ${user_id}`)
                    let cur_popolnili = sqlite.run(`SELECT popolnili FROM bot_settings WHERE newid = 0;`)
                    cur_popolnili = Number(cur_popolnili[0].popolnili)
                    sqlite.run(`UPDATE bot_settings SET popolnili = '${cur_popolnili + amount}'`)
                    let ref = sqlite.run(`SELECT referal FROM users WHERE id = ${user_id}`)
                    ref = ref[0].referal
                    if (ref != 0) {
                        cur_balanceRef = sqlite.run(`SELECT invest_bal FROM users WHERE id = ${ref}`)
                        cur_balanceRef = Number(cur_balanceRef[0].invest_bal)
                        sqlite.run(`UPDATE users SET invest_bal = '${cur_balance + Number(amount) * 0.05}' WHERE id = ${ref}`)
                    }
                    sqlite.close();
                }
            }
        } else {
            sqlite.connect('./users.db')
            let cur_balance = sqlite.run(`SELECT invest_bal FROM users WHERE id = ${user_id}`)
            cur_balance = Number(cur_balance[0].invest_bal)
            sqlite.run(`UPDATE users SET invest_bal = '${cur_balance + Number(amount)}' WHERE id = ${user_id}`)
            let cur_popolnili = sqlite.run(`SELECT popolnili FROM bot_settings WHERE newid = 0;`)
            cur_popolnili = Number(cur_popolnili[0].popolnili)
            sqlite.run(`UPDATE bot_settings SET popolnili = '${cur_popolnili + amount}'`)
            let ref = sqlite.run(`SELECT referal FROM users WHERE id = ${user_id}`)
            ref = ref[0].referal
            if (ref != 0) {
                cur_balanceRef = sqlite.run(`SELECT invest_bal FROM users WHERE id = ${ref}`)
                cur_balanceRef = Number(cur_balanceRef[0].invest_bal)
                sqlite.run(`UPDATE users SET invest_bal = '${cur_balance + Number(amount) * 0.05}' WHERE id = ${ref}`)
            }
            sqlite.close();
        }
    }
    else if (req_body.type === 'payout') {
        let status = req_body.data.status;
        if (status === 'canceled') {
            let system = req_body.data.system;
            let purse = req_body.data.purse;
            let amount = req_body.data.amount
            if (system === 'card-rub') {
                sqlite.connect('./users.db');
                let user_id = sqlite.run(`SELECT id FROM users WHERE rekvizitiCARD = '${purse}'`)
                user_id = user_id[0].id
                let cur_balance = sqlite.run(`SELECT vivod_bal FROM users WHERE id = ${user_id}`)
                cur_balance = Number(cur_balance[0].vivod_bal)
                sqlite.run(`UPDATE users SET vivod_bal = '${cur_balance + Number(amount)}' WHERE id = ${user_id}`)
                sqlite.close()
            }
            else if (system === 'sbp') {
                sqlite.connect('./users.db');
                let user_id = sqlite.run(`SELECT id FROM users WHERE rekvizitiSBP = '${purse}'`)
                user_id = user_id[0].id
                let cur_balance = sqlite.run(`SELECT vivod_bal FROM users WHERE id = ${user_id}`)
                cur_balance = Number(cur_balance[0].vivod_bal)
                sqlite.run(`UPDATE users SET vivod_bal = '${cur_balance + Number(amount)}' WHERE id = ${user_id}`)
                sqlite.close();
            }
            else if (system === 'yoomoney') {
                sqlite.connect('./users.db');
                let user_id = sqlite.run(`SELECT id FROM users WHERE rekvizitiYOOMONEY = '${purse}'`)
                user_id = user_id[0].id
                let cur_balance = sqlite.run(`SELECT vivod_bal FROM users WHERE id = ${user_id}`)
                cur_balance = Number(cur_balance[0].vivod_bal)
                sqlite.run(`UPDATE users SET vivod_bal = '${cur_balance + Number(amount)}' WHERE id = ${user_id}`)
                sqlite.close();
            }
        }
    }
})

app.listen(port, () => {
    console.log(`KeksikCallback listening on PORT ${port}`)
})

