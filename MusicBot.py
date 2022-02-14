import discord
from discord.ext import commands
import youtube_dl

class MusicBot(commands.Cog):
    #Initializes this client
    def __init__(self, client):
        #Options for formating and retrieving music data from youtube
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
                  'options': '-vn'}
        self.YDL_OPTIONS = {'format': 'bestaudio'}
        #Queue of URLs as FFmpeg audio
        self.audio_queue = []
        #Queue of URLs as strings for status
        self.url_queue = []

        self.client = client        

    #Adds This Music Bot Class as a "collection of commands" to the given client
    def setup(client):
        client.add_cog(MusicBot(client))

    #Joins or Moves to voice channel of caller
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Please join a Voice Channel.")
            return
        author_voice_channel = ctx.message.author.voice.channel
        if ctx.voice_client is None:
            await author_voice_channel.connect()
        else:
            await ctx.voice_client.move_to(author_voice_channel)

    #Removes bot from a voice channel
    @commands.command()
    async def leave(self, ctx):
        voice = ctx.voice_client
        if voice != None:
            await voice.disconnect()
        else:
            await ctx.send("Not in any voice channel.")

    #plays the next song in queue and if called from the 'after' 
    #lambda function then it will update the current playing url string.
    def play_next(self, ctx, removeUrlFromQueue):
        voice  = ctx.voice_client

        if(removeUrlFromQueue and (len(self.url_queue) > 0)):
            self.url_queue.pop(0)

        if (len(self.audio_queue) <= 0):
            return
        audio_source = self.audio_queue[0]
        self.audio_queue.pop(0)

        voice.play(audio_source, after=lambda e: self.play_next(ctx, True))

    #Adds FFmpeg audio to the audio_queue
    async def enqueue(self, url):
        self.url_queue.append(url)
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            print("Queueing: " + url + '\n')
            audio_info = ydl.extract_info(url, download=False)
            stream_url = audio_info['formats'][0]['url']
            audio_source = await discord.FFmpegOpusAudio.from_probe(stream_url, **self.FFMPEG_OPTIONS)
            self.audio_queue.append(audio_source)

    @commands.command(aliases=['paly', 'queue', 'p', 'q'])
    async def play(self, ctx, url):
        voice  = ctx.voice_client

        #If Bot not in a channel 
        if voice == None:
            await self.join(ctx)
            voice  = ctx.voice_client
            #If caller not in a channel
            if voice == None:
                return

        await self.enqueue(url)
        #Print to Channel (Make this a bool from enqueue)
        await ctx.send("Queued Succefully.")

        if voice.is_playing() or voice.is_paused():
            await ctx.send("To play inputed audio 'skip' the current audio.")
            return

        self.play_next(ctx, False)

    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        if len(self.audio_queue) <= 0:
            await ctx.send("No Song In Queue.")
            return

        ctx.voice_client.stop()

    #Prints Current Song Playing If Any
    @commands.command()
    async def status(self, ctx):
        if (len(self.url_queue) > 0):
            message = "Currently Playing: " + self.url_queue[0]
            await ctx.send(message)
        else:
            message = "No Songs In Queue."
            await ctx.send(message)

    @commands.command()
    async def pause(self, ctx):
        voice = ctx.voice_client
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("No audio is playing.")

    @commands.command()
    async def resume(self, ctx):
        voice = ctx.voice_client
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("Audio is playing or queue is empty.")

    #Stops voice and clears queue
    @commands.command()
    async def stop(self, ctx):
        self.audio_queue.clear()
        self.url_queue.clear()
        voice = ctx.voice_client
        voice.stop()