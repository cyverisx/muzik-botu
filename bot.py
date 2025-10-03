import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import os   # 🔹 Eksik olan eklendi

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# yt-dlp ayarları
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'extract_flat': False,
}

ffmpeg_options = {
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
    else:
        await ctx.send("Önce bir ses kanalına gir!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Zaten herhangi bir kanalda değilim.")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.voice_client:
        await ctx.invoke(join)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search, download=False)
            if "entries" in info:  # ytsearch dönerse
                info = info["entries"][0]
            url = info["url"]
        except Exception as e:
            await ctx.send(f"Hata oluştu: {e}")
            return

    source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
    ctx.voice_client.stop()
    ctx.voice_client.play(source)
    await ctx.send(f"🎶 Şimdi çalıyor: **{info.get('title', 'Bilinmeyen')}**")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹ Çalma durduruldu.")
    else:
        await ctx.send("Şu anda müzik çalmıyorum.")

bot.run(os.getenv("DISCORD_TOKEN"))
