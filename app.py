"""
🎮 O'yin Boti - 10 ta charchamay o'ynash uchun o'yin
Kutubxona: pyTelegramBotAPI (telebot)
O'rnatish: pip install pyTelegramBotAPI
Ishga tushirish: python games_bot.py
"""

import telebot
import random
import time
from telebot import types
from collections import defaultdict

# =============================================
# 🔑 TOKEN - O'z tokeningizni kiriting!
# BotFather dan oling: @BotFather -> /newbot
# =============================================
BOT_TOKEN = "8883773002:AAFghpw-SX5-Ph8nCRUYYLVbgbEgPYAMQm4"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =============================================
# 🗄️ O'yinchi ma'lumotlari (xotira ichida)
# =============================================
user_data = defaultdict(dict)

# =============================================
# 🎯 YORDAMCHI FUNKSIYALAR
# =============================================

def main_menu():
    """Asosiy o'yin menyusi"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("🔢 Raqam toping",        callback_data="game_guess"),
        types.InlineKeyboardButton("✂️ Tosh-qaychi-qog'oz", callback_data="game_rps"),
        types.InlineKeyboardButton("🎲 Zar tashlash",         callback_data="game_dice"),
        types.InlineKeyboardButton("🧮 Matematik duel",       callback_data="game_math"),
        types.InlineKeyboardButton("🪙 Tanga tashlash",       callback_data="game_coin"),
        types.InlineKeyboardButton("🔤 So'z toping",          callback_data="game_word"),
        types.InlineKeyboardButton("🎯 Lotereya",             callback_data="game_lottery"),
        types.InlineKeyboardButton("🐍 Raqam zanjiri",        callback_data="game_chain"),
        types.InlineKeyboardButton("🃏 Karta o'yini",         callback_data="game_card"),
        types.InlineKeyboardButton("🧠 Topishmoq",            callback_data="game_riddle"),
    ]
    markup.add(*buttons)
    return markup

def back_btn():
    """Faqat qaytish tugmasi"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Menyuga qaytish", callback_data="menu"))
    return markup

