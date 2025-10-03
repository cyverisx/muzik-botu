import discord
from discord.ext import commands
import youtube_dl
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}

def check_queue(ctx, id):
    if id in queues and queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        voice.play(source, after=lambda x=None: check_queue(ctx, id))

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

    ytdl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
    }

    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **{'options': '-vn'})

        voice = ctx.guild.voice_client
        if not voice.is_playing():
            voice.play(source, after=lambda x=None: check_queue(ctx, ctx.guild.id))
            await ctx.send(f"🎶 Şimdi çalıyor: **{info['title']}**")
        else:
            guild_id = ctx.guild.id
            if guild_id in queues:
                queues[guild_id].append(source)
            else:
                queues[guild_id] = [source]
            await ctx.send(f"✅ Kuyruğa eklendi: **{info['title']}**")

@bot.command()
async def dur(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹ Müzik durduruldu!")

@bot.command()
async def cık(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Kanaldan ayrıldım!")

# TOKEN
bot.run(os.getenv("DISCORD_TOKEN"))
