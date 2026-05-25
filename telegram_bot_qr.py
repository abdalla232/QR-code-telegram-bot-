import asyncio
import io
import qrcode

from PIL import Image, ImageDraw, ImageFont

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
def create_styled_qr(text, bot_name="QR Bot"):

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(text)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGBA")

    qr_size = 400
    qr_img = qr_img.resize((qr_size, qr_size))

    # 🎯 نعمل canvas جديد بدل background paste
    canvas = Image.new("RGBA", (800, 800), (20, 20, 20, 255))  # خلفية نظيفة

    # دمج QR
    pos = ((800 - qr_size) // 2, (800 - qr_size) // 2)
    canvas.paste(qr_img, pos, qr_img)

    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), bot_name, font=font)
    text_width = bbox[2] - bbox[0]

    draw.text(
        ((800 - text_width) // 2, 50),
        bot_name,
        fill=(255, 255, 255, 255),
        font=font
    )

    bio = io.BytesIO()
    bio.name = "qr.png"
    canvas.save(bio, "PNG")
    bio.seek(0)

    return BufferedInputFile(bio.getvalue(), filename="qr.png")


# ================= START =================
@dp.message(Command("start"))
async def start(message: Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎯 Generate QR Code", callback_data="qr")]
    ])

    await message.answer(
        "👋 Welcome!\nPress button to generate QR Code:",
        reply_markup=keyboard
    )


# ================= BUTTON =================
@dp.callback_query(F.data == "qr")
async def qr_button(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✍️ Send the text or link:")
    await state.set_state(QRState.waiting_text)
    await call.answer()


# ================= GENERATE QR =================
@dp.message(QRState.waiting_text)
async def generate_qr(message: Message, state: FSMContext):

    if not message.text:
        await message.answer("❌ Please send a valid text or link")
        return

    photo = create_styled_qr(
        text=message.text,
        bot_name="QR Generator Bot"
    )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔁 Generate again", callback_data="qr")]
    ])

    await message.answer_photo(photo=photo, reply_markup=keyboard)

    await state.clear()


# ================= RUN =================
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
