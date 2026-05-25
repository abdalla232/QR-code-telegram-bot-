import asyncio
import io
import qrcode

from PIL import Image

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

TOKEN = "8639399155:AAERI2N4r7LqnQCTdL7LjofZ4yM153VY9YY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= STATES =================
class QRState(StatesGroup):
    waiting_text = State()

# ================= QR FUNCTION =================
def create_professional_qr(text):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(text)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # Load logo (syria flag)
    logo = Image.open("syria_flag.png").convert("RGBA")

    # Resize logo
    qr_width, qr_height = qr_img.size
    logo_size = qr_width // 4
    logo = logo.resize((logo_size, logo_size))

    # Center position
    pos = (
        (qr_width - logo_size) // 2,
        (qr_height - logo_size) // 2
    )

    qr_img.paste(logo, pos, mask=logo)

    bio = io.BytesIO()
    bio.name = "qr.png"
    qr_img.save(bio, "PNG")
    bio.seek(0)

    return BufferedInputFile(bio.getvalue(), filename="qr.png")

# ================= START =================
@dp.message(Command("start"))
async def start(message: Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎯 Generate QR Code", callback_data="qr")]
    ])

    await message.answer("👋 Welcome!\nPress button to generate QR Code:", reply_markup=keyboard)

# ================= BUTTON =================
@dp.callback_query(F.data == "qr")
async def qr_button(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✍️ Send the text or link:")
    await state.set_state(QRState.waiting_text)
    await call.answer()

# ================= GENERATE QR =================
@dp.message(QRState.waiting_text)
async def generate_qr(message: Message, state: FSMContext):
    photo = create_professional_qr(message.text)

    await message.answer_photo(photo=photo)

    await state.clear()

# ================= RUN =================
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
