from pyrogram import Client, idle, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
import datetime
import secrets
import requests
import time
import asyncio
from pymongo import MongoClient

app = Client(
    'my_bot',
    api_id=10247139,
    api_hash='96b46175824223a33737657ab943fd6a',
    bot_token='5786017840:AAEsbeA-1QUdr_0Stp3Bg8V0ov0kxl1A_28'
)

# Connect to MongoDB
client = MongoClient('mongodb+srv://anime:2004@cluster0.ghzkqob.mongodb.net/?retryWrites=true&w=majority')
db = client['user_tokens']

async def is_user_authorized(user_id, usr_txt):
    # Check if the user_id exists in the user_tokens collection
    user_token = db.user_tokens.find_one({"user_id": user_id, "token": usr_txt}))
    if user_token:
        expiration_time = user_token["expiration_time"]
        return expiration_time > asyncio.get_event_loop().time()
    return False

async def delete_expired_tokens():
    while True:
        current_time = asyncio.get_event_loop().time()
        expired_tokens = db.user_tokens.find({"expiration_time": {"$lte": current_time}})
        for token in expired_tokens:
            db.user_tokens.delete_one({"_id": token["_id"]})
        await asyncio.sleep(30)
        
@app.on_message(filters.private & (filters.command("start", prefixes="/") | filters.command("help", prefixes="/")))
async def handle_start_help_command(bot, cmd: Message):
    user_id = cmd.from_user.id
    usr_cmd = cmd.text.split("_", 1)[-1]
    usr_txt = usr_cmd.split("_")[-1]
    if await is_user_authorized(user_id, usr_txt):
        await cmd.reply("You are authorized to use the bot.")
        
    else:
        # Generate a new token and set its expiration time to 24 hours from now
        expiration_time = asyncio.get_event_loop().time() + 60
        # Store the token in MongoDB
        enc = secrets.token_hex(nbytes=16)
        db.user_tokens.insert_one({"user_id": user_id, "token": enc, "expiration_time": expiration_time})
        await cmd.reply("You have been authorized for 24 hours. Please use this link to start: https://t.me/anime_data_bot?start=" + enc)
if __name__ == '__main__':
    asyncio.ensure_future(delete_expired_tokens())
    app.run()

