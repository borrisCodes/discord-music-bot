import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
from dotenv import load_dotenv

GUILD_ID = discord.Object(id=1171584985346617474)

class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands to guild {GUILD_ID.id}")
        except Exception as e:
            print(f"Error syncing commands: {e}")

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)


voice_clients = {}
queue ={}
yt_dl_options = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

os.environ["PATH"] = "/home/cameron/ffmpeg:" + os.environ["PATH"]

ffmpeg_options = {
    'options': '-vn'
}

@client.tree.command(name='play', description='play a song from a link', guild=GUILD_ID)
async def youTube(interaction: discord.Interaction, link: str):

    try:
        if interaction.guild.id not in voice_clients:
            voice_client = await interaction.user.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

    except Exception as e:
        print(f"Connection error: {e}")
        return

    try:
        await interaction.response.defer()
        url = link
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        
        song = {'url': data['url'], 'title': data['title']}
        add_to_queue(interaction.guild.id, song)

        if not voice_clients[interaction.guild.id].is_playing():
            await play_next_song(interaction.guild.id)

        await interaction.followup.send(f"Added to queue: {song['title']}")

    except Exception as e:
        print(f"Playback error: {e}")
    
@client.tree.command(name='search', description='search for a youtube video', guild=GUILD_ID)
async def search(interaction: discord.Interaction, search: str):
    try:
        if interaction.guild.id not in voice_clients:
            voice_client = await interaction.user.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

    except Exception as e:
        print(f"Connection error: {e}")
        return

    try:
        await interaction.response.defer()
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{search}", download=False))

        if 'entries' in data and len(data['entries']) > 0:
            first_result = data['entries'][0]
            song = {'url': first_result['url'], 'title': first_result['title']}
            add_to_queue(interaction.guild.id, song)

            if not voice_clients[interaction.guild.id].is_playing():
                await play_next_song(interaction.guild.id)
            
            await interaction.followup.send(f"Added to queue: {song['title']}")
        else:
            await interaction.response.send_message("No results found.")
    except Exception as e:
        print(f"Playback error: {e}")

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

@client.tree.command(name='skip', description='skip the current song', guild=GUILD_ID)
async def skip(interaction:discord.Interaction):
    voice_client = voice_clients.get(interaction.guild.id)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("Skipped the current song")
    else:
        await interaction.response.send_message("No song is currently playing")

def add_to_queue(GUILD_ID, song):
    if GUILD_ID not in queue:
        queue[GUILD_ID] = []
    queue[GUILD_ID].append(song)

async def play_next_song(GUILD_ID):
    if GUILD_ID in queue and queue[GUILD_ID]:
        song = queue[GUILD_ID].pop(0)
        voice_client = voice_clients[GUILD_ID]
    
        try:
            player = discord.FFmpegOpusAudio(song['url'], **ffmpeg_options)
            voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(GUILD_ID), client.loop))
        except Exception as e:
            await play_next_song(GUILD_ID)

load_dotenv()
client.run(os.environ.get('TOKEN'))