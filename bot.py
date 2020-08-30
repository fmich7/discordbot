import json
import discord
from discord.ext import commands
import os


def loadConfigFile():
    with open('config.json', 'r') as file:
        return json.load(file)


def loadHelpCommands():
    with open('helpcommands.txt', 'r', encoding='utf8') as file:
        arr = []
        for line in file:
            if line.startswith('?'):
                arr.append([line])
            else:
                arr[-1].append(line)
        return arr


client = commands.Bot(command_prefix=loadConfigFile()['prefix'])


@client.command(name='clear')
async def removeMessages(ctx, number: int):
    await ctx.channel.purge(limit=(number + 1))


@client.command()
async def printHelp(ctx, cmd=None):
    embed = discord.Embed(colour=discord.Color.orange())

    embed.set_author(name='Help')

    for command in loadHelpCommands():
        if cmd is None or cmd == command[0]:
            options = ''.join(command[2:])
            embed.add_field(name=command[1], value=options, inline=False)

    await ctx.send(embed=embed)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(" 👿🤘 Dis to ziom :)"))
    print("Bot is ready")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('❌ Został podany zły argument polecenia')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('❌ Coś poszło nie tak')


@client.command()
async def ping(ctx):
    await ctx.send(f'⏳ Ping Bota: {round(client.latency * 1000)}ms')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.remove_command('help')
client.run(os.environ.get('TOKEN'))