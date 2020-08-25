import json
import discord
from discord.ext import commands
import os
import io


def loadConfigFile():
    with io.open('config.json', 'r') as file:
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
client.remove_command('help')


@client.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=(amount + 1))


@client.command()
async def help(ctx):
    embed = discord.Embed(colour=discord.Color.orange())

    embed.set_author(name='Help')

    commandsList = loadHelpCommands()
    for i in range(len(commandsList)):
        tempstr = ''.join(commandsList[i][2:])
        embed.add_field(name=commandsList[i][1], value=tempstr, inline=False)

    await ctx.send(embed=embed)


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(" 👿🤘 Dis to ziom :)"))
    print("Bot is ready")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('❌ Został podany zły argument komendy')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('❌ Coś poszło nie tak')


@client.command()
async def ping(ctx):
    await ctx.send(f'⏳ Ping bota: {round(client.latency * 1000)}ms')

client.run(loadConfigFile()['TOKEN'])