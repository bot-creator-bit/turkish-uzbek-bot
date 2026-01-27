import logging
import random
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import sqlite3

# Bot tokeningizni muhit o'zgaruvchisidan yoki to'g'ridan-to'g'ri olish
TOKEN = os.getenv("BOT_TOKEN", "8336134380:AAFBWpbfhY4HdiuVevvXxHjlfqpH3pn-8aE")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM States
class TestStates(StatesGroup):
    choosing_level = State()
    ready_to_start = State()
    taking_test = State()

# JSON fayldan so'zlarni yuklash
def load_words_from_json():
    """JSON fayldan barcha so'zlarni yuklaydi"""
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("words.json fayli topilmadi!")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"JSON faylni o'qishda xatolik: {e}")
        return {}

# Database yaratish va so'zlarni qo'shish
def init_database():
    """Database va jadvallarni yaratadi, JSON dan so'zlarni yuklaydi"""
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    
    # Users jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level TEXT,
            test_count INTEGER DEFAULT 0
        )
    ''')
    
    # Words jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            uzbek TEXT,
            turkish TEXT
        )
    ''')
    
    # Test results jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            level TEXT,
            correct INTEGER,
            incorrect INTEGER,
            test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # So'zlar mavjudligini tekshirish
    cursor.execute("SELECT COUNT(*) FROM words")
    if cursor.fetchone()[0] == 0:
        # JSON dan so'zlarni yuklash
        words_data = load_words_from_json()
        
        if words_data:
            logging.info("JSON fayldan so'zlarni databasega yuklash boshlandi...")
            
            for level, words in words_data.items():
                for uzb, turk in words:
                    cursor.execute(
                        "INSERT INTO words (level, uzbek, turkish) VALUES (?, ?, ?)",
                        (level, uzb, turk)
                    )
            
            conn.commit()
            logging.info(f"✅ Jami {len(words_data)} daraja uchun so'zlar muvaffaqiyatli yuklandi!")
        else:
            logging.warning("⚠️ JSON fayldan so'zlar yuklanmadi!")
    else:
        logging.info("✅ Database allaqachon so'zlar bilan to'ldirilgan")
    
    conn.close()

# Foydalanuvchini database saqlash
def save_user(user_id, username, level):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, level, test_count)
        VALUES (?, ?, ?, COALESCE((SELECT test_count FROM users WHERE user_id = ?), 0))
    ''', (user_id, username, level, user_id))
    conn.commit()
    conn.close()

# Foydalanuvchi ma'lumotlarini olish
def get_user(user_id):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Test uchun so'zlarni olish
def get_test_words(level, count=20):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT uzbek, turkish FROM words WHERE level = ? ORDER BY RANDOM() LIMIT ?",
        (level, count)
    )
    words = cursor.fetchall()
    conn.close()
    return words

# Test natijasini saqlash
def save_test_result(user_id, level, correct, incorrect):
    conn = sqlite3.connect('language_test.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO test_results (user_id, level, correct, incorrect)
        VALUES (?, ?, ?, ?)
    ''', (user_id, level, correct, incorrect))
    cursor.execute(
        "UPDATE users SET test_count = test_count + 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

# Daraja tanlash tugmalari
def get_level_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A1 - Boshlang'ich", callback_data="level_A1")],
        [InlineKeyboardButton(text="A2 - Elementar", callback_data="level_A2")],
        [InlineKeyboardButton(text="B1 - O'rta", callback_data="level_B1")],
        [InlineKeyboardButton(text="B2 - O'rta-Yuqori", callback_data="level_B2")],
        [InlineKeyboardButton(text="C1 - Ilg'or", callback_data="level_C1")],
        [InlineKeyboardButton(text="C2 - Mohir", callback_data="level_C2")]
    ])
    return keyboard

# Testni boshlash tugmalari
def get_start_test_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data="start_yes"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="start_no")
        ]
    ])
    return keyboard

# Javob tugmalari
def get_answer_keyboard(options):
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f"answer_{i}")] 
               for i, opt in enumerate(options)]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# /start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    
    if user:
        await message.answer(
            f"Xush kelibsiz, {message.from_user.first_name}!\n\n"
            f"Sizning darajangiz: {user[2]}\n"
            f"Topshirgan testlar soni: {user[3]}\n\n"
            f"Yangi test boshlash uchun darajangizni tanlang:",
            reply_markup=get_level_keyboard()
        )
    else:
        await message.answer(
            f"Assalomu alaykum, {message.from_user.first_name}! 🇺🇿🇹🇷\n\n"
            f"O'zbek-Turk tili test botiga xush kelibsiz!\n\n"
            f"Iltimos, o'z darajangizni tanlang:",
            reply_markup=get_level_keyboard()
        )
    await state.set_state(TestStates.choosing_level)

