# Built-in imports
import os
import json
from dotenv import load_dotenv

# Local imports
import utils

# Third-party imports
import discord

load_dotenv()

# Necessary global variables
SESSION_ID = -1
ENABLE_VOICE_RESPONSE = os.getenv("ENABLE_VOICE_RESPONSE")
CONVAI_CHARACTER_ID = os.getenv("CONVAI_CHARACTER_ID")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Send messages
async def sendMessage(message, user_message, is_private):
    global SESSION_ID
    global ENABLE_VOICE_RESPONSE
    global CONVAI_CHARACTER_ID

    try:
        response = utils.getResponse(
            userQuery=message,
            characterID=CONVAI_CHARACTER_ID,
            sessionID=SESSION_ID,
            voiceResponse=ENABLE_VOICE_RESPONSE
        )

        # Updating SESSION_ID with new value for new chat sessions after it has been set to -1
        SESSION_ID = response["sessionID"]

        # Replying with the required text receive from the api call
        await message.author.send(response["text"]) if is_private else await message.channel.send(response["text"])

    except Exception as e:
        print(e)

def runDiscordBot():
    client = discord.Client(
        intents=discord.Intents.all()
    )

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        # If the user message contains a '@' in front of the text, it becomes a private message
        if user_message[0] == '@':
            user_message = user_message[1:]  # [1:] Removes the '@'
            await sendMessage(message, user_message, is_private=True)
        else:
            await sendMessage(message, user_message, is_private=False)

    # Remember to run your bot with your personal TOKEN
    client.run(DISCORD_BOT_TOKEN)