import discord
from discord.ext import commands
import requests
import os


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents = intents, command_prefix=commands.when_mentioned)
openai_token = os.getenv('OPENAI_TOKEN')
picossa_token = os.getenv('PICOSSA_TOKEN')

headers = {"Authorization": "Bearer " + openai_token}

@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user.name}!")

@bot.event
async def on_message(message):
    if message.author.bot == False and bot.user.mentioned_in(message):
        prompt = message.clean_content.replace('@Picossa', '')
        new_data = {"prompt": prompt,"n": 1,"size": "512x512","response_format": "url"}
        post_response = requests.post("https://api.openai.com/v1/images/generations", json=new_data, headers=headers)
        post_response_json = post_response.json()
        if (post_response_json.get("error") == None):
            image = post_response_json["data"][0]["url"]
            response = requests.get(image)
            if response.status_code:
                fp = open('image01.webp', 'wb')
                fp.write(response.content)
                fp.close()
                await message.channel.send(file=discord.File('image01.webp'))
                return
            await message.channel.send("J'ai que l'url pour cette image : " + post_response_json["data"][0]["url"])
            return
        await message.channel.send("prompt interdit car : [" + post_response_json["error"]["message"] + "]")
        
bot.run(picossa_token)
