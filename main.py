import discord
from discord.ext import commands
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

    addToVoice()

    try:
        url = search
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        
        song_url = data['url']
        
        player = discord.FFmpegOpusAudio(song_url, **ffmpeg_options)
        voice_clients[interaction.guild.id].play(player)

    except Exception as e:
        print(f"Playback error: {e}")
    
@client.tree.command(name='search', description='search for a youtube video', guild=GUILD_ID)
async def search(interaction: discord.Interaction, search: str):
    
    addToVoice()

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{search}", download=False))

        if 'entries' in data and len(data['entries']) > 0:
            first_result = data['entries'][0]
            url = first_result['url']  
            player = discord.FFmpegOpusAudio(url, **ffmpeg_options)
            voice_clients[interaction.guild.id].play(player)
        else:
            await interaction.response.send_message("No results found.")
    except Exception as e:
        print(f"Error: {e}")

@client.tree.command(name='stop', description='turn off current song', guild=GUILD_ID)
async def pause(interaction: discord.Interaction):
    try:
        voice_client = voice_clients.get(interaction.guild.id)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Paused the current song")
    except Exception as e:
        print(f"Error: {e}")

@client.tree.command(name='resume', description='resume the current song', guild=GUILD_ID)
async def resume(interaction: discord.Interaction):
    try:
        voice_client = voice_clients.get(interaction.guild.id)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Unpaused the music")
    except Exception as e:
        print(f"Error: {e}")

load_dotenv()
client.run(os.environ.get('TOKEN'))

async def addToVoice(interaction: discord.Interaction):
    try:
        if interaction.guild.id not in voice_clients:
            voice_client = await interaction.user.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

    except Exception as e:
        print(f"Connection error: {e}")
        return
