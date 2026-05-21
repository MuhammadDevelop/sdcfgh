import os
import telebot
from telebot import types
from threading import Thread
from flask import Flask

# 1. FLASK VEB-SERVER QISMI
app = Flask('')

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda! 24/7 faol."

# 2. TELEGRAM BOT QISMI
# Tokenni birinchi bo'lib Render muhitidan (Environment) qidiradi, topilmasa pastdagini oladi
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8883773002:AAFghpw-SX5-Ph8nCRUYYLVbgbEgPYAMQm4")
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

user_sessions = {}

def get_quiz_keyboard(options, question_index):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        callback_data = f"quiz_{question_index}_{option}"
        button = types.InlineKeyboardButton(text=option, callback_data=callback_data)
        keyboard.add(button)
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
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

@bot.message_handler(func=lambda message: message.text == "🚀 Imtihonni boshlash")
def start_quiz(message):
    user_id = message.from_user.id
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

@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz_"))
def process_quiz_answer(call):
    user_id = call.from_user.id
    if user_id not in user_sessions:
        bot.answer_callback_query(call.id, "Iltimos, imtihonni qaytadan boshlang!", show_alert=True)
        return

    data_parts = call.data.split("_")
    q_index = int(data_parts[1])
    selected_option = data_parts[2]
    
    session = user_sessions[user_id]
    
    if q_index != session["current_q"]:
        bot.answer_callback_query(call.id, "Bu savolga allaqachon javob bergansiz!", show_alert=True)
        return

    current_q_data = QUESTIONS[q_index]
    if selected_option == current_q_data["correct"]:
        session["correct_ans"] += 1
        bot.answer_callback_query(call.id, "To'g'ri! ✅")
    else:
        bot.answer_callback_query(call.id, f"Noto'g'ri! ❌\nTo'g'ri javob: {current_q_data['correct']}", show_alert=True)

    next_q_index = q_index + 1
    session["current_q"] = next_q_index

    if next_q_index < len(QUESTIONS):
        next_q_data = QUESTIONS[next_q_index]
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=next_q_data["question"],
            reply_markup=get_quiz_keyboard(next_q_data["options"], next_q_index)
        )
    else:
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

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("🚀 Imtihonni boshlash"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=result_text,
            parse_mode="Markdown"
        )
        
        bot.send_message(call.message.chat.id, "Qayta urinish uchun pastdagi tugmani bosing:", reply_markup=markup)
        del user_sessions[user_id]

# Botni alohida oqimda ishga tushirish funksiyasi
def run_bot():
    print("Telegram bot so'rovlarni qabul qilishni boshladi...")
    bot.infinity_polling()

# 3. LOYIHANI ISHGA TUSHIRISH MANTIQI
if __name__ == "__main__":
    # Birinchi navbatda botni fonda (Thread ichida) ishga tushiramiz
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True  # Asosiy dastur yopilsa, bu ham yopilishi uchun
    bot_thread.start()
    
    # Keyin esa Flask serverini ASOSIY OQIMDA ishga tushiramiz (Render portni aniq ko'rishi uchun)
    print("Flask veb-server ishga tushmoqda...")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)