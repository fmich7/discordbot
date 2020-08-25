import datetime
import discord
import requests
import json
from bot import loadHelpCommands, loadConfigFile
from translate import Translator
from discord.ext import commands
from bs4 import BeautifulSoup

weather_key = loadConfigFile()['WEATHER_KEY']


class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='f1')
    async def formula_one(self, ctx, *args):
        #https://ergast.com/api/f1/2020/1/results
        nationalities = {'American': 'us', "Argentine": 'ar', 'Australian': 'au', 'Austrian': 'at', 'Belgian': 'be',
                         'Brazilian': 'br', 'British': 'gb', 'Canadian': 'ca', 'Chilean': 'cl', 'Colombian': 'co',
                         'Czech': 'cz', 'Danish': 'dk', 'Dutch': 'nl', 'Finnish': 'fi', 'French': 'fr', 'German': 'de',
                         'East German': 'de', 'Hungarian': 'hu', 'Indian': 'in', 'Indonesian': 'in', 'Irish': 'ie',
                         'Italian': 'it', 'Japanese': 'jp', 'Liechtenstein': 'li', 'Malaysian': 'my', 'Mexican': 'mx',
                         'Monegasque': 'mc', 'Moroccan': 'ma', 'New Zealand': 'nz', 'Ireland‎': 'ie', 'Polish': 'pl',
                         'Portuguese': 'pt', 'Rhodesian': 'rh', 'Russian': 'ru', 'South African': 'za', 'Spanish': 'es',
                         'Swedish': 'se', 'Swiss': 'ch', 'Thai': 'th', 'Uruguayan': 'uy', 'Venezuelan': 've'}
        if not args:
            embed = discord.Embed(colour=discord.Color.orange())
            data = loadHelpCommands()
            for i in range(len(data)):
                if(data[i][0]) == '?f1?\n':
                    tempstr = ''.join(data[i][2:])
                    embed.add_field(name=data[i][1], value=tempstr, inline=False)
            await ctx.send(embed=embed)
        elif args[0].lower() == 'season':
            if len(args) < 2:
                data_formula = getData('https://ergast.com/api/f1/current/driverStandings.json')
            else:
                try:
                    data_formula = getData(f'https://ergast.com/api/f1/{args[1]}/driverStandings.json')
                except:
                    await ctx.send('❌ Nie ma danych na temat tego sezonu')
                    return

            season_info = getData(f'http://ergast.com/api/f1/{data_formula["MRData"]["StandingsTable"]["season"]}.json')

            standings = data_formula['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

            embed = discord.Embed(title=f"TABELA WYNIKÓW {data_formula['MRData']['StandingsTable']['season']}",
                                  description=f"         Wyścigi {data_formula['MRData']['StandingsTable']['StandingsLists'][0]['round']}/{season_info['MRData']['total']}",
                                  color=0xc01b1b)

            for i in range(len(standings)):
                embed.add_field(
                    name=f'#{i + 1} :flag_{nationalities[standings[i]["Driver"]["nationality"]]}: {standings[i]["Driver"]["givenName"]} {standings[i]["Driver"]["familyName"]} [{standings[i]["Constructors"][0]["name"]}]',
                    value=f'PTS: {standings[i]["points"]} | Wins: {standings[i]["wins"]}', inline=False)

            embed.set_footer(text=f"@ergast.com/api | {datetime.date.today()}")

            await ctx.send(embed=embed)
        elif args[0].lower() == 'tracklist':
            if len(args) < 2:
                data = getData(f'https://ergast.com/api/f1/current.json')
            else:
                try:
                    data = getData(f'https://ergast.com/api/f1/{args[1]}.json')
                except:
                    await ctx.send('❌ Nie można znaleźć tego sezonu')
                    return

            embed = discord.Embed(title=f"Harmonogram wyścigów [{data['MRData']['total']}]", description=f"sezon {data['MRData']['RaceTable']['season']}",
                                  color=0x13a6a3)

            shortcut = data['MRData']['RaceTable']['Races']

            for i in range(len(shortcut)):
                embed.add_field(name=f"#{shortcut[i]['round']} {shortcut[i]['raceName']}", value=f"{shortcut[i]['Circuit']['Location']['country']} [{shortcut[i]['Circuit']['Location']['locality']}] | {shortcut[i]['date']}", inline=False)

            embed.set_footer(text=f"@ergast.com/api | {datetime.date.today()}")

            await ctx.send(embed=embed)
        elif args[0].lower() == 'quali':
            if len(args) < 2:
                data = getData(f'https://ergast.com/api/f1/current/1/qualifying.json')
            else:
                try:
                    data = getData(f'https://ergast.com/api/f1/current/{args[1]}/qualifying.json')
                except:
                    await ctx.send('❌ Nie można znaleźć tego tych kwalifikacji')
                    return

            embed = discord.Embed(title=f"Wyniki kwalifikacji [{data['MRData']['RaceTable']['season']}]", description=f"#{data['MRData']['RaceTable']['round']} {data['MRData']['RaceTable']['Races'][0]['raceName']} [{data['MRData']['RaceTable']['Races'][0]['Circuit']['circuitName']}]", color=0x13a6a3)

            allDriversStantings = ''
            alldriversTimes = ''
            shortcut = data['MRData']['RaceTable']['Races'][0]['QualifyingResults']
            for i in range(len(shortcut)):
                temponaryTimesStorage = []
                allDriversStantings += f"#{shortcut[i]['position']} :flag_{nationalities[shortcut[i]['Driver']['nationality']]}: {shortcut[i]['Driver']['givenName']} {shortcut[i]['Driver']['familyName']}\n"
                # for loop na 3 bo musi sprawdzic ktory kierowca nie ma q2 q3
                for x in range(3):
                    try:
                        temponaryTimesStorage.append(data['MRData']['RaceTable']['Races'][0]['QualifyingResults'][i][f"Q{x+1}"])
                    except:
                        break
                alldriversTimes += f"{' | '.join(temponaryTimesStorage)}\n"

            embed.add_field(name="Kierowcy", value=allDriversStantings, inline=True)
            embed.add_field(name="Q1 | Q2 | Q3", value=alldriversTimes, inline=True)

            embed.set_footer(text=f"@ergast.com/api | {datetime.date.today()}")

            await ctx.send(embed=embed)
        elif args[0].lower() == 'race':
            if len(args) < 2:
                data = getData(f'https://ergast.com/api/f1/current/1/results.json')
            else:
                try:
                    data = getData(f'https://ergast.com/api/f1/current/{args[1]}/results.json')
                except:
                    await ctx.send('❌ Nie można znaleźć tego wyścigu')
                    return

            embed = discord.Embed(title=f"Wyniki wyścigu [{data['MRData']['RaceTable']['season']}]",
                                  description=f"#{data['MRData']['RaceTable']['round']} {data['MRData']['RaceTable']['Races'][0]['raceName']} [{data['MRData']['RaceTable']['Races'][0]['Circuit']['circuitName']}]",
                                  color=0x13a6a3)

            allDriversStantings = ''
            allDriversTimes = ''
            allDriversGap = ''
            shortcut = data['MRData']['RaceTable']['Races'][0]['Results']
            for i in range(len(shortcut)):
                allDriversStantings += f"#{shortcut[i]['position']} :flag_{nationalities[shortcut[i]['Driver']['nationality']]}: {shortcut[i]['Driver']['givenName']} {shortcut[i]['Driver']['familyName']}\n"
                allDriversTimes += f"{shortcut[i]['FastestLap']['Time']['time']}\n"
                if i >= 10:
                    continue
                allDriversGap += f"{shortcut[i]['Time']['time']}\n"

            embed.add_field(name="Klasyfikacja", value=allDriversStantings, inline=True)
            embed.add_field(name="Gap", value=allDriversGap, inline=True)
            embed.add_field(name="Najlepszy czas", value=allDriversTimes, inline=True)

            embed.set_footer(text=f"@ergast.com/api | {datetime.date.today()}")

            await ctx.send(embed=embed)
        else:
            await ctx.send('❌ Coś poszło nie tak')

    # en -> any language
    @commands.command(name='translate')
    async def translator(self, ctx, *args):
        translator = Translator(to_lang=args[0])
        translation = translator.translate(' '.join(args[1:]))
        await ctx.send(translation)

    @commands.command(name='wykop')
    async def wykop(self, ctx):
        url = 'https://www.wykop.pl/hity/'
        data = requests.get(url)
        soup = BeautifulSoup(data.content, 'html.parser')
        results = soup.find(id='itemsStream')
        data = results.find_all('li', class_='link iC hot')
        for i in range(5):
            embed = discord.Embed(title=data[i].find('h2').a.string,
                                  url=data[i].find('h2').a['href'],
                                  description=data[i].find(class_='description').a.string,
                                  color=0x009dff)
            try:
                embed.set_thumbnail(
                    url=data[i].find(class_='media-content m-reset-float').a.img['src'])
            except:
                embed.set_thumbnail(
                    url=data[i].find(class_='media-content m-reset-float').a.img['data-original'])
            embed.set_author(name=f"#{i + 1} 🔥 {data[i].find(class_='diggbox').a.span.string}")
            embed.set_footer(
                text=f"{data[i].find('div', class_='fix-tagline').a.get_text()} | {data[i].find('span', class_='affect').time.string}")
            await ctx.send(embed=embed)

    @commands.command()
    async def corona(self, ctx, *args):
        data = getData('https://api.covid19api.com/summary')
        if not args:
            await ctx.send(
                f'🌍 Na świecie:     ☣ {"{:,}".format(data["Global"]["TotalConfirmed"])}     💀 {"{:,}".format(data["Global"]["TotalDeaths"])}     🏥 {"{:,}".format(data["Global"]["TotalRecovered"])}\n'
                f'🇵🇱 W Polsce:     ☣ {"{:,}".format(data["Countries"][133]["TotalConfirmed"])}     💀 {"{:,}".format(data["Countries"][133]["TotalDeaths"])}     🏥 {"{:,}".format(data["Countries"][133]["TotalRecovered"])}\n'
                f'🕒 Aktualizowane: {data["Countries"][133]["Date"][:-1].replace("T", " ")}')
            return
        try:
            country_id = next((i for i, item in enumerate(data['Countries']) if item["CountryCode"] == args[0].upper()), None)

            await ctx.send(
                f':flag_{args[0].lower()}: W {data["Countries"][country_id]["Country"]}:     ☣ {"{:,}".format(data["Countries"][country_id]["TotalConfirmed"])}     💀 {"{:,}".format(data["Countries"][country_id]["TotalDeaths"])}     '
                f'🏥 {"{:,}".format(data["Countries"][country_id]["TotalRecovered"])}\n'
                f'🕒 Aktualizowane: {data["Countries"][country_id]["Date"][:-1].replace("T", " ")}')

        except:
            await ctx.send('❌ Podany kod kraju nie istnieje')

    @commands.command()
    async def watch(self, ctx):
        await ctx.send('https://www.watch2gether.com/')

    @commands.command()
    async def list(self, ctx, *args):

        if not args:
            with open('config.json', 'r') as file:
                data = json.loads(file.read())
                o = '📋 Lista: \n'
                for x in range(len(data['lista'])):
                    o += f'[{x + 1}] {data["lista"][x]} \n'
                await ctx.send(o)

        elif args[0].lower() == 'add':
            with open('config.json', 'r+') as file:
                data = json.loads(file.read())
                data['lista'].append(' '.join(args[1:]))
                file.seek(0)
                json.dump(data, file)
                await ctx.send(f'✍🏻 {" ".join(args[1:])} zostało dodane do listy')

        elif args[0].lower() == 'remove':
            with open('config.json', 'r+') as file:
                data = json.loads(file.read())
                condition = data['lista'][int(args[1]) - 1]
                del data['lista'][int(args[1]) - 1]
                file.truncate(0)
                file.seek(0)
                json.dump(data, file)
                await ctx.send(f'⚠ {condition} zostało usunięte z listy')

        elif args[0].lower() == 'clear':
            with open('config.json', 'r+') as file:
                data = json.loads(file.read())
                data['lista'].clear()
                file.truncate(0)
                file.seek(0)
                json.dump(data, file)
                await ctx.send(f'📋 Lista została wyczyszczona')

    @commands.command()
    async def pogoda(self, ctx, *city):
        if not city:
            city = 'Milejów-Osada'
        else:
            city = ' '.join(city)

        data = getData(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}&lang=pl')

        if data['cod'] != 200:
            await ctx.send('❌ Nie mogę znaleźć takiego miasta')
            return

        color = 0xf7f10d
        img_id = ''
        first_letter = str(data['weather'][0]['id'])[0]

        if first_letter == '2':
            img_id = '11d'
            color = 0x0e1e31
        elif first_letter == '3':
            img_id = '09d'
            color = 0xf4fa6
        elif first_letter == '5':
            if data['weather'][0]['id'] == 511:
                img_id = '13d'
                color = 0xfffafa
            elif data['weather'][0]['id'] >= 520:
                img_id = '09d'
                color = 0xf4fa6
            else:
                img_id = '10d'
                color = 0xafc3cc
        elif first_letter == '6':
            img_id = '13d'
            color = 0xfffafa
        elif first_letter == '7':
            img_id = '50d'
            color = 0x686868
        elif first_letter == '8':
            if data['weather'][0]['id'] == 800:
                img_id = '01d'
                color = 0xf7f10d
            elif data['weather'][0]['id'] == 801:
                img_id = '02d'
                color = 0x7a7800
            elif data['weather'][0]['id'] == 802:
                img_id = '03d'
                color = 0x909090
            else:
                img_id = '04d'
                color = 0xcccccc

        embed = discord.Embed(title=f"Pogoda {city}",
                              description="----------------------------------------------------", color=color)
        embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{img_id}@2x.png")
        embed.add_field(name=f'Zjawisko pogodowe:', value=data["weather"][0]["description"].capitalize(), inline=True)
        embed.add_field(name=f'Temperatura:', value=f'{round(data["main"]["temp"] - 273.15)} °C', inline=False)
        embed.add_field(name=f'Zachmurzenie:', value=f'{data["clouds"]["all"]} %', inline=False)
        embed.add_field(name=f'Wiatr:', value=f'{data["wind"]["speed"]} m/s', inline=False)
        embed.add_field(name=f'Wilgotność:', value=f'{data["main"]["humidity"]} %', inline=False)
        embed.add_field(name=f'Ciśnienie:', value=f'{data["main"]["pressure"]} hPa', inline=False)
        embed.set_footer(text=f"@OpenWeatherMap | {datetime.date.today()}")

        await ctx.send(embed=embed)


def getData(url):
    print(url)
    return requests.get(url).json()


def setup(client):
    client.add_cog(Example(client))