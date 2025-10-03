import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# yt-dlp ayarları
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',  # isimle arama yapabilsin
    'quiet': True
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yapıldı!')

# Şarkı çalma
@bot.command(name="çal")
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("🎤 Önce bir ses kanalına gir!")
        return

    channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await channel.connect()

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(YDL_OPTIONS).extract_info(search, download=False))

    if "entries" in data:  # Arama sonucu dönerse ilkini al
        data = data["entries"][0]

    url2 = data["url"]
    title = data.get("title", "Bilinmeyen Müzik")

    voice_client.stop()
    voice_client.play(discord.FFmpegOpusAudio(url2, **FFMPEG_OPTIONS))

    await ctx.send(f"🎶 Şimdi çalıyor: **{title}**\n🔗 {data.get('webpage_url', search)}")

# Şarkıyı durdur
@bot.command(name="durdur")
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏹️ Müzik durduruldu!")
    else:
        await c
