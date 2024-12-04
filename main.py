import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")


load_dotenv()  
client = Client(intents=intents)
client.run(os.environ.get('TOKEN'))