import pyrogram
import datetime
import secrets
import requests
import time
import pymongo


# URL shortener API endpoint
SHORTENER_API = 'https://tnshort.net/api'

# Connect to MongoDB (Make sure you have MongoDB installed and running)
client = pymongo.MongoClient('mongodb+srv://anime:2004@cluster0.ghzkqob.mongodb.net/?retryWrites=true&w=majority')
db = client['bot_database']

# Function to check if the user has enough credits to use the bot
def has_enough_credits(user_id):
    user_data = db.user_data.find_one({'user_id': user_id})
    if not user_data:
        return False
    return user_data.get('credits', 0) > 0

# Function to shorten a URL using the URL shortener API
def shorten_url(url):
    api_key = 'fea911843f6e7bec739708f3e562b56184342089'
    shortener_url = f'{SHORTENER_API}?api={api_key}&url={url}&format=text'
    response = requests.get(shortener_url)
    return response.text.strip()

app = pyrogram.Client(
    'my_bot',
    api_id=10247139,
    api_hash='96b46175824223a33737657ab943fd6a',
    bot_token='5786017840:AAEsbeA-1QUdr_0Stp3Bg8V0ov0kxl1A_28'
)

# Command handler for /start command
@app.on_message(pyrogram.filters.command('start'))
def start_command(client, message):
    user_id = message.from_user.id

    user_data = db.user_data.find_one({'user_id': user_id})
    if not user_data:
        user_data = {'user_id': user_id, 'credits': 0, 'trial_expiry': None}

    # Check if the user is in the trial period
    if user_data['trial_expiry'] is None:
        user_data['trial_expiry'] = datetime.datetime.now() + datetime.timedelta(minutes=2)
        message.reply("Welcome! You have a 3-day free trial. Enjoy!")

    elif user_data['trial_expiry'] > datetime.datetime.now():
        message.reply("You are still in your trial period. Enjoy!")

    elif has_enough_credits(user_id):
        message.reply("You have enough credits to use the bot.")

    db.user_data.replace_one({'user_id': user_id}, user_data, upsert=True)

# Command handler for /earncredit command
@app.on_message(pyrogram.filters.command('earncredit'))
def earn_credit_command(client, message):
    user_id = message.from_user.id

    user_data = db.user_data.find_one({'user_id': user_id})
    if not user_data:
        user_data = {'user_id': user_id, 'credits': 0, 'trial_expiry': None}

    # Check if the user has already earned a credit today
    if 'last_earned' in user_data and \
            user_data['last_earned'] + datetime.timedelta(minutes=2) > datetime.datetime.now():
        message.reply("You have already earned a credit today. Try again tomorrow!")

    else:
        # Try to shorten a sample URL (replace with your own)
        enc = secrets.token_hex(nbytes=16)
        sample_url = f"https://t.me/anime_data_bot?start={enc}"
        shortened_url = shorten_url(sample_url)

        if enc in update.text:
            user_data['credits'] += 1
            user_data['last_earned'] = datetime.datetime.now()
            message.reply(f"Congratulations! You earned 1 credit. You can now use the bot for 24 hours.")
        else:
            message.reply("Failed to earn a credit. Please try again later.")

    db.user_data.replace_one({'user_id': user_id}, user_data, upsert=True)

if __name__ == '__main__':
    app.run()
