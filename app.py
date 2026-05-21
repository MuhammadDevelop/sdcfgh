import os
import telebot
from telebot import types
from threading import Thread
from flask import Flask

# 1. FLASK VEB-SERVER QISMI (Render 24/7 o'chib qolmasligi uchun kerak)
app = Flask('')

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda! 24/7 faol."

def run_flask():
    # Render avtomatik PORT beradi, agar bo'lmasa 8080 portda ishlaydi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


# 2. TELEGRAM BOT QISMI
# Bot tokeningizni shu yerga yozing
BOT_TOKEN = "8883773002:AAFghpw-SX5-Ph8nCRUYYLVbgbEgPYAMQm4"
bot = telebot.TeleBot(BOT_TOKEN)

# Imtihon savollari bazasi
QUESTIONS = [
    {
        "question": "1. Python-da ro'yxatga (list) element qo'shish uchun qaysi metoddan foydalaniladi?",
        "options": ["add()", "append()", "push()", "insert_into()"],
        "correct": "append()"
    },
    {
        "question": "2. HTML-da eng katta sarlavha (heading) qaysi teg orqali yoziladi?",
        "options": ["<h6>", "<head>", "<heading>", "<h1>"],
        "correct": "<h1>"
    },
    {
        "question": "3. CSS nima so'zining qisqartmasi?",
        "options": ["Cascading Style Sheets", "Creative Style Slots", "Computer Style Sheets", "Colorful Style Sheets"],
        "correct": "Cascading Style Sheets"
    },
    {
        "question": "4. O'zbekiston Respublikasi mustaqilligi qaysi yili e'lon qilingan?",
        "options": ["1990", "1991", "1992", "1993"],
        "correct": "1991"
    }
]

# Foydalanuvchilarning sessiyalarini xotirada saqlash
user_sessions = {}

# Inline (shisha) tugmalarni yaratish funksiyasi
def get_quiz_keyboard(options, question_index):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        # Callback format: quiz_savol-indeksi_tanlangan-variant
        callback_data = f"quiz_{question_index}_{option}"
        button = types.InlineKeyboardButton(text=option, callback_data=callback_data)
        keyboard.add(button)
    return keyboard

# /start buyrug'i kelganda
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    
    # Eski sessiya bo'lsa o'chirib tashlaymiz
    if user_id in user_sessions:
        del user_sessions[user_id]
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("🚀 Imtihonni boshlash"))
    
    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        f"Imtihon botiga xush kelibsiz. Bilamingizni sinab ko'rishga tayyormisiz?",
        reply_markup=markup
    )

# "🚀 Imtihonni boshlash" tugmasi bosilganda
@bot.message_handler(func=lambda message: message.text == "🚀 Imtihonni boshlash")
def start_quiz(message):
    user_id = message.from_user.id
    
    # Yangi imtihon sessiyasini boshlash
    user_sessions[user_id] = {
        "current_q": 0,
        "correct_ans": 0
    }
    
    first_q = QUESTIONS[0]
    
    bot.send_message(
        message.chat.id,
        text=first_q["question"],
        reply_markup=get_quiz_keyboard(first_q["options"], 0)
    )

# Variantlardan biri tanlanganda (Inline tugma bosilganda)
@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz_"))
def process_quiz_answer(call):
    user_id = call.from_user.id
    
    # Xavfsizlik: Foydalanuvchi sessiyasi mavjudligini tekshirish
    if user_id not in user_sessions:
        bot.answer_callback_query(call.id, "Iltimos, imtihonni qaytadan boshlang!", show_alert=True)
        return

    # Callback_data dan ma'lumotlarni ajratib olish
    data_parts = call.data.split("_")
    q_index = int(data_parts[1])
    selected_option = data_parts[2]
    
    session = user_sessions[user_id]
    
    # Anti-cheat: Eskirgan savol tugmasini qayta bosishdan himoya
    if q_index != session["current_q"]:
        bot.answer_callback_query(call.id, "Bu savolga allaqachon javob bergansiz!", show_alert=True)
        return

    # Javobni tekshirish
    current_q_data = QUESTIONS[q_index]
    if selected_option == current_q_data["correct"]:
        session["correct_ans"] += 1
        bot.answer_callback_query(call.id, "To'g'ri! ✅")
    else:
        bot.answer_callback_query(call.id, f"Noto'g'ri! ❌\nTo'g'ri javob: {current_q_data['correct']}", show_alert=True)

    next_q_index = q_index + 1
    session["current_q"] = next_q_index

    # Keyingi savolni chiqarish yoki imtihonni yakunlash
    if next_q_index < len(QUESTIONS):
        next_q_data = QUESTIONS[next_q_index]
        # Chat toza turishi uchun xabarni o'zgartiramiz
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=next_q_data["question"],
            reply_markup=get_quiz_keyboard(next_q_data["options"], next_q_index)
        )
    else:
        # Natijalarni hisoblash
        total_q = len(QUESTIONS)
        correct = session["correct_ans"]
        percent = (correct / total_q) * 100
        
        result_text = (
            f"🎉 **Imtihon yakunlandi!**\n\n"
            f"📊 **Natijangiz:**\n"
            f"✅ To'g'ri javoblar: {correct} ta\n"
            f"❌ Noto'g'ri javoblar: {total_q - correct} ta\n"
            f"📈 Umumiy samaradorlik: **{percent:.1f}%**\n\n"
        )
        
        if percent >= 80:
            result_text += "🔥 Dahshat! Imtihondan a'lo baho bilan o'tdingiz! 👏"
        elif percent >= 50:
            result_text += "👍 Yaxshi, imtihondan o'tdingiz. Yanada yaxshiroq tayyorlanishingiz mumkin."
        else:
            result_text += "⚠️ Afsuski, imtihondan o'ta olmadingiz. Yana urinib ko'ring."

        # Qayta boshlash tugmasi
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("🚀 Imtihonni boshlash"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=result_text,
            parse_mode="Markdown"
        )
        
        bot.send_message(call.message.chat.id, "Qayta urinish uchun pastdagi tugmani bosing:", reply_markup=markup)
        
        # Foydalanuvchi sessiyasini xotiradan tozalaymiz
        del user_sessions[user_id]


# 3. LOYIHANI ISHGA TUSHIRISH MANTIQI
if __name__ == "__main__":
    print("Bot va veb-server ishga tushmoqda...")
    
    # Flask veb-serverini alohida parallel oqimda (Thread) boshlaymiz
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Telegram botni cheksiz so'rovlar rejimida ishga tushiramiz
    bot.infinity_polling()