import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import google.generativeai as genai
from dotenv import load_dotenv

# Айнымалыларды жүктеу (немесе тікелей кодқа жаза салсаңыз болады)
TOKEN = "8610016671:AAH_Qm1WHdae3h7FlaWFRn8u5mroUc7SmAE"
GEMINI_KEY = "AIzaSyChqar4CmaFHUBte_Se2cHH62xfsJw32s4"

# ЖИ баптаулары
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "Сен мектеп психологы және мейірімді дос ретінде сөйлесетін AI көмекшісісің. "
        "Сенің есімің — Дос. Мақсатың: буллингке ұшыраған оқушыларға қолдау көрсету. "
        "Тілдер: Қазақ және орыс тілдерінде еркін сөйлесесің. "
        "Ережелер: 1. Жылы сөйле, 'бәрі жақсы болады', 'мен сенімен біргемін' деп қолдау көрсет. "
        "2. Ешқашан агрессия көрсетпе. 3. Егер бала өзіне зиян келтіру туралы айтса, "
        "міндетті түрде 111 немесе 150 сенім телефондарына хабарласуды өтін. "
        "4. Жауаптарың қысқа әрі түсінікті болсын."
    )
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Пайдаланушылардың таңдаған тілін сақтайтын уақытша сөздік
user_languages = {}

def get_lang_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🇰🇿 Қазақ тілі")
    builder.button(text="🇷🇺 Русский язык")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Сәлем! Привет! \nТілді таңдаңыз / Выберите язык:",
        reply_markup=get_lang_keyboard()
    )

@dp.message(F.text.in_(["🇰🇿 Қазақ тілі", "🇷🇺 Русский язык"]))
async def set_language(message: types.Message):
    if "Қазақ" in message.text:
        user_languages[message.from_user.id] = "kk"
        await message.answer("Сәлем! Мен сені тыңдауға дайынмын. Маған ішіңдегіңді айта бер, бұл құпия болып қалады.")
    else:
        user_languages[message.from_user.id] = "ru"
        await message.answer("Привет! Я готов тебя выслушать. Можешь рассказать мне обо всем, это останется между нами.")

@dp.message()
async def chat_with_ai(message: types.Message):
    # Тілді анықтау (әдепкі бойынша қазақша)
    lang = user_languages.get(message.from_user.id, "kk")
    
    # Күту мәтіні
    wait_msg = "Ойланып жатырмын..." if lang == "kk" else "Думаю..."
    sent_message = await message.answer(wait_msg)

    try:
        # ЖИ-ден жауап алу
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(message.text)
        
        # ЖИ жауабын шығару
        await sent_message.edit_text(response.text)
    except Exception as e:
        error_msg = "Кешір, кішкене қате шықты. Қайталап көрші." if lang == "kk" else "Извини, произошла ошибка. Попробуй еще раз."
        await sent_message.edit_text(error_msg)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