# Daraja tanlash
@dp.callback_query(F.data.startswith("level_"))
async def process_level_selection(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(level=level)
    
    save_user(callback.from_user.id, callback.from_user.username, level)
    
    await callback.message.edit_text(
        f"Siz {level} darajasini tanladingiz.\n\n"
        f"Testni boshlashga tayyormisiz?\n"
        f"Test 20 ta savoldan iborat.",
        reply_markup=get_start_test_keyboard()
    )
    await state.set_state(TestStates.ready_to_start)
    await callback.answer()

# Testni boshlash
@dp.callback_query(F.data == "start_yes")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    level = data.get('level')
    
    # Testni boshlash
    words = get_test_words(level, 20)
    
    if not words:
        await callback.message.edit_text("Xatolik! Ushbu daraja uchun so'zlar topilmadi.")
        await state.clear()
        return
    
    # Test savollarini tayyorlash
    questions = []
    for uzb, turk in words:
        # Tasodifiy yo'nalish: O'zbekcha->Turkcha yoki Turkcha->O'zbekcha
        if random.choice([True, False]):
            question_word = uzb
            correct_answer = turk
            question_type = "uz_tr"
        else:
            question_word = turk
            correct_answer = uzb
            question_type = "tr_uz"
        
        # Noto'g'ri javoblar uchun boshqa so'zlarni olish
        other_words = get_test_words(level, 4)
        wrong_answers = []
        for w in other_words:
            if question_type == "uz_tr":
                if w[1] != correct_answer:
                    wrong_answers.append(w[1])
            else:
                if w[0] != correct_answer:
                    wrong_answers.append(w[0])
            if len(wrong_answers) >= 3:
                break
        
        # Javoblarni aralashtirish
        options = wrong_answers[:3] + [correct_answer]
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        questions.append({
            'question': question_word,
            'options': options,
            'correct': correct_index,
            'type': question_type
        })
    
    await state.update_data(
        questions=questions,
        current_question=0,
        correct_answers=0,
        incorrect_answers=0
    )
    
    # Birinchi savolni yuborish
    await send_question(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "start_no")
async def cancel_test(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Test bekor qilindi. Qaytadan boshlash uchun /start buyrug'ini yuboring."
    )
    await state.clear()
    await callback.answer()

# Savolni yuborish
async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    current = data['current_question']
    
    if current >= len(questions):
        # Test tugadi
        await finish_test(message, state)
        return
    
    question = questions[current]
    lang_direction = "🇺🇿 ➡️ 🇹🇷" if question['type'] == "uz_tr" else "🇹🇷 ➡️ 🇺🇿"
    
    text = (
        f"Savol {current + 1}/20 {lang_direction}\n\n"
        f"<b>{question['question']}</b> so'zining tarjimasini toping:"
    )
    
    await message.edit_text(
        text,
        reply_markup=get_answer_keyboard(question['options']),
        parse_mode="HTML"
    )
    await state.set_state(TestStates.taking_test)

# Javobni tekshirish
@dp.callback_query(F.data.startswith("answer_"))
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answer_index = int(callback.data.split("_")[1])
    
    questions = data['questions']
    current = data['current_question']
    correct_answers = data['correct_answers']
    incorrect_answers = data['incorrect_answers']
    
    question = questions[current]
    
    if answer_index == question['correct']:
        correct_answers += 1
        result = "✅ To'g'ri!"
    else:
        incorrect_answers += 1
        correct_word = question['options'][question['correct']]
        result = f"❌ Noto'g'ri! To'g'ri javob: <b>{correct_word}</b>"
    
    # Keyingi savolga o'tish
    await state.update_data(
        current_question=current + 1,
        correct_answers=correct_answers,
        incorrect_answers=incorrect_answers
    )
    
    await callback.answer(result, show_alert=True)
    await send_question(callback.message, state)

# Testni tugatish
async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct = data['correct_answers']
    incorrect = data['incorrect_answers']
    level = data['level']
    
    total = correct + incorrect
    percentage = (correct / total * 100) if total > 0 else 0
    
    # Natijani saqlash
    save_test_result(message.chat.id, level, correct, incorrect)
    
    # Baho berish
    if percentage >= 90:
        grade = "A'lo! 🌟"
    elif percentage >= 75:
        grade = "Yaxshi! 👍"
    elif percentage >= 60:
        grade = "Qoniqarli ✅"
    else:
        grade = "Yaxshilanishi kerak 📚"
    
    result_text = (
        f"🎉 <b>Test yakunlandi!</b>\n\n"
        f"📊 <b>Natijalaringiz:</b>\n"
        f"✅ To'g'ri javoblar: {correct}\n"
        f"❌ Noto'g'ri javoblar: {incorrect}\n"
        f"📈 Foiz: {percentage:.1f}%\n\n"
        f"🏆 Baho: {grade}\n\n"
        f"Yangi test boshlash uchun /start buyrug'ini yuboring."
    )
    
    await message.edit_text(result_text, parse_mode="HTML")
    await state.clear()

# Botni ishga tushirish
async def main():
    """Bot ishga tushirish"""
    try:
        # Database yaratish va so'zlarni yuklash
        init_database()
        logging.info("✅ Bot muvaffaqiyatli ishga tushdi!")
        
        # Polling boshlash
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Bot ishga tushirishda xatolik: {e}")

if __name__ == "__main__":
    asyncio.run(main())