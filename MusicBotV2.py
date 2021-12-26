import discord
from discord.ext import commands
import youtube_dl

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
                  'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio'}
#36768768 for permissions

token = "token"
client = commands.Bot(command_prefix = "-")

audio_queue = []

#works
@client.event
async def on_ready():
    print("Bot Online!")

#works
async def Stream_Audio(voice, ctx):
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        url = audio_queue[0]
        audio_queue.pop(0)
        print("Playing:")
        print(url)
        audio_info = ydl.extract_info(url, download=False)
        stream_url = audio_info['formats'][0]['url']
        audio_source = await discord.FFmpegOpusAudio.from_probe(stream_url,
        **FFMPEG_OPTIONS)
        voice.play(audio_source)
        message = "Currently Playing: " + url
        await ctx.send(message)
        print()

#works
@client.command(aliases=['paly', 'queue'])
async def play(ctx, url : str):

    if ctx.author.voice:
        voice_client_test = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice_client_test == None:
            voice_channel = ctx.message.author.voice.channel
            await voice_channel.connect()
    else:
        await ctx.send("Please join a Voice Channel.")
        return

    audio_queue.append(url)
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing() or voice.is_paused():
        await ctx.send("To play inputed audio 'skip' the current audio.")
        return        

    await Stream_Audio(voice, ctx)

#works
@client.command(aliases=['next'])
async def skip(ctx):
    print("Current Queue:")
    print(audio_queue)
    print()

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if len(audio_queue) == 0:
        await ctx.send("No Song In Queue.")
        return

    if voice.is_playing() or voice.is_paused():
        voice.stop()
        await Stream_Audio(voice, ctx)
        return

    await Stream_Audio(voice, ctx)
    
#works
@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice != None:
        await voice.disconnect()
    else:
        await ctx.send("Not in any voice channel.")

#works
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No audio is playing.")

#works
@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Audio is playing.")

#works
@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

#works
@client.command()
async def shutdown(ctx):
    await client.close()
    quit(0)

client.run(token)
