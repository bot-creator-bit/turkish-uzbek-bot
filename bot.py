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

# 🔥 BU YERGA YANGI TOKENNI YOZING
TOKEN = os.getenv("BOT_TOKEN", "8085922451:AAHiBt-5HvDL51LZmSQgfw_4ls5p6_zEluI")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Database yo'li
def get_db_path():
    """Database fayl yo'lini qaytaradi"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'language_test.db')

# FSM States
class TestStates(StatesGroup):
    choosing_level = State()
    ready_to_start = State()
    taking_test = State()

# JSON fayldan so'zlarni yuklash
def load_words_from_json():
    """JSON fayldan barcha so'zlarni yuklaydi"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'words.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)
            logging.info(f"✅ JSON yuklandi: {len(words_data)} daraja")
            return words_data
    except FileNotFoundError:
        logging.error(f"❌ words.json topilmadi: {json_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON xatosi: {e}")
        return {}

# Database yaratish
def init_database():
    """Database va jadvallarni yaratadi"""
    db_path = get_db_path()
    logging.info(f"📁 Database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level TEXT,
            test_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            uzbek TEXT,
            turkish TEXT
        )
    ''')
    
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
    
    cursor.execute("SELECT COUNT(*) FROM words")
    word_count = cursor.fetchone()[0]
    
    if word_count == 0:
        logging.info("📥 So'zlarni yuklash...")
        words_data = load_words_from_json()
        
        if words_data:
            total = 0
            for level, words in words_data.items():
                for uzb, turk in words:
                    cursor.execute(
                        "INSERT INTO words (level, uzbek, turkish) VALUES (?, ?, ?)",
                        (level, uzb, turk)
                    )
                    total += 1
            conn.commit()
            logging.info(f"✅ {total} ta so'z yuklandi!")
        else:
            logging.error("⚠️ JSON fayl bo'sh!")
    else:
        logging.info(f"✅ Database: {word_count} ta so'z")
    
    conn.close()

def save_user(user_id, username, level):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, level, test_count)
        VALUES (?, ?, ?, COALESCE((SELECT test_count FROM users WHERE user_id = ?), 0))
    ''', (user_id, username, level, user_id))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_test_words(level, count=20):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "SELECT uzbek, turkish FROM words WHERE level = ? ORDER BY RANDOM() LIMIT ?",
        (level, count)
    )
    words = cursor.fetchall()
    conn.close()
    return words

def save_test_result(user_id, level, correct, incorrect):
    conn = sqlite3.connect(get_db_path())
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

def get_level_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A1 - Boshlang'ich", callback_data="level_A1")],
        [InlineKeyboardButton(text="A2 - Elementar", callback_data="level_A2")],
        [InlineKeyboardButton(text="B1 - O'rta", callback_data="level_B1")],
        [InlineKeyboardButton(text="B2 - O'rta-Yuqori", callback_data="level_B2")],
        [InlineKeyboardButton(text="C1 - Ilg'or", callback_data="level_C1")],
        [InlineKeyboardButton(text="C2 - Mohir", callback_data="level_C2")]
    ])

def get_start_test_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data="start_yes"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="start_no")
        ]
    ])

def get_answer_keyboard(options):
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f"answer_{i}")] 
               for i, opt in enumerate(options)]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    
    if user:
        await message.answer(
            f"Xush kelibsiz, {message.from_user.first_name}!\n\n"
            f"Darajangiz: {user[2]}\n"
            f"Testlar: {user[3]}\n\n"
            f"Yangi test uchun darajani tanlang:",
            reply_markup=get_level_keyboard()
        )
    else:
        await message.answer(
            f"Assalomu alaykum, {message.from_user.first_name}! 🇺🇿🇹🇷\n\n"
            f"O'zbek-Turk tili test botiga xush kelibsiz!\n\n"
            f"Darajangizni tanlang:",
            reply_markup=get_level_keyboard()
        )
    await state.set_state(TestStates.choosing_level)

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

@dp.callback_query(F.data == "start_yes")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    level = data.get('level')
    
    words = get_test_words(level, 20)
    
    if not words:
        await callback.message.edit_text(f"❌ {level} uchun so'zlar topilmadi!")
        await state.clear()
        return
    
    questions = []
    for uzb, turk in words:
        if random.choice([True, False]):
            question_word = uzb
            correct_answer = turk
            question_type = "uz_tr"
        else:
            question_word = turk
            correct_answer = uzb
            question_type = "tr_uz"
        
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
        
        options = wrong_answers[:3] + [correct_answer]
        random.shuffle(options)
        
        questions.append({
            'question': question_word,
            'options': options,
            'correct': options.index(correct_answer),
            'type': question_type
        })
    
    await state.update_data(
        questions=questions,
        current_question=0,
        correct_answers=0,
        incorrect_answers=0
    )
    
    await send_question(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "start_no")
async def cancel_test(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Test bekor qilindi. /start")
    await state.clear()
    await callback.answer()

async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data['questions']
    current = data['current_question']
    
    if current >= len(questions):
        await finish_test(message, state)
        return
    
    question = questions[current]
    lang = "🇺🇿 ➡️ 🇹🇷" if question['type'] == "uz_tr" else "🇹🇷 ➡️ 🇺🇿"
    
    await message.edit_text(
        f"Savol {current + 1}/20 {lang}\n\n"
        f"<b>{question['question']}</b> so'zining tarjimasini toping:",
        reply_markup=get_answer_keyboard(question['options']),
        parse_mode="HTML"
    )
    await state.set_state(TestStates.taking_test)

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
        result = f"❌ Noto'g'ri! To'g'ri: {question['options'][question['correct']]}"
    
    await state.update_data(
        current_question=current + 1,
        correct_answers=correct_answers,
        incorrect_answers=incorrect_answers
    )
    
    await callback.answer(result, show_alert=True)
    await send_question(callback.message, state)

async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct = data['correct_answers']
    incorrect = data['incorrect_answers']
    level = data['level']
    
    total = correct + incorrect
    percentage = (correct / total * 100) if total > 0 else 0
    save_test_result(message.chat.id, level, correct, incorrect)
    
    if percentage >= 90:
        grade = "A'lo! 🌟"
    elif percentage >= 75:
        grade = "Yaxshi! 👍"
    elif percentage >= 60:
        grade = "Qoniqarli ✅"
    else:
        grade = "Yaxshilanish kerak 📚"
    
    await message.edit_text(
        f"🎉 <b>Test yakunlandi!</b>\n\n"
        f"📊 Natijalar:\n"
        f"✅ To'g'ri: {correct}\n"
        f"❌ Noto'g'ri: {incorrect}\n"
        f"📈 Foiz: {percentage:.1f}%\n\n"
        f"🏆 Baho: {grade}\n\n/start",
        parse_mode="HTML"
    )
    await state.clear()

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("✅ Webhook o'chirildi")
        
        init_database()
        logging.info("✅ Bot ishga tushdi!")
        
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Xato: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
