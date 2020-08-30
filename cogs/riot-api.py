import discord
import json
import requests
import datetime
from bot import printHelp
from discord.ext import commands

champions = {266: "Aatrox", 103: "Ahri", 84: "Akali", 12: "Alistar", 32: "Amumu", 34: "Anivia", 1: "Annie",
             523: "Aphelios", 22: "Ashe", 136: "AurelionSol", 268: "Azir", 432: "Bard", 53: "Blitzcrank", 63: "Brand",
             201: "Braum", 51: "Caitlyn", 164: "Camille", 69: "Cassiopeia", 31: "Chogath", 42: "Corki", 122: "Darius",
             131: "Diana", 119: "Draven", 36: "DrMundo", 245: "Ekko", 60: "Elise", 28: "Evelynn", 81: "Ezreal",
             9: "Fiddlesticks", 114: "Fiora", 105: "Fizz", 3: "Galio", 41: "Gangplank", 86: "Garen", 150: "Gnar",
             79: "Gragas", 104: "Graves", 120: "Hecarim", 74: "Heimerdinger", 420: "Illaoi", 39: "Irelia", 427: "Ivern",
             40: "Janna", 59: "JarvanIV", 24: "Jax", 126: "Jayce", 202: "Jhin", 222: "Jinx", 145: "Kaisa",
             429: "Kalista", 43: "Karma", 30: "Karthus", 38: "Kassadin", 55: "Katarina", 10: "Kayle", 141: "Kayn",
             85: "Kennen", 121: "Khazix", 203: "Kindred", 240: "Kled", 96: "KogMaw", 7: "Leblanc", 64: "LeeSin",
             89: "Leona", 127: "Lissandra", 236: "Lucian", 117: "Lulu", 99: "Lux", 54: "Malphite", 90: "Malzahar",
             57: "Maokai", 11: "MasterYi", 21: "MissFortune", 62: "MonkeyKing", 82: "Mordekaiser", 25: "Morgana",
             267: "Nami", 75: "Nasus", 111: "Nautilus", 518: "Neeko", 76: "Nidalee", 56: "Nocturne", 20: "Nunu",
             2: "Olaf", 61: "Orianna", 516: "Ornn", 80: "Pantheon", 78: "Poppy", 555: "Pyke", 246: "Qiyana",
             133: "Quinn", 497: "Rakan", 33: "Rammus", 421: "RekSai", 58: "Renekton", 107: "Rengar", 92: "Riven",
             68: "Rumble", 13: "Ryze", 113: "Sejuani", 235: "Senna", 875: "Sett", 35: "Shaco", 98: "Shen",
             102: "Shyvana", 27: "Singed", 14: "Sion", 15: "Sivir", 72: "Skarner", 37: "Sona", 16: "Soraka",
             50: "Swain", 517: "Sylas", 134: "Syndra", 223: "TahmKench", 163: "Taliyah", 91: "Talon", 44: "Taric",
             17: "Teemo", 412: "Thresh", 18: "Tristana", 48: "Trundle", 23: "Tryndamere", 4: "TwistedFate",
             29: "Twitch", 77: "Udyr", 6: "Urgot", 110: "Varus", 67: "Vayne", 45: "Veigar", 161: "Velkoz", 254: "Vi",
             112: "Viktor", 8: "Vladimir", 106: "Volibear", 19: "Warwick", 498: "Xayah", 101: "Xerath", 5: "XinZhao",
             157: "Yasuo", 83: "Yorick", 350: "Yuumi", 154: "Zac", 238: "Zed", 115: "Ziggs", 26: "Zilean", 142: "Zoe",
             143: "Zyra"}

region = "eun1"

summonerByNamePath = "summoner/v4/summoners/by-name"
matchesByAccountPath = "match/v4/matchlists/by-account"
activeGamesBySummonerPath = "spectator/v4/active-games/by-summoner"
maestriesBySummonerPath = "champion-mastery/v4/champion-masteries/by-summoner"
rankedBySummonerPath = "league/v4/entries/by-summoner"
matchByIdPath = 'match/v4/matches'

