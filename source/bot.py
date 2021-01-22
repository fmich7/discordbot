import json
import discord
from discord.ext import commands
import os
import time

def loadConfigFile():
    with open(f'{os.getcwd()}\config.json', 'r') as file:
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


@client.command(name='clear')
async def removeMessages(ctx, number: int):
    await ctx.channel.purge(limit=(number + 1))


@client.command(name='help')
async def printHelp(ctx, cmd=None):
    embed = discord.Embed(colour=discord.Color.orange())

    embed.set_author(name='Help')

    for command in loadHelpCommands():
        if cmd is None or cmd == command[0]:
            options = ''.join(command[2:])
            embed.add_field(name=command[1], value=options, inline=False)

    await ctx.send(embed=embed)


@client.command(name='połk', pass_context=True)
async def sendMessageToSpecificUser(ctx, user: discord.User, *message):
    global loopTimes
    print(message[0])
    if '[' in message[0] and ']' in message[0]:
        loopTimes = int(message[0][1:-1])
        message = ' '.join(message[1:])
    else:
        message = ' '.join(message)
        loopTimes = 1

    if not message:
        message = '@{}'.format(user.name)

    rightUser = client.get_user(user.id)
    for i in range(loopTimes):
        await rightUser.send(message)
        time.sleep(0.5)


@client.command(pass_context=True)
async def ligusia(ctx, *, message = '[Sad] Wariacie dawaj na serwer bo akurat nam brakuje typka do ligusi flexy/normalki'):
    role = discord.utils.get(ctx.guild.roles, name='KOZAK DO LIGI')
    for member in role.members:
        if str(member.status) == 'online':
            embed = discord.Embed(description=f"```css\nSerwer SAD```", color=discord.Color.orange())
            embed.set_thumbnail(url=f"https://i.pinimg.com/originals/82/ee/cf/82eecf7ecd32a7d9076553a9ca5c65dd.png")
            embed.add_field(name='😎🤙🏿', value=f'**{message}**', inline=True)
            embed.set_footer(text="Jak coś to jest bot")

            await member.send(embed=embed)

@client.command()
async def ping(ctx):
    await ctx.send(f'⏳ Ping Bota: {round(client.latency * 1000)}ms')


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


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.environ.get('TOKEN'))
