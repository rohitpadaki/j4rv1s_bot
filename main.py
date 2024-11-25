import discord
import random
import logging
import json
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import aiohttp
from dotenv import load_dotenv
import os

#Load env
load_dotenv()

#Load yomomma xD
with open('jokes.json', 'r', encoding="utf-8") as file:
    yomomma_jokes = json.load(file)

#Logging inits
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

#Gemini Bot init
gemini_api = os.getenv("GEMINI_API")
genai.configure(api_key=gemini_api)
model = genai.GenerativeModel('gemini-pro')

#ask-gemini inits
chat = model.start_chat()

#Discord Intent inits
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Bot inits
bot = commands.Bot(command_prefix = "j!", intents=intents, help_command=None)
moods = ["with Depression", "TAG!", "unhappily","life on hard", "nothing. Help me!", "God", "with Paneer"]

#Gemini func
async def query_gemini_sdk(prompt: str):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error while querying Gemini: {type(e).__name__}")
        return "Sorry, there was an error processing your request."

#ask-gemini func
async def query_gemini_with_history(prompt: str):
    try:
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error while querying Gemini: {type(e).__name__}")
        return "Sorry, there was an error processing your request."

#Cat Image func
async def fetch_cat_image():
    url = "https://api.thecatapi.com/v1/images/search"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[0]["url"]
                else:
                    logging.error(f"Cat API returned non-200 status: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Failed to fetch cat image: {type(e).__name__}")
        return None

#Dog Image func
async def fetch_dog_image():
    url = "https://random.dog/woof.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["url"]
                else:
                    logging.error(f"Dog API returned non-200 status: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Failed to fetch dog image: {type(e).__name__}")
        return None

#Zenyatta Quote func
async def fetch_zen_quote():
    url = "https://zenquotes.io/api/random"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[0]["q"]
                else:
                    logging.error(f"Zen API returned non-200 status: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Failed to fetch zen quote: {type(e).__name__}")
        return None

