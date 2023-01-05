import discord
import asyncio
import json
import os
import uuid
import time
import re
import random
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class SentimentAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> str:
        scores = self.sid.polarity_scores(text)
        if scores['compound'] > 0.5:
            return "_positive"
        elif scores['compound'] < -0.5:
            return "_negative"
        else:
            return "_neutral"

    
intents = discord.Intents.default()
intents.message_content = True

cmd_template = """
convert \
    $INFILE \
    -coalesce \
    -font impact -pointsize 36 -fill white -stroke black -strokewidth 2 \
    -gravity north -annotate +0+0 '$TOPTEXT' \
    -gravity south -annotate +0+0 '$BOTTOMTEXT' \
    $FILENAME
"""

sanitize = r"[^a-zA-Z0-9$ !.,]"
strlen = 25

client = discord.Client(intents=intents)

miku_folder = "mikus"

def break_up(string):
    s = ""
    idx = 1
    for i in string:
        if idx % 25 == 0:
            s += "\n"
        s += i
        idx += 1
    return s

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('miku'):
        if " " not in message.content: return
        text = message.content.split(" ", 1)[1]
        text = re.sub(sanitize, '', text)
        text = text[:150]
        print(text)
        
        ### NLTK HERE ###
        nltk_obj = SentimentAnalyzer()
        categorization = nltk_obj.analyze(text)

        sentiment_folder = miku_folder + "/" + categorization


        if " $ " in text: top, bottom = text.split(" $ ", 1)
        else: top = text; bottom = ""

        top = break_up(top)
        bottom = break_up(bottom)

        cmd_run = cmd_template.replace("$TOPTEXT", top)
        cmd_run = cmd_run.replace("$BOTTOMTEXT", bottom)

        file = random.choice([x for x in os.listdir(sentiment_folder) if os.path.isfile(os.path.join(miku_folder, x))])
        file = f"{miku_folder}/{file}"
        cmd_run = cmd_run.replace("$INFILE", file)
        
        filename = str(uuid.uuid4())[0:4] + str(int(time.time())) + ".gif"
        filename = f"output-gifs/{filename}"
        cmd_run = cmd_run.replace("$FILENAME", filename)

        p = await asyncio.create_subprocess_shell(cmd_run)
        await p.communicate()

        await message.channel.send(file=discord.File(filename))

with open("config.json", 'r') as f:
    config = json.load(f)

client.run(config['token'])
