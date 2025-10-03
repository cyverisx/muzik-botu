import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}

def check_queue(ctx, id):
    if queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def cal(ctx, *, url):
    if not ctx.author.voice:
        await ctx.send("❌ Önce bir ses kanalına katılmalısın!")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)

    ydl_opts = {"format": "bestaudio"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info["url"]

    voice = ctx.guild.voice_client
    source = await discord.FFmpegOpusAudio.from_probe(URL, method="fallback")

    if not voice.is_playing():
        voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))
        await ctx.send(f"🎶 Şimdi çalıyor: **{info['title']}**")
    else:
        guild_id = ctx.message.guild.id
        if guild_id in queues:
            queues[guild_id].append(source)
        else:
            queues[guild_id] = [source]
        await ctx.send(f"✅ Kuyruğa eklendi: **{info['title']}**")

@bot.command()
async def dur(ctx):
    if ctx.voice_client:
        await ctx.voice_client.stop()
        await ctx.send("⏹️ Müzik durduruldu!")

@bot.command()
async def cik(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Kanaldan ayrıldım!")

# TOKENİ BURADAN ÇEKECEK
bot.run(os.getenv("DISCORD_TOKEN"))

