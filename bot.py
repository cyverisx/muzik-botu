import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Youtube-dl ayarları
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',  # arama özelliği açık
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Bot hazır olduğunda
@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı.")

# Basit ping komutu
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Ses kanalına katıl
@bot.command(name="katıl")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"🔊 {channel} kanalına katıldım!")
    else:
        await ctx.send("Önce bir ses kanalına gir!")

# Ses kanalından ayrıl
@bot.command(name="ayrıl")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("❌ Kanaldan ayrıldım.")
    else:
        await ctx.send("Ben zaten bir ses kanalında değilim.")

# Müzik çal (hem isim hem link çalışır)
@bot.command(name="çal")
async def play(ctx, *, search: str):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            return await ctx.send("Önce bir ses kanalına gir!")

    vc = ctx.voice_client

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))

    if "entries" in data:  # Eğer arama yapıldıysa
        data = data["entries"][0]

    url2 = data["url"]
    vc.stop()
    vc.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options))
    await ctx.send(f"🎶 Şimdi oynatılıyor: **{data['title']}**")

# Müziği durdur
@bot.command(name="durdur")
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹ Müzik durduruldu.")
    else:
        await ctx.send("Şu anda çalan bir şey yok.")

# Token Github Secrets'ten alınacak
bot.run(os.getenv("DISCORD_TOKEN"))
