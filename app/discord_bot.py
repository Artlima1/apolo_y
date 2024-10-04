import os
import discord
from dotenv import load_dotenv
from assistant import generate_response

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL_ID')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure this is set to True

# Create the client instance with intents
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    

    if message.channel.id == int(CHANNEL):
        response = generate_response(message.content, str(message.channel.id), message.author.global_name)
        for i in range(0, len(response), 2000):
            chunk = response[i:i + 2000]
            await message.channel.send(chunk)

client.run(TOKEN)
