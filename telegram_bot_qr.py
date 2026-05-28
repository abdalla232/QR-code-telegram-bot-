import asyncio
import io
import qrcode

from PIL import Image, ImageDraw, ImageFont, ImageFilter

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


# ================= STYLE MENU =================
@dp.callback_query(F.data == "qr")
async def qr_button(call: CallbackQuery, state: FSMContext):

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⚫ Classic", callback_data="style_classic")],
        [types.InlineKeyboardButton(text="🌑 Dark", callback_data="style_dark")],
        [types.InlineKeyboardButton(text="💎 Premium Glow", callback_data="style_premium")]
    ])

    await call.message.answer("🎨 Choose QR style:", reply_markup=keyboard)
    await call.answer()


# ================= SAVE STYLE =================
@dp.callback_query(F.data.startswith("style_"))
async def choose_style(call: CallbackQuery, state: FSMContext):

    style = call.data.replace("style_", "")

    await state.update_data(style=style)

    await call.message.answer("✍️ Send text or link:")
    await state.set_state(QRState.waiting_text)

    await call.answer()


# ================= GET TEXT =================
@dp.message(QRState.waiting_text)
async def get_text(message: Message, state: FSMContext):

    data = await state.get_data()
    style = data.get("style", "classic")

    photo = create_qr(message.text, style)

    await message.answer_photo(photo=photo)

    await state.clear()


# ================= QR GENERATOR =================
def create_qr(text, style="classic"):

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

    qr_img = qr_img.resize((400, 400))

    canvas = Image.new("RGBA", (800, 800))
    pos = ((800 - 400) // 2, (800 - 400) // 2)


    # ================= CLASSIC =================
    if style == "classic":
        canvas = Image.new("RGBA", (800, 800), (255, 255, 255, 255))
        canvas.paste(qr_img, pos, qr_img)


    # ================= DARK =================
    elif style == "dark":
        canvas = Image.new("RGBA", (800, 800), (20, 20, 20, 255))
        canvas.paste(qr_img, pos, qr_img)


    # ================= PREMIUM GLOW =================
    elif style == "premium":

        canvas = Image.new("RGBA", (800, 800), (10, 10, 25, 255))

        base = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
        base.paste(qr_img, pos, qr_img)

        # 🔥 Glow layers (قوي)
        glow1 = base.copy().filter(ImageFilter.GaussianBlur(8))
        glow2 = base.copy().filter(ImageFilter.GaussianBlur(16))
        glow3 = base.copy().filter(ImageFilter.GaussianBlur(25))

        canvas = Image.alpha_composite(canvas, glow3)
        canvas = Image.alpha_composite(canvas, glow2)
        canvas = Image.alpha_composite(canvas, glow1)

        # QR الحاد فوق الغلو
        canvas = Image.alpha_composite(canvas, base)

        # ✨ نص بسيط
        draw = ImageDraw.Draw(canvas)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        draw.text((20, 20), "QR PREMIUM", fill=(255, 255, 255, 200), font=font)


    # ================= SAVE =================
    bio = io.BytesIO()
    bio.name = "qr.png"
    canvas.save(bio, "PNG")
    bio.seek(0)

    return BufferedInputFile(bio.getvalue(), filename="qr.png")


# ================= RUN =================
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