#Load mentions
def load_user_messages():
    try:
        with open('user_messages.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

#Save mentions
def save_user_messages():
    with open('user_messages.json', 'w') as file:
        json.dump(user_messages, file, indent=4)

#Mentions init
user_messages = load_user_messages()

@bot.event
async def on_ready():
    await bot.tree.sync()
    mood = random.choice(moods)
    logging.info(f"Bot is online as {bot.user} with mood: {mood}")
    await bot.change_presence(activity=discord.Game(name=mood))

@bot.event
async def on_command(ctx):
    logging.info(f"Command '{ctx.command}' invoked by {ctx.author} in {ctx.channel}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower().startswith("yomomma"):
        mentioned_user = message.mentions
        joke = random.choice(yomomma_jokes)
        if mentioned_user:
            await message.channel.send(f"{mentioned_user[0].mention} {joke}")
        else:
            await message.channel.send(joke)
        logging.info(f"Sent a Yo Momma joke to {message.author} in {message.channel}: {joke}")

    if len(message.mentions) > 0 and len(message.content.strip()) == len(' '.join([mention.mention for mention in message.mentions])):
        user_id = str(message.mentions[0].id)
        if user_id in user_messages:
            await message.channel.send(user_messages[user_id].replace("{mention}", message.mentions[0].mention))
            logging.info(f"Sent a personalized message from {message.author} to {message.mentions[0]}")

    if message.channel.name == "ask-gemini":
        prompt = message.content.strip()
        async with message.channel.typing():
            response = await query_gemini_with_history(prompt)
            if len(response) > 2000:
                response = response[:2000]
        await message.channel.send(response)
        logging.info(f"Gemini response sent in #{message.channel.name} by {message.author}: {response[:50]} ...")

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.channels, name="welcome")
    if welcome_channel:
        welcome_message = f"Welcome {member.mention}!"
        gif_url = "https://tenor.com/qJpfghVYyfP.gif"
        additional_message = "Psst.. Try /help to know what I can do!"
        try:
            await welcome_channel.send(welcome_message)
            await welcome_channel.send(gif_url)
            await welcome_channel.send(additional_message)
            logging.info(f"Sent welcome message for {member} in {welcome_channel.name}")
        except Exception as e:
            logging.error(f"Error sending welcome message for {member}: {type(e).__name__}")
    else:
        logging.warning(f"No #welcome channel found in {member.guild.name}")

@bot.tree.command(name="set", description="Set a custom ping response")
async def set_response(interaction: discord.Interaction, custom_message: str):
    user_id = str(interaction.user.id)
    user_messages[user_id] = custom_message
    save_user_messages()
    logging.info(f"Set custom message for {user_id}: {custom_message}")
    await interaction.response.send_message(f"Your message has been set. Try pinging yourself!", ephemeral=True)

@bot.tree.command(name="ask", description="Ask Gemini AI a question")
async def ask_gemini_cmd(interaction: discord.Interaction, prompt: str):
    try:
        await interaction.response.defer(ephemeral=False)
        response = await query_gemini_sdk(prompt)
        if len(response) > 2000:
            response = response[:2000]
        await interaction.followup.send(response, ephemeral=False)
        logging.info(f"Gemini response sent to {interaction.user} in {interaction.channel}: {response[:50]} ...")
    except Exception as e:
        logging.error(f"Error in ask command: {type(e).__name__}")
        await interaction.response.send_message("Sorry, there was an error processing your request.", ephemeral=True)

@bot.tree.command(name="meow", description="Fetches a Cute Kitty")
async def fetch_cat(interaction: discord.Interaction):
    cat_url = await fetch_cat_image()
    if cat_url:
        await interaction.response.send_message(cat_url, ephemeral=False)
        logging.info(f"Sent a cat image to {interaction.user} in {interaction.channel}: {cat_url}")
    else:
        await interaction.response.send_message("Couldn't fetch a cat image. Try again later!", ephemeral=False)

@bot.tree.command(name="woof", description="Fetches a Loyal Doggy")
async def fetch_dog(interaction: discord.Interaction):
    dog_url = await fetch_dog_image()
    if dog_url:
        await interaction.response.send_message(dog_url, ephemeral=False)
        logging.info(f"Sent a dog image to {interaction.user} in {interaction.channel}: {dog_url}")
    else:
        await interaction.response.send_message("Couldn't fetch a dog image. Try again later!", ephemeral=False)

@bot.tree.command(name="zen", description="Fetches a Zenyatta Quote")
async def fetch_zen(interaction: discord.Interaction):
    zen_url = await fetch_zen_quote()
    zen_emote = discord.utils.get(interaction.guild.emojis, name="zen")
    if zen_url:
        if zen_emote:
            await interaction.response.send_message(str(zen_emote) + " " + zen_url + " " + str(zen_emote), ephemeral=False)
        else:
            await interaction.response.send_message(zen_url, ephemeral=False)
        logging.info(f"Sent a zen quote to {interaction.user} in {interaction.channel}: {zen_url}")
    else:
        await interaction.response.send_message("Couldn't fetch a zen quote. Try again later!", ephemeral=False)

@bot.tree.command(name="emote", description="Make the bot mimic an emote")
async def mimic_emote(interaction: discord.Interaction, emote: str):
    req_emote = discord.utils.get(interaction.guild.emojis, name=emote)
    if req_emote:
        await interaction.response.defer(ephemeral=True)
        webhook = None
        for existing_webhook in await interaction.channel.webhooks():
            if existing_webhook.name == "MimicWebhook":
                webhook = existing_webhook
                break
        if not webhook:
            webhook = await interaction.channel.create_webhook(name="MimicWebhook")
        await webhook.send(
            content=str(req_emote),
            username=interaction.user.display_name,
            avatar_url=interaction.user.display_avatar.url,
        )
        await interaction.delete_original_response()
        return
    await interaction.response.send_message(f"Emote '{emote}' not found in this server.", ephemeral=True)

@bot.tree.command(name="flipcoin", description="Flips a coin for decision making")
async def flip_coin(interaction: discord.Interaction):
    result = random.randint(0,1)
    await interaction.response.send_message("Tails" if result == 0 else "Heads", ephemeral=False)

@bot.tree.command(name="help", description="Show the bot's help menu")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message("""**Hi! I am J4RV1S**

Hey there! 🌟 I'm here to assist you with some fun and useful commands. Take a look at what I can do:

1. **Random Cat Image**
    - Type `/meow` to see a random adorable cat picture.
2. **Random Dog Image**
    - Type `/woof` to fetch a delightful doggy photo.
3. **Yo Momma Joke**
    - Try `yomomma` for a good laugh with a classic "Yo Momma" joke.
4. **Animated Emoji (No Nitro)**
    - Use `/emote` followed by an animated emoji. Example: `/emote agunr`.
5. **Zenyatta**
    - Use `/zen` to listen to what zenyatta says. Experience Tranquility!
6. **Mention Message**
    - Want a message to be showcased when pinged? Set yourself with `/set` command.
7. **AI Chatbot**
    - Start your message with `/ask` for a chat with our AI-powered chatbot.
8. **Help Menu**
    - Type `/help` to display this help message.

Feel free to explore these commands and have fun! If you want to work on this bot maybe because you don't have anything useful to do, Ping Paneer! 🚀""", ephemeral=False)

token = os.getenv("BOT_TOKEN")
bot.run(token)