def back_and_retry(retry_callback):
    """Qaytish + Yana o'ynash tugmasi"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔄 Yana",               callback_data=retry_callback),
        types.InlineKeyboardButton("🔙 Menyuga qaytish",    callback_data="menu"),
    )
    return markup

def send_with_back(bot, cid, mid, text, retry_cb=None):
    """Xabar + qaytish tugmasini birgalikda yuborish"""
    markup = back_and_retry(retry_cb) if retry_cb else back_btn()
    bot.edit_message_text(text, cid, mid, reply_markup=markup)

def reply_with_back(bot, cid, text, retry_cb=None):
    """send_message orqali qaytish tugmali javob"""
    markup = back_and_retry(retry_cb) if retry_cb else back_btn()
    bot.send_message(cid, text, reply_markup=markup)

def cancel_mode(uid):
    """O'yinchi rejimini o'chirish"""
    user_data[uid]["mode"] = ""

# =============================================
# /start va /menu komandalar
# =============================================
@bot.message_handler(commands=["start", "menu"])
def start(message):
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Salom, <b>{name}</b>!\n\n"
        "🎮 <b>10 ta qiziqarli o'yin</b> tayyor!\n"
        "Charchaganda o'ynash uchun pastdan o'yinni tanlang 👇",
        reply_markup=main_menu()
    )

# =============================================
# CALLBACK HANDLER
# =============================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data

    # ==========================================
    # 🏠 ASOSIY MENYU
    # ==========================================
    if data == "menu":
        cancel_mode(uid)
        bot.edit_message_text(
            "🎮 <b>O'yinlar menyusi</b>\n\nO'yin tanlang 👇",
            cid, mid, reply_markup=main_menu()
        )

    # ==========================================
    # 1️⃣  RAQAM TOPISH
    # ==========================================
    elif data == "game_guess":
        number = random.randint(1, 100)
        user_data[uid].update({
            "guess_number": number,
            "guess_tries": 0,
            "mode": "guess",
        })
        bot.edit_message_text(
            "🔢 <b>Raqam topish o'yini!</b>\n\n"
            "Men 1 dan 100 gacha raqam o'yladim.\n"
            "Siz nechta urinishda topasiz?\n\n"
            "✍️ Raqamni yozing yoki:\n",
            cid, mid,
            reply_markup=back_btn()          # ← qaytish tugmasi har doim ko'rinadi
        )

    # ==========================================
    # 2️⃣  TOSH-QAYCHI-QOG'OZ
    # ==========================================
    elif data == "game_rps":
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("🪨 Tosh",    callback_data="rps_rock"),
            types.InlineKeyboardButton("✂️ Qaychi",  callback_data="rps_scissors"),
            types.InlineKeyboardButton("📄 Qog'oz",  callback_data="rps_paper"),
        )
        markup.add(types.InlineKeyboardButton("🔙 Menyuga qaytish", callback_data="menu"))
        bot.edit_message_text(
            "✂️ <b>Tosh-Qaychi-Qog'oz!</b>\n\nTanlov qiling:",
            cid, mid, reply_markup=markup
        )

    elif data in ["rps_rock", "rps_scissors", "rps_paper"]:
        choices = {"rps_rock": "🪨 Tosh", "rps_scissors": "✂️ Qaychi", "rps_paper": "📄 Qog'oz"}
        wins   = {"rps_rock": "rps_scissors", "rps_scissors": "rps_paper", "rps_paper": "rps_rock"}
        bot_choice  = random.choice(list(choices.keys()))
        user_choice = data
        sc = user_data[uid].setdefault("rps_score", {"win": 0, "lose": 0, "draw": 0})

        if user_choice == bot_choice:
            result = "🤝 Durrang!"
            sc["draw"] += 1
        elif wins[user_choice] == bot_choice:
            result = "🎉 Siz yutdingiz!"
            sc["win"] += 1
        else:
            result = "😔 Bot yutdi!"
            sc["lose"] += 1

        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("🪨",         callback_data="rps_rock"),
            types.InlineKeyboardButton("✂️",         callback_data="rps_scissors"),
            types.InlineKeyboardButton("📄",         callback_data="rps_paper"),
        )
        markup.add(types.InlineKeyboardButton("🔙 Menyuga qaytish", callback_data="menu"))
        bot.edit_message_text(
            f"Siz: <b>{choices[user_choice]}</b>\n"
            f"Bot: <b>{choices[bot_choice]}</b>\n\n"
            f"<b>{result}</b>\n\n"
            f"📊 ✅{sc['win']} ❌{sc['lose']} 🤝{sc['draw']}\n\n"
            "Yana o'ynash uchun tanlang:",
            cid, mid, reply_markup=markup
        )

    # ==========================================
    # 3️⃣  ZAR TASHLASH
    # ==========================================
    elif data == "game_dice":
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("1️⃣", callback_data="dice_1"),
            types.InlineKeyboardButton("2️⃣", callback_data="dice_2"),
            types.InlineKeyboardButton("3️⃣", callback_data="dice_3"),
            types.InlineKeyboardButton("4️⃣", callback_data="dice_4"),
            types.InlineKeyboardButton("5️⃣", callback_data="dice_5"),
            types.InlineKeyboardButton("6️⃣", callback_data="dice_6"),
        )
        markup.add(types.InlineKeyboardButton("🔙 Menyuga qaytish", callback_data="menu"))
        bot.edit_message_text(
            "🎲 <b>Zar o'yini!</b>\n\n"
            "Zar qaysi raqamga tushishini taxmin qiling.\n"
            "✅ To'g'ri = +10 ball  |  ❌ Noto'g'ri = -3 ball\n\n"
            f"Balingiz: <b>{user_data[uid].get('dice_score', 0)}</b>\n\n"
            "Raqamni tanlang:",
            cid, mid, reply_markup=markup
        )

    elif data.startswith("dice_"):
        guess      = int(data.split("_")[1])
        result_num = random.randint(1, 6)
        faces      = ["⚀","⚁","⚂","⚃","⚄","⚅"]
        user_data[uid].setdefault("dice_score", 0)

        if guess == result_num:
            user_data[uid]["dice_score"] += 10
            msg = f"🎉 To'g'ri! {faces[result_num-1]} = {result_num}\n+10 ball!"
        else:
            user_data[uid]["dice_score"] -= 3
            msg = f"❌ Noto'g'ri! {faces[result_num-1]} = {result_num}\n-3 ball"

        bot.edit_message_text(
            f"{msg}\n\n📊 Umumiy ball: <b>{user_data[uid]['dice_score']}</b>",
            cid, mid,
            reply_markup=back_and_retry("game_dice")
        )

    # ==========================================
    # 4️⃣  MATEMATIK DUEL
    # ==========================================
    elif data == "game_math":
        op = random.choice(["+", "-", "*"])
        if op == "+":
            a, b = random.randint(1, 50), random.randint(1, 50); ans = a + b
        elif op == "-":
            a, b = random.randint(10, 99), random.randint(1, 10); ans = a - b
        else:
            a, b = random.randint(2, 12), random.randint(2, 12); ans = a * b

        user_data[uid].update({
            "math_answer": ans,
            "math_time":   time.time(),
            "mode":        "math",
        })
        user_data[uid].setdefault("math_score", 0)

        bot.edit_message_text(
            "🧮 <b>Matematik duel!</b>\n\n"
            f"Hisoblab bering:\n\n"
            f"<code>{a} {op} {b} = ?</code>\n\n"
            f"Ball: <b>{user_data[uid]['math_score']}</b>\n\n"
            "✍️ Javobni yozing yoki:",
            cid, mid,
            reply_markup=back_btn()          # ← qaytish tugmasi
        )

    # ==========================================
    # 5️⃣  TANGA TASHLASH
    # ==========================================
    elif data == "game_coin":
        sc = user_data[uid].setdefault("coin_score", {"win": 0, "lose": 0})
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🪙 Yuz", callback_data="coin_heads"),
            types.InlineKeyboardButton("🪙 Dum", callback_data="coin_tails"),
        )
        markup.add(types.InlineKeyboardButton("🔙 Menyuga qaytish", callback_data="menu"))
        bot.edit_message_text(
            "🪙 <b>Tanga o'yini!</b>\n\n"
            "Tanga qaysi tomonga tushishini taxmin qiling!\n\n"
            f"✅ {sc['win']} | ❌ {sc['lose']}\n\n"
            "Tanlov qiling:",
            cid, mid, reply_markup=markup
        )

    elif data in ["coin_heads", "coin_tails"]:
        result = random.choice(["coin_heads", "coin_tails"])
        names  = {"coin_heads": "🪙 Yuz", "coin_tails": "🪙 Dum"}
        sc     = user_data[uid].setdefault("coin_score", {"win": 0, "lose": 0})

        if data == result:
            sc["win"] += 1;  msg = f"🎉 To'g'ri! {names[result]}"
        else:
            sc["lose"] += 1; msg = f"❌ Noto'g'ri! {names[result]}"

        bot.edit_message_text(
            f"{msg}\n\n✅ {sc['win']} | ❌ {sc['lose']}",
            cid, mid,
            reply_markup=back_and_retry("game_coin")
        )

    # ==========================================
    # 6️⃣  SO'Z TOPING
    # ==========================================
    elif data == "game_word":
        words = [
            ("PYTHON",     "Mashxur dasturlash tili 🐍"),
            ("TELEGRAM",   "Bu bot shu orqali ishlaydi 📱"),
            ("KOMPYUTER",  "Elektronik hisoblash qurilmasi 💻"),
            ("DASTURCHI",  "Kod yozadigan mutaxassis 👨‍💻"),
            ("INTERNET",   "Global tarmoq 🌐"),
            ("ROBOT",      "Avtomatik mexanizm 🤖"),
            ("KLAVIATURA", "Yozish uchun qurilma ⌨️"),
            ("EKRAN",      "Ko'rsatish qurilmasi 🖥️"),
            ("FAYL",       "Ma'lumot saqlash birligi 📁"),
            ("DASTUR",     "Kompyuter uchun yozilgan kod 💾"),
        ]
        word, hint = random.choice(words)
        shuffled   = list(word); random.shuffle(shuffled)
        user_data[uid].update({"word_answer": word, "mode": "word"})

        bot.edit_message_text(
            "🔤 <b>So'z toping!</b>\n\n"
            f"Aralashtirilgan harflar:\n"
            f"<code>{'  '.join(shuffled)}</code>\n\n"
            f"💡 Izoh: {hint}\n\n"
            "✍️ So'zni yozing yoki:",
            cid, mid,
            reply_markup=back_btn()          # ← qaytish tugmasi
        )

    # ==========================================
    # 7️⃣  LOTEREYA
    # ==========================================
    elif data == "game_lottery":
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(*[types.InlineKeyboardButton(str(i), callback_data=f"lotto_{i}") for i in range(1, 10)])
        markup.add(types.InlineKeyboardButton("🔙 Menyuga qaytish", callback_data="menu"))
        bot.edit_message_text(
            "🎯 <b>Lotereya!</b>\n\n"
            "1 dan 9 gacha raqam tanlang.\n"
            "To'g'ri chiqsa — JACKPOT! 🎰\n\n"
            "Baxt kulib boqsinmi? Tanlov qiling:",
            cid, mid, reply_markup=markup
        )

    elif data.startswith("lotto_"):
        guess      = int(data.split("_")[1])
        result_num = random.randint(1, 9)

        if guess == result_num:
            msg = f"🎰 JACKPOT! 🎉\nSiz {result_num} ni topdingiz!\n\n🤑 BAXTLI KUN!"
        elif abs(guess - result_num) == 1:
            msg = f"😅 Deyarli! Raqam {result_num} edi.\nSiz {guess} ni tanladingiz — 1 ta farq!"
        else:
            msg = f"❌ Omad kelmadi!\nRaqam: {result_num}\nSiz: {guess}"

        bot.edit_message_text(msg, cid, mid, reply_markup=back_and_retry("game_lottery"))

    # ==========================================
    # 8️⃣  RAQAM ZANJIRI
    # ==========================================
    elif data == "game_chain":
        start_num = random.randint(1, 20)
        rule      = random.choice(["juft", "toq", "3ga_karrali"])
        user_data[uid].update({
            "chain_num":  start_num,
            "chain_step": rule,
            "mode":       "chain",
        })
        rule_names = {
            "juft":        "juft raqamlar (2, 4, 6…)",
            "toq":         "toq raqamlar (1, 3, 5…)",
            "3ga_karrali": "3 ga karrali raqamlar (3, 6, 9…)"
        }
        bot.edit_message_text(
            "🐍 <b>Raqam zanjiri!</b>\n\n"
            f"Qoida: <b>{rule_names[rule]}</b>\n"
            f"Boshlang'ich raqam: <b>{start_num}</b>\n\n"
            "✍️ Keyingi raqamni yozing yoki:",
            cid, mid,
            reply_markup=back_btn()          # ← qaytish tugmasi
        )

    # ==========================================
    # 9️⃣  KARTA O'YINI
    # ==========================================
    elif data == "game_card":
        suits  = ["♠️","♥️","♦️","♣️"]
        values = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        card_v = {"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,
                  "10":10,"J":10,"Q":10,"K":10,"A":11}

        pc, bc  = random.choice(values), random.choice(values)
        pv, bv  = card_v[pc], card_v[bc]
        s1, s2  = random.choice(suits), random.choice(suits)
        sc      = user_data[uid].setdefault("card_score", {"win":0,"lose":0,"draw":0})

        if pv > bv:   sc["win"]  += 1; result = "🎉 Siz yutdingiz!"
        elif pv < bv: sc["lose"] += 1; result = "😔 Bot yutdi!"
        else:         sc["draw"] += 1; result = "🤝 Durrang!"

        bot.edit_message_text(
            "🃏 <b>Karta o'yini!</b>\n\n"
            f"Siz: <b>{s1}{pc}</b> ({pv})\n"
            f"Bot: <b>{s2}{bc}</b> ({bv})\n\n"
            f"<b>{result}</b>\n\n"
            f"📊 ✅{sc['win']} ❌{sc['lose']} 🤝{sc['draw']}",
            cid, mid,
            reply_markup=back_and_retry("game_card")
        )

    # ==========================================
    # 🔟  TOPISHMOQ
    # ==========================================
    elif data == "game_riddle":
        riddles = [
            ("Qancha ko'p olsang, shuncha ko'p qoladi. Bu nima?",                      "teshik"),
            ("Tili bor, lekin gapirmaydi. Bu nima?",                                   "kitob"),
            ("Oyoqlari bor, lekin yura olmaydi. Bu nima?",                             "stol"),
            ("Ko'zlari bor, lekin ko'rmaydi. Bu nima?",                                "igna"),
            ("Qancha qorasang, shuncha oppoq bo'ladi. Bu nima?",                       "doska"),
            ("Yoz kiyinadi, qish yechinadi. Bu nima?",                                 "daraxt"),
            ("Ichida suv bor, lekin dengiz emas. Bu nima?",                            "tarvuz"),
            ("Kunduz uxlaydi, kechasi uyg'onadi. Bu nima?",                            "yulduz"),
            ("Qanotlari bor, lekin qush emas; uchadi, lekin samolyot emas. Bu nima?",  "kapalak"),
            ("Har kuni o'ladi, har kuni tug'iladi. Bu nima?",                          "kun"),
        ]
        riddle, answer = random.choice(riddles)
        user_data[uid].update({"riddle_answer": answer, "mode": "riddle"})
        user_data[uid].setdefault("riddle_score", 0)

        bot.edit_message_text(
            "🧠 <b>Topishmoq!</b>\n\n"
            f"❓ {riddle}\n\n"
            f"Ball: <b>{user_data[uid]['riddle_score']}</b>\n\n"
            "✍️ Javobni yozing yoki:",
            cid, mid,
            reply_markup=back_btn()          # ← qaytish tugmasi
        )

    bot.answer_callback_query(call.id)


# =============================================
# MATN XABAR HANDLER (o'yin javoblari)
# =============================================
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid  = message.from_user.id
    cid  = message.chat.id
    text = message.text.strip()
    mode = user_data[uid].get("mode", "")

    # ------------------------------------------
    # 1️⃣  RAQAM TOPISH
    # ------------------------------------------
    if mode == "guess":
        try:
            guess  = int(text)
            secret = user_data[uid]["guess_number"]
            user_data[uid]["guess_tries"] += 1
            tries  = user_data[uid]["guess_tries"]

            if guess < secret:
                bot.send_message(cid,
                    f"📈 Kattaroq! ({tries}-urinish)",
                    reply_markup=back_btn())
            elif guess > secret:
                bot.send_message(cid,
                    f"📉 Kichikroq! ({tries}-urinish)",
                    reply_markup=back_btn())
            else:
                cancel_mode(uid)
                stars = "⭐" * max(1, 6 - tries)
                bot.send_message(cid,
                    f"🎉 <b>Barakalla!</b> {secret} raqamini "
                    f"{tries} ta urinishda topdingiz!\n{stars}",
                    reply_markup=back_and_retry("game_guess"))
        except ValueError:
            bot.send_message(cid, "❗ Faqat raqam kiriting!",
                             reply_markup=back_btn())

    # ------------------------------------------
    # 4️⃣  MATEMATIK DUEL
    # ------------------------------------------
    elif mode == "math":
        try:
            answer  = int(text)
            correct = user_data[uid]["math_answer"]
            elapsed = round(time.time() - user_data[uid].get("math_time", time.time()), 1)
            user_data[uid].setdefault("math_score", 0)
            cancel_mode(uid)

            if answer == correct:
                points = max(1, 10 - int(elapsed // 3))
                user_data[uid]["math_score"] += points
                bot.send_message(cid,
                    f"✅ To'g'ri! {elapsed}s da topdingiz!\n"
                    f"+{points} ball  |  Jami: <b>{user_data[uid]['math_score']}</b>",
                    reply_markup=back_and_retry("game_math"))
            else:
                user_data[uid]["math_score"] -= 2
                bot.send_message(cid,
                    f"❌ Noto'g'ri! To'g'ri javob: <b>{correct}</b>\n"
                    f"-2 ball  |  Jami: <b>{user_data[uid]['math_score']}</b>",
                    reply_markup=back_and_retry("game_math"))
        except ValueError:
            bot.send_message(cid, "❗ Faqat son kiriting!",
                             reply_markup=back_btn())

    # ------------------------------------------
    # 6️⃣  SO'Z TOPISH
    # ------------------------------------------
    elif mode == "word":
        correct = user_data[uid].get("word_answer", "")
        cancel_mode(uid)
        if text.upper() == correct:
            bot.send_message(cid,
                f"🎉 To'g'ri! So'z: <b>{correct}</b>",
                reply_markup=back_and_retry("game_word"))
        else:
            bot.send_message(cid,
                f"❌ Noto'g'ri! To'g'ri so'z: <b>{correct}</b>",
                reply_markup=back_and_retry("game_word"))

    # ------------------------------------------
    # 8️⃣  RAQAM ZANJIRI
    # ------------------------------------------
    elif mode == "chain":
        try:
            num  = int(text)
            prev = user_data[uid]["chain_num"]
            rule = user_data[uid]["chain_step"]

            def ok(n, r):
                if r == "juft":        return n % 2 == 0
                if r == "toq":         return n % 2 == 1
                if r == "3ga_karrali": return n % 3 == 0

            if ok(num, rule) and num > prev:
                user_data[uid]["chain_num"] = num
                rnames = {"juft":"juft", "toq":"toq", "3ga_karrali":"3 ga karrali"}
                bot.send_message(cid,
                    f"✅ To'g'ri! {num} — {rnames[rule]} raqam.\n\n"
                    "✍️ Keyingisini yozing yoki:",
                    reply_markup=back_btn())
            else:
                cancel_mode(uid)
                bot.send_message(cid,
                    f"❌ Xato! {num} qoidaga mos emas yoki kichik.\n"
                    "Zanjir uzildi!",
                    reply_markup=back_and_retry("game_chain"))
        except ValueError:
            bot.send_message(cid, "❗ Faqat raqam kiriting!",
                             reply_markup=back_btn())

    # ------------------------------------------
    # 🔟  TOPISHMOQ
    # ------------------------------------------
    elif mode == "riddle":
        correct = user_data[uid].get("riddle_answer", "")
        user_data[uid].setdefault("riddle_score", 0)
        cancel_mode(uid)

        if text.lower() == correct.lower():
            user_data[uid]["riddle_score"] += 5
            bot.send_message(cid,
                f"🎉 To'g'ri! Javob: <b>{correct}</b>\n"
                f"+5 ball  |  Jami: <b>{user_data[uid]['riddle_score']}</b>",
                reply_markup=back_and_retry("game_riddle"))
        else:
            user_data[uid]["riddle_score"] -= 1
            bot.send_message(cid,
                f"❌ Noto'g'ri! To'g'ri javob: <b>{correct}</b>\n"
                f"-1 ball  |  Jami: <b>{user_data[uid]['riddle_score']}</b>",
                reply_markup=back_and_retry("game_riddle"))

    # ------------------------------------------
    # O'yin rejimi yo'q — menyuga yo'naltir
    # ------------------------------------------
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎮 O'yinlar menyusi", callback_data="menu"))
        bot.send_message(cid,
            "O'yin tanlang 👇",
            reply_markup=markup)
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda!"

def run_flask():
    # Render avtomatik ravishda PORT muhit o'zgaruvchisini beradi
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
    
# =============================================
# BOTNI ISHGA TUSHIRISH
# =============================================
if __name__ == "__main__":
    print("🎮 O'yin boti ishga tushdi!")
    print("To'xtatish uchun: Ctrl+C")
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)