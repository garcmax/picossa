import discord
from discord.ext import commands
import requests
import os


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents = intents, command_prefix='!')
openai_token = os.getenv('OPENAI_TOKEN')
picossa_token = os.getenv('PICOSSA_TOKEN')
headers = {"Authorization": "Bearer " + openai_token}

@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user.name}!")

@bot.event
async def on_message(message):
    if message.author.bot == False and bot.user.mentioned_in(message):
        userToReply = message.author
        prompt = message.clean_content.replace('@Picossa', '')
        print(f'{"prompt : "}{"["}{prompt}{"]"}')
        new_data = {"prompt": prompt,"n": 1,"size": "1792x1024","response_format": "url", "model": "dall-e-3", "quality": "hd"}
        post_response = requests.post("https://api.openai.com/v1/images/generations", json=new_data, headers=headers)
        post_response_json = post_response.json()
        if (post_response_json.get("error") == None):
            image = post_response_json["data"][0]["url"]
            revisedPrompt = post_response_json["data"][0]["revised_prompt"]
            response = requests.get(image)
            if response.status_code:
                fp = open('image01.webp', 'wb')
                fp.write(response.content)
                fp.close()
                await message.channel.send(f'{userToReply.mention} : {await translateInFrench(revisedPrompt)}', file=discord.File('image01.webp'))
                return
            await message.channel.send("J'ai que l'url pour cette image : " + post_response_json["data"][0]["url"])
            return
        await message.channel.send("prompt interdit car : [" + post_response_json["error"]["message"] + "]")
        return
    
    await bot.process_commands(message)

bot.run(picossa_token)

def translateInFrench(message):
    body = """{
        "model": "gpt-3.5-turbo",
        "messages": [
        {
            "role": "system",
            "content": "Your only goal is to translate from english to french the messages you'll recceive as input"
        },
        {
            "role": "user",
            "content": {message}
        }
        ]
    }"""
    post_response = requests.post("https://api.openai.com/v1/images/generations", json=body, headers=headers)
    post_response_json = post_response.json()
    if (post_response_json.get("error") == None):
        translatedMessage = post_response_json["choices"][0]["message"]["content"]
    return translatedMessage