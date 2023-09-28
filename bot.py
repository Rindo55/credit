from pyrogram import Client, filters
import datetime
import asyncio
from pymongo import MongoClient
import secrets 

# Initialize the Pyrogram client
app = Client(
    'my_bot',
    api_id=10247139,
    api_hash='96b46175824223a33737657ab943fd6a',
    bot_token='5786017840:AAEsbeA-1QUdr_0Stp3Bg8V0ov0kxl1A_28'
)

# Connect to MongoDB
client = MongoClient('mongodb+srv://anime:2004@cluster0.ghzkqob.mongodb.net/?retryWrites=true&w=majority')
db = client['user_tokens']
db.user_tokens.create_index([("user_id", 1)], unique=True)

async def is_user_authorized(user_id, token):
    # Check if the user_id and token exist in the user_tokens collection
    user_token = db.user_tokens.find_one({"user_id": user_id, "token": token})
    if user_token:
        expiration_time = user_token["expiration_time"]
        return expiration_time > datetime.datetime.utcnow()
    return False

async def delete_expired_tokens():
    while True:
        current_time = datetime.datetime.utcnow()
        expired_tokens = db.user_tokens.find({"expiration_time": {"$lte": current_time}})
        for token in expired_tokens:
            db.user_tokens.delete_one({"_id": token["_id"]})
        await asyncio.sleep(30)

@app.on_message(filters.private & filters.command("start"))
async def handle_start_command(bot, cmd):
    user_id = cmd.from_user.id
    # Generate a new token and set its expiration time to 24 hours from now
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    enc = secrets.token_hex(nbytes=16)
    db.user_tokens.insert_one({"user_id": user_id, "token": enc, "expiration_time": expiration_time})
    await cmd.reply("You have been authorized for 24 hours. Please use this link to start: https://t.me/anime_data_bot?start=" + enc)
@app.on_message(filters.private & filters.regex(r'^https://t\.me/anime_data_bot\?start=(\w+)$'))
async def handle_link_with_token(bot, msg):
    user_id = msg.from_user.id
    token = msg.matches[0].group(1)

    if await is_user_authorized(user_id, token):
        await msg.reply("You are authorized to use the bot.")
    else:
        await msg.reply("Unauthorized. Please start the bot using the /start command.")

if __name__ == '__main__':
    asyncio.ensure_future(delete_expired_tokens())
    app.run()