class Player:
    def __init__(self, name: str):

        playerData = getData(summonerByNamePath, name)

        self.summonerId = playerData['id']
        self.accountId = playerData['accountId']
        self.nick = playerData['name']
        self.profileIconId = playerData['profileIconId']
        self.level = playerData['summonerLevel']
        self.maestry = self.createMaestryList()
        self.ranked = self.createRankedList()
        self.currentChampionId = None

    # Zbiera informacje na temat punktów maestrii danego gracza
    def createMaestryList(self):
        maestries = getData(maestriesBySummonerPath, self.summonerId)[:3]
        l = []
        for maestry in maestries:
            l.append(
                f' {champions.get(maestry["championId"])} [{maestry["championLevel"]}] {"{:,}".format(maestry["championPoints"]).replace(",", " ")},')
        return l

    # zbiera informacje na temat rozegranych matchy
    def createMatchList(self, start=0, end=1):

        match_list = getData(matchesByAccountPath, self.accountId)
        match_history = list()

        def userDataFromMatch(matchData):
            dataBase = list()
            nicks = [name['player']['summonerName'] for name in matchData['participantIdentities']]
            for i in range(len(nicks)):
                participantInfo = matchData['participants'][i]

                nick = nicks[i]
                minionsKilled = participantInfo['stats']['totalMinionsKilled']
                damageDealt = participantInfo['stats']['totalDamageDealtToChampions']
                winOrNo = participantInfo['stats']['win']
                stats = f'{participantInfo["stats"]["kills"]}/{participantInfo["stats"]["deaths"]}/{participantInfo["stats"]["assists"]}'
                championId = participantInfo['championId']
                # self.rank = None
                # self.level = None
                dataBase.append({'nick': nick, 'minionsKilled': minionsKilled,
                                 'damageDealt': damageDealt, 'stats': stats, 'championId': championId,
                                 'winOrNo': winOrNo})
            return dataBase

        for i in range(start, end):
            match = getData(matchByIdPath, match_list['matches'][i]['gameId'])
            matchData = {'users': userDataFromMatch(match),
                         'matchLength': str(datetime.timedelta(seconds=match['gameDuration']))[2:]}
            match_history.append(matchData)

        return match_history

    def createRankedList(self):
        c_dataranked = getData(rankedBySummonerPath, self.summonerId)
        l = []
        for i in range(len(c_dataranked)):
            dict = {'RANKED_FLEX_SR': 1, 'RANKED_SOLO_5x5': 0}

            try:
                promo = f'[{c_dataranked[i]["miniSeries"]["wins"]}/{len(c_dataranked[i]["miniSeries"]["progress"])}]'
            except:
                promo = ''

            l.append(
                f'{dict.get(c_dataranked[i]["queueType"])}{c_dataranked[i]["tier"]} {c_dataranked[i]["rank"]} {promo}  '
                f'{c_dataranked[i]["leaguePoints"]}/100p\n'
                f'     W/L: {c_dataranked[i]["wins"]}/{c_dataranked[i]["losses"]}      '
                f'WR: {int((c_dataranked[i]["wins"] / (c_dataranked[i]["losses"] + c_dataranked[i]["wins"]) * 100) + 0.5)}%')
        while len(l) < 2:
            l.append("NNie gra tych rankedów :)")
        return sorted(l, key=str.lower)


# zbiera dane z bieżącej gry, dodać exception
def liveMatch(name):
    c_currentmatch = getData(activeGamesBySummonerPath, getData(summonerByNamePath, name)['id'])
    currentMatchPlayers = []
    currentMatchPlayersChampionsId = []
    for i in range(10):
        currentMatchPlayers.append(Player(c_currentmatch['participants'][i]['summonerName']))
        currentMatchPlayersChampionsId.append(c_currentmatch['participants'][i]['championId'])
    return {'names': currentMatchPlayers, 'champId': currentMatchPlayersChampionsId}


