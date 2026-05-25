import asyncio
import io
import qrcode

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

TOKEN = "8639399155:AAERI2N4r7LqnQCTdL7LjofZ4yM153VY9YY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class QRState(StatesGroup):
    waiting_text = State()

@dp.message(Command("start"))
async def start(message: Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Create QR Code", callback_data="create_qr")]
    ])

    await message.answer("Welcome 👋", reply_markup=keyboard)

@dp.callback_query(F.data == "create_qr")
async def create_qr(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Send text for QR:")
    await state.set_state(QRState.waiting_text)
    await call.answer()

@dp.message(QRState.waiting_text)
async def generate_qr(message: Message, state: FSMContext):
    text = message.text

    qr = qrcode.make(text)

    bio = io.BytesIO()
    qr.save(bio, "PNG")
    bio.seek(0)

    # ✅ FIX HERE
    photo = BufferedInputFile(bio.getvalue(), filename="qr.png")

    await message.answer_photo(photo=photo)

    await state.clear()

async def main():
    print("Bot running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())