import discord
from discord.ext import commands
import pafy
import os
import time

token = "token"
client = commands.Bot(command_prefix = "-")
audio_queue = []

#works
@client.event
async def on_ready():
    print("Bot Online!")

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

    audio_isthere = os.path.isfile("audio.webm")
    if audio_isthere:
        os.remove("audio.webm")        

    #downloads the url audio in WEBM format
    video = pafy.new(audio_queue[0])
    audio_queue.pop(0)
    audio = video.getbestaudio(preftype="webm",ftypestrict=True)
    audio.download()

    for file in os.listdir("./"):
        if file.endswith(".webm"):
            print("Playing:")
            print(file)
            print()
            os.rename(file, "audio.webm")
    
    audio_source = discord.FFmpegPCMAudio("audio.webm")
    voice.play(audio_source)

@client.command()
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing() or voice.is_paused():
        if len(audio_queue) != 0:
            voice.stop()
            time.sleep(1)
            os.remove("audio.webm")

            video = pafy.new(audio_queue[0])
            audio_queue.pop(0)
            audio = video.getbestaudio(preftype="webm",ftypestrict=True)
            audio.download()

            for file in os.listdir("./"):
                if file.endswith(".webm"):
                    print("Playing:")
                    print(file)
                    print()
                    os.rename(file, "audio.webm")
    
            audio_source = discord.FFmpegPCMAudio("audio.webm")
            voice.play("audio.webm")
        else:
            await ctx.send("No Songs In Queue.")
            return

@client.command()
async def next(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    print("Current Queue:")
    print(audio_queue)
    print()

    if len(audio_queue) == 0:
        await ctx.send("No Songs In Queue.")
        return
    if voice.is_playing() or voice.is_paused():
        await ctx.send("Please 'skip' the current audio.")
        return
    
    audio_isthere = os.path.isfile("audio.webm")
    if audio_isthere:
        os.remove("audio.webm")

    video = pafy.new(audio_queue[0])
    audio_queue.pop(0)
    audio = video.getbestaudio(preftype="webm",ftypestrict=True)
    audio.download()

    for file in os.listdir("./"):
        if file.endswith(".webm"):
            print("Playing:")
            print(file)
            print()
            os.rename(file, "audio.webm")
    
    audio_source = discord.FFmpegPCMAudio("audio.webm")
    voice.play(audio_source)
    
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
    time.sleep(1)

#works
@client.command()
async def shutdown(ctx):
    client.close()
    time.sleep(1)
    quit()

client.run(token)