class Riot(commands.Cog):

    def __init__(self, client):
        self.client = client

    # function updates riot api key
    @commands.command()
    async def r(self, ctx, *args):
        # subcommands = {"key": handleKey, "link": handleLink}
        # subcommands[args[0].lower()]()
        if not args:
            await printHelp(ctx, "?r?\n")
        elif args[0].lower() == "key":
            # ten if sprawdza czy klucz jest ważny
            if len(args) == 1:
                deltatime = datetime.datetime.today() - datetime.datetime.strptime(getExpirationDate(),
                                                                                   '%Y-%m-%d %H:%M:%S.%f')
                if deltatime < datetime.timedelta(hours=24):
                    displayTimeRemaining = str(datetime.timedelta(hours=24) - deltatime).split(".")[0]
                    await ctx.send(f'🆗 Klucz jest nadal aktualny przez ⏳ {displayTimeRemaining} [{getApiKey()}]')
                else:
                    await ctx.send(f'❌ Wygeneruj nowy klucz [https://developer.riotgames.com/]')
            # zapisuje klucz i date do configu
            else:
                with open('config.json', 'r+') as file:
                    data = json.loads(file.read())
                    data['riot-key'] = args[1]
                    data['expiration_date'] = str(datetime.datetime.today())
                    file.truncate(0)
                    file.seek(0)
                    json.dump(data, file)

                await ctx.send(f'✍ Zapisywanie nowego klucza: {args[1]}')
        elif args[0].lower() == "link":
            await ctx.send('🔗 Link do api riotu: https://developer.riotgames.com/')
        else:
            await ctx.send('❌ Coś poszło nie tak')

    # wywołuje inne funkcje na temat live matcha
    @commands.command()
    async def match(self, ctx, name='kubabmw1'):

        _summoners = liveMatch(name)

        await self.printTeamInfo(ctx, 0x25aaf1, [_summoners['names'][0:5], _summoners['champId'][0:5]])
        await self.printTeamInfo(ctx, 0xe71212, [_summoners['names'][5:10], _summoners['champId'][5:10]])

    async def printTeamInfo(self, ctx, color, summoners):
        for i in range(len(summoners[0])):
            embed = discord.Embed(title=f'{summoners[0][i].nick}',
                                  description=f"```Level: {summoners[0][i].level}```", color=color)
            embed.set_thumbnail(
                url=f"https://ddragon.leagueoflegends.com/cdn/10.14.1/img/champion/{champions.get(summoners[1][i])}.png")
            embed.add_field(name=f"⚔ Ranked solo/duo:", value=f'{summoners[0][i].ranked[0][1:]}',
                            inline=True)
            embed.add_field(name="🛡️ Ranked flex: ", value=f'{summoners[0][i].ranked[1][1:]}', inline=True)
            embed.add_field(name="🧒 Champion maestry:", value=f'{"".join(summoners[0][i].maestry)[:-1]}',
                            inline=False)

            await ctx.send(embed=embed)

    # wypisuje mecze na chacie na podstawie danych z innej funkcji
    async def writeMatchesInChat(self, ctx, data, name):
        print(data)
        for i in range(len(data)):

            targetPlayerIndex = 0
            for x in range(len(data[i]["users"])):
                if data[i]["users"][x]['nick'] == name:
                    targetPlayerIndex = x

            targetPlayer = data[i]["users"][targetPlayerIndex]

            winOrNo = {True: ["Wygrana", 0x29f805], False: ['Przegrana', 0xf80505]}

            embed = discord.Embed(title=targetPlayer['nick'],
                                  description=f"```Staty: {targetPlayer['stats']} | {targetPlayer['minionsKilled']} CS\nMecz: {winOrNo[targetPlayer['winOrNo']][0]}\nDługość: {data[0]['matchLength']}```",
                                  color=winOrNo[targetPlayer['winOrNo']][1])
            embed.set_thumbnail(
                url=f"https://ddragon.leagueoflegends.com/cdn/10.14.1/img/champion/{champions.get(targetPlayer['championId'])}.png")
            redteamstr = ''
            blueteamstr = ''
            # first team
            for x in range(5):
                short = data[i]["users"][x]
                # sprawdza czy champ i nick nie ma wiecej niz 20 charów, jak tak to zmienia na skróconą wersję
                champAndPlayer = f'[{champions.get(short["championId"])}] {short["nick"]}'
                if len(champAndPlayer) >= 20:
                    champAndPlayer = champAndPlayer[0:20] + "..."
                redteamstr += f'```css\n{champAndPlayer}``````{short["stats"]} {short["minionsKilled"]} CS {short["damageDealt"]} DMG```'
            # second team
            for x in range(5, 10):
                short = data[i]["users"][x]
                # sprawdza czy champ i nick nie ma wiecej niz 20 charów, jak tak to zmienia na skróconą wersję
                champAndPlayer = f'[{champions.get(short["championId"])}] {short["nick"]}'
                if len(champAndPlayer) >= 20:
                    champAndPlayer = champAndPlayer[0:20] + "..."
                blueteamstr += f'```ini\n{champAndPlayer}``````{short["stats"]} {short["minionsKilled"]} CS {short["damageDealt"]} DMG```'
            print(2)
            embed.add_field(name="Red team", value=redteamstr, inline=True)
            embed.add_field(name="Blue team", value=blueteamstr, inline=True)
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('😀')

    # wypisuje informacje na temat gracza
    @commands.command()
    async def summoner(self, ctx, *, name='kubabmw1'):

        user = Player(name)

        embed = discord.Embed(title=f'{user.nick}', description=f"```Level: {user.level}```")
        embed.set_thumbnail(
            url=f"https://ddragon.leagueoflegends.com/cdn/10.14.1/img/profileicon/{user.profileIconId}.png")
        embed.add_field(name=f"⚔ Ranked solo/duo:", value=f'{user.ranked[0][1:]}',
                        inline=True)
        embed.add_field(name="🛡️ Ranked flex: ", value=f'{user.ranked[1][1:]}', inline=True)
        embed.add_field(name="🧒 Champion maestry:", value=f'{"".join(user.maestry)[:-1]}',
                        inline=False)

        await ctx.send(embed=embed)

    # wyświetla historię gier
    @commands.command()
    async def matches(self, ctx, name='kubabmw1', lastIndex=3, firstIndex=0):

        user = Player(name)
        data = user.createMatchList(firstIndex, lastIndex)
        print(data)
        await self.writeMatchesInChat(ctx, data, name)


def getData(short, requiredValue):
    url = f"https://{region}.api.riotgames.com/lol/{short}/{requiredValue}?api_key={getApiKey()}"
    print(url)
    return requests.get(url).json()


def getApiKey():
    with open('config.json', 'r') as file:
        data = json.loads(file.read())
        return data['riot-key']


def getExpirationDate():
    with open('config.json', 'r') as file:
        data = json.loads(file.read())
        return data['expiration_date']


def setup(client):
    client.add_cog(Riot(client))
