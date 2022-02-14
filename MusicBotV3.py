import discord
from discord.ext import commands
from MusicBot import MusicBot    

if __name__ == '__main__':
    #36768768 for bot permissions
    token = "token"

    #Setup client with MusicBot class using a "collection of commands"
    cogs = [MusicBot]
    client = commands.Bot(command_prefix = "-")
    for i in range(len(cogs)):
        cogs[i].setup(client)

    @client.event
    async def on_ready():
        print("Bot Online!")

    @client.command()
    async def shutdown(ctx):
        await client.close()
        quit(0)
    
    #Run client with token and the given commands
    client.run(token)