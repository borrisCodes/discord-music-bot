import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
import os
from dotenv import load_dotenv

class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        try:
            guild = discord.Object(id=1171584985346617474)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")
        except Exception as e:
            print(f"Error syncing commands: {e}")

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)

GUILD_ID = discord.Object(id=1171584985346617474)
voice_clients = {}
yt_dl_options = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

os.environ["PATH"] = "/home/cameron/ffmpeg:" + os.environ["PATH"]

ffmpeg_options = {
    'options': '-vn'
}

@client.tree.command(name='play', description='search for music', guild=GUILD_ID)
async def youTube(interaction: discord.Interaction, search: str):
    try:
        if interaction.guild.id not in voice_clients:
            voice_client = await interaction.user.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

    except Exception as e:
        print(f"Connection error: {e}")
        return

    try:
        url = search
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        print(f"Extracted data: {data}")
        
        song_url = data['url']
        print(f"Playing URL: {song_url}")
        
        player = discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
        voice_clients[interaction.guild.id].play(player)

    except Exception as e:
        print(f"Playback error: {e}")


load_dotenv()
client.run(os.environ.get('TOKEN'))
