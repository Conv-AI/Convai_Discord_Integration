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
ENABLE_VOICE_RESPONSE = os.getenv("ENABLE_VOICE_RESPONSE")
CONVAI_CHARACTER_ID = os.getenv("CONVAI_CHARACTER_ID")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

ALLOWED_CHANNELS = os.getenv("ALLOWED_CHANNELS").split(",") if os.getenv("ALLOWED_CHANNELS") else None
SESSION_IDS = {}    # Maintaining separate sessions of conversation for separate channels and private messages

# Send messages
async def sendMessage(message, user_message, is_private):
    global SESSION_IDS
    global ENABLE_VOICE_RESPONSE
    global CONVAI_CHARACTER_ID

    try:
        # Check if the channel is listed in SESSION_IDS to maintain context of conversation
        if message.channel.id not in SESSION_IDS.keys():
                SESSION_IDS[message.channel.id] = "-1"
        # Get the session-id
        sessionID = SESSION_IDS[message.channel.id]

        response = utils.getResponse(
            userQuery=user_message,
            characterID=CONVAI_CHARACTER_ID,
            sessionID= sessionID,
            voiceResponse=ENABLE_VOICE_RESPONSE
        )

        # Updating SESSION_ID with new value for new chat sessions after it has been set to -1
        if SESSION_IDS[message.channel.id] == "-1":
            SESSION_IDS[message.channel.id] = response["sessionID"]

        # Replying with the required text receive from the api call
        await message.author.send(response["text"]) if is_private else await message.channel.send(response["text"])

    except Exception as e:
        print(e)

def runDiscordBot():
    global ALLOWED_CHANNELS
    global SESSION_IDS

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

        # Restricting the bot to speak only in a specific channel and DM channels
        if type(message.channel) != discord.DMChannel and ALLOWED_CHANNELS and message.channel.name not in ALLOWED_CHANNELS:
            return

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        #If the message is a direct message, you do not need any prefix to talk with the chatbot
        if type(message.channel) == discord.DMChannel:
            if user_message.startswith('/reset <@{}>'.format(client.user.id)):
                SESSION_IDS[message.channel.id] = "-1"
                await message.channel.send("I just had a great sleep. Feeling refreshed and better.")

            else:
                user_message = user_message.strip()
                await sendMessage(message, user_message, is_private=True)

        else:
            # If the user message is from an ALLOWED_CHANNELS and contains a '@{chatbot-name}'
            # in front of the text, then only responsd to the user
            if user_message.startswith('<@{}>'.format(client.user.id)):
                user_message = user_message.split('<@{}>'.format(client.user.id))[1].strip()  # Consider the text after mentions
                await sendMessage(message, user_message, is_private=False)

            # If the user message contains a '/private @{chatbot-name}' in front of the text,
            # shift the conversation to private channel with the user
            elif user_message.startswith('/private <@{}>'.format(client.user.id)):
                # Advisable to not use this code right now. Needs extensive testing.
                user_message = user_message.split('/private <@{}>'.format(client.user.id))[1].strip()  # Consider the text after mentions
                await sendMessage(message, user_message, is_private=True)

            # If the user message contains a '/reset @{chatbot-name}' in front of the text,
            # start a new session of conversation with the chatbot
            elif user_message.startswith('/reset <@{}>'.format(client.user.id)):
                SESSION_IDS[message.channel.id] = "-1"
                await message.channel.send("I just had a great sleep. Feeling refreshed and better.")

            else:
                # Do not reply to messages you are not mentioned
                return

    # Remember to run your bot with your personal TOKEN
    client.run(DISCORD_BOT_TOKEN)