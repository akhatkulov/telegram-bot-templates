import telebot
from telebot.async_telebot import AsyncTeleBot
from alch import create_user, get_step, put_step, user_count, get_all_user, get_channel, put_channel, get_channel_with_id, delete_channel
from helper.buttons import admin_buttons, channel_control, join_key

import conf
import asyncio

API_TOKEN = conf.BOT_TOKEN
ADMIN_ID = conf.ADMIN_id

bot = AsyncTeleBot(API_TOKEN, parse_mode="html")

async def join(user_id):
    try:
        channels = await get_channel()
        r = 0
        for channel in channels:
            res = await bot.get_chat_member(f"@{channel}", user_id)
            if res.status in ['member', 'creator', 'administrator']:
                r += 1
        if r != len(channels):
            await bot.send_message(user_id,
                                   "<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>",
                                   reply_markup=join_key())
            return False
        else:
            return True
    except Exception as e:
        await bot.send_message(chat_id=ADMIN_ID, text=f"Kanalga bot admin qilinmagan yoki xato: {str(e)}")
        return True

@bot.message_handler(commands=['start'])
async def start(message: telebot.types.Message):
    if message.text == "/start" and await join(message.chat.id):
        await bot.send_message(message.chat.id, "<b>Salom</b>")
        try:
            await create_user(cid=message.chat.id, name=message.chat.first_name)
        except Exception as e:
            print(f"Error creating user: {str(e)}")

@bot.message_handler(content_types=['text'])
async def more(message: telebot.types.Message):
    if message.text == "/admin" and message.chat.id == ADMIN_ID:
        await bot.send_message(chat_id=ADMIN_ID, text="Salom, Admin", reply_markup=admin_buttons())
        await put_step(cid=message.chat.id, step="!!!")

    if await get_step(message.chat.id) == "channel_del" and message.text != "/start" and message.text != "/admin":
        channel_id = int(message.text)
        if await delete_channel(ch_id=channel_id):
            await bot.send_message(chat_id=message.chat.id, text="Kanal olib tashlandi")
            await put_step(cid=message.chat.id, step="!!!")
        else:
            await bot.send_message(chat_id=message.chat.id, text="Xatolik! IDni to'g'ri kiritdingizmi tekshiring!")

    if await get_step(message.chat.id) == "add_channel" and message.text != "/start" and message.text != "/admin":
        if await put_channel(message.text):
            await bot.send_message(chat_id=message.chat.id, text=f"{message.text} kanali qabul qilindi!")
            await put_step(cid=ADMIN_ID, step="!!!")
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text="Xatolik! Bu kanal oldin qo'shilgan bo'lishi mumkin yoki boshqa xatolik, iltimos tekshiring")
            await put_step(cid=ADMIN_ID, step="!!!")
    
    if await get_step(message.chat.id) == 'send':
        text = message.text
        mid = message.message_id
        await bot.send_message(chat_id=message.chat.id, text="Xabar yuborish boshlandi")
        try:
            for user_id in await get_all_user():
                try:
                    await bot.forward_message(chat_id=user_id, from_chat_id=ADMIN_ID, message_id=mid)
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {str(e)}")
            await bot.send_message(chat_id=message.chat.id, text="Tarqatish yakunlandi")
            await put_step(cid=ADMIN_ID, step="!!!")
        except Exception as e:
            await bot.send_message(chat_id=message.chat.id, text=f"Xabar yuborishda muammo bo'ldi: {str(e)}")

@bot.callback_query_handler(lambda call: True)
async def callback_query(call: telebot.types.CallbackQuery):
    if call.data == "/start" and await join(call.message.chat.id):
        await bot.send_message(chat_id=call.message.chat.id, text="<b>Obuna tasdiqlandi✅</b>")
    elif call.data == "stat" and str(call.message.chat.id) == str(ADMIN_ID):
        await bot.send_message(chat_id=call.message.chat.id, text=f"Foydalanuvchilar soni: {await user_count()}")
    elif call.data == "send" and str(call.message.chat.id) == str(ADMIN_ID):
        await put_step(cid=call.message.chat.id, step="send")
        await bot.send_message(chat_id=call.message.chat.id, text="Forward xabaringizni yuboring")
    elif call.data == "channels" and str(call.message.chat.id) == str(ADMIN_ID):
        channels = await get_channel_with_id()
        await bot.send_message(chat_id=call.message.chat.id, text=f"Kanallar ro'yxati:{channels}", reply_markup=channel_control())
    elif call.data == "channel_add" and str(call.message.chat.id) == str(ADMIN_ID):
        await put_step(cid=call.message.chat.id, step="add_channel")
        await bot.send_message(chat_id=call.message.chat.id, text="Kanali linkini yuboring! bekor qilish uchun /start !")
    elif call.data == "channel_del" and str(call.message.chat.id) == str(ADMIN_ID):
        await put_step(cid=call.message.chat.id, step="channel_del")
        channels = await get_channel_with_id()
        await bot.send_message(chat_id=call.message.chat.id,
                               text=f"{channels}\n⚠️O'chirmoqchi bo'lgan kanalingiz IDsini bering, bekor qilish uchun /start yoki /admin deng!")

async def main():
    print(await bot.get_me())
    await bot.polling(none_stop=True)

if __name__ == '__main__':
    asyncio.run(main())
