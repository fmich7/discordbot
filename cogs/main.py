import datetime
import discord
import requests
import json
import os
from bot import loadHelpCommands, printHelp
from translate import Translator
from discord.ext import commands
from bs4 import BeautifulSoup

weather_key = os.environ.get('weather_key')


class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='f1')
    async def formula_one(self, ctx, *args):

        nationalities = {'American': 'us', "Argentine": 'ar', 'Australian': 'au', 'Austrian': 'at', 'Belgian': 'be',
                         'Brazilian': 'br', 'British': 'gb', 'Canadian': 'ca', 'Chilean': 'cl', 'Colombian': 'co',
                         'Czech': 'cz', 'Danish': 'dk', 'Dutch': 'nl', 'Finnish': 'fi', 'French': 'fr', 'German': 'de',
                         'East German': 'de', 'Hungarian': 'hu', 'Indian': 'in', 'Indonesian': 'in', 'Irish': 'ie',
                         'Italian': 'it', 'Japanese': 'jp', 'Liechtenstein': 'li', 'Malaysian': 'my', 'Mexican': 'mx',
                         'Monegasque': 'mc', 'Moroccan': 'ma', 'New Zealand': 'nz', 'New Zealander': 'nz', 'Ireland‎': 'ie', 'Polish': 'pl',
                         'Portuguese': 'pt', 'Rhodesian': 'rh', 'Russian': 'ru', 'South African': 'za', 'Spanish': 'es',
                         'Swedish': 'se', 'Swiss': 'ch', 'Thai': 'th', 'Uruguayan': 'uy', 'Venezuelan': 've'}
        if not args:
            await printHelp(ctx, '?f1?\n')

        def getFormulaData(link: str, linkWithOption: str, arguments, count: int):
            if len(arguments) < count:
                dataFormula = getData(link)
            else:
                # robię to z replace, bo coś nie działa z formatowaniem podczas wywoływania funkcji
                dataFormula = getData(linkWithOption.replace("{ARGS[1]}", args[1]))

            return dataFormula

        if args[0].lower() == 'season':
            data_formula = getFormulaData('https://ergast.com/api/f1/current/driverStandings.json',
                                          'https://ergast.com/api/f1/{ARGS[1]}/driverStandings.json', args, 2)

            if type(data_formula) is not dict:
                await ctx.send('❌ Nie ma danych na temat tego sezonu')
                return

            season_info = getData(f'http://ergast.com/api/f1/{data_formula["MRData"]["StandingsTable"]["season"]}.json')
            standings = data_formula['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

            embed = discord.Embed(title=f"TABELA WYNIKÓW {data_formula['MRData']['StandingsTable']['season']}",
                                  description=f"         Wyścigi {data_formula['MRData']['StandingsTable']['StandingsLists'][0]['round']}/{season_info['MRData']['total']}",
                                  color=0xc01b1b)

            for driver in standings:
                embed.add_field(
                    name=f'#{driver["position"]} :flag_{nationalities[driver["Driver"]["nationality"]]}: {driver["Driver"]["givenName"]} {driver["Driver"]["familyName"]} [{driver["Constructors"][0]["name"]}]',
                    value=f'PTS: {driver["points"]} | Wins: {driver["wins"]}', inline=False)

            embed.set_footer(text=f"@ergast.com/api | {datetime.date.today()}")

            await ctx.send(embed=embed)
        elif args[0].lower() == 'tracklist':
            data_formula = getFormulaData('https://ergast.com/api/f1/current.json',
                                          'https://ergast.com/api/f1/{ARGS[1]}.json', args, 2)

            if type(data_formula) is not dict:
                await ctx.send('❌ Nie ma danych na temat tego sezonu')
                return

            embed = discord.Embed(title=f"Harmonogram wyścigów [{data_formula['MRData']['total']}]",
                                  description=f"sezon {data_formula['MRData']['RaceTable']['season']}",
                                  color=0x13a6a3)

            shortcut = data_formula['MRData']['RaceTable']['Races']

            for i in range(len(shortcut)):
                embed.add_field(name=f"#{shortcut[i]['round']} {shortcut[i]['raceName']}",
                                value=f"{shortcut[i]['Circuit']['Location']['country']} [{shortcut[i]['Circuit']['Location']['locality']}] | {shortcut[i]['date']}",
                                inline=False)

            embed.set_footer(text=f"@ergast.com/api | {datetime.date.today()}")

            await ctx.send(embed=embed)
        elif args[0].lower() == 'quali':
            data_formula = getFormulaData('https://ergast.com/api/f1/current/qualifying.json?limit=30&offset=120',
                                          'https://ergast.com/api/f1/current/{ARGS[1]}/qualifying.json', args, 2)

            if type(data_formula) is not dict:
                await ctx.send('❌ Nie ma danych na temat tego sezonu')
                return

            # sprawdza zależnie od warunku args[1] sezon i runde
            try:
                wyniki = data_formula['MRData']['RaceTable']['season']
                descr = data_formula['MRData']['RaceTable']['round']
            except:
                wyniki = data_formula['MRData']['RaceTable']['Races'][0]['season']
                descr = data_formula['MRData']['RaceTable']['Races'][0]['round']

            embed = discord.Embed(title=f"Wyniki kwalifikacji [{wyniki}]",
                                  description=f"#{descr} "
                                              f"{data_formula['MRData']['RaceTable']['Races'][0]['raceName']} "
                                              f"[{data_formula['MRData']['RaceTable']['Races'][0]['Circuit']['circuitName']}]",
                                  color=0x13a6a3)

            allDriversStandings = ''
            alldriversTimes = ''
            shortcut = data_formula['MRData']['RaceTable']['Races'][0]['QualifyingResults']
            for i in range(len(shortcut)):
                temponaryTimesStorage = []
                allDriversStandings += f"#{shortcut[i]['position']} :flag_{nationalities[shortcut[i]['Driver']['nationality']]}: {shortcut[i]['Driver']['givenName']} {shortcut[i]['Driver']['familyName']}\n"
                # for loop na 3 bo musi sprawdzic ktory kierowca nie ma q2 q3
                for x in range(3):
                    try:
                        temponaryTimesStorage.append(
                            data_formula['MRData']['RaceTable']['Races'][0]['QualifyingResults'][i][f"Q{x + 1}"])
                    except:
                        break
                alldriversTimes += f"{' | '.join(temponaryTimesStorage)}\n"

            embed.add_field(name="Kierowcy", value=allDriversStandings, inline=True)
            embed.add_field(name="Q1 | Q2 | Q3", value=alldriversTimes, inline=True)

            embed.set_footer(text=f"@ergast.com/api | {datetime.date.today()}")

            await ctx.send(embed=embed)
        elif args[0].lower() == 'race':
            data_formula = getFormulaData('https://ergast.com/api/f1/current/1/results.json',
                                          'https://ergast.com/api/f1/current/{ARGS[1]}/results.json', args, 2)

            if type(data_formula) is not dict:
                await ctx.send('❌ Nie ma danych na temat tego sezonu')
                return

            embed = discord.Embed(title=f"Wyniki wyścigu [{data_formula['MRData']['RaceTable']['season']}]",
                                  description=f"#{data_formula['MRData']['RaceTable']['round']} {data_formula['MRData']['RaceTable']['Races'][0]['raceName']} [{data_formula['MRData']['RaceTable']['Races'][0]['Circuit']['circuitName']}]",
                                  color=0x13a6a3)

            allDriversStantings = ''
            allDriversTimes = ''
            allDriversGap = ''
            shortcut = data_formula['MRData']['RaceTable']['Races'][0]['Results']
            for i in range(len(shortcut)):
                # refactor this please
                try:
                    gap = shortcut[i]['Time']['time']
                except:
                    gap = shortcut[i]['status']
                try:
                    fastestLap = shortcut[i]['FastestLap']['Time']['time']
                except:
                    fastestLap = 'No info'

                allDriversStantings += f"#{shortcut[i]['position']} :flag_{nationalities[shortcut[i]['Driver']['nationality']]}: {shortcut[i]['Driver']['givenName']} {shortcut[i]['Driver']['familyName']}\n"
                allDriversTimes += f"{fastestLap}\n"

                if i >= 10:
                    continue
                allDriversGap += f"{gap}\n"

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

    @commands.command(aliases=['c'])
    async def build(self, ctx, arg: str):
        await ctx.send(f'https://u.gg/lol/champions/{arg.lower()}/build')

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
            country_id = next((i for i, item in enumerate(data['Countries']) if item["CountryCode"] == args[0].upper()),
                              None)

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
    async def lista(self, ctx, *args):
        response = ''
        with open('config.json', 'r+') as file:
            data = json.loads(file.read())
            if not args:
                response = '📋 Lista: \n'
                for x in range(len(data['lista'])):
                    response += f'[{x + 1}] {data["lista"][x]} \n'
                # Tutaj daje await i return, bo ten if nie potrzebuje json.dump
                await ctx.send(response)
                return

            if args[0].lower() == 'add':
                data['lista'].append(' '.join(args[1:]))
                file.seek(0)
                response = f'✍🏻 {" ".join(args[1:])} zostało dodane do listy'

            elif args[0].lower() == 'remove':
                condition = data['lista'][int(args[1]) - 1]
                del data['lista'][int(args[1]) - 1]
                file.truncate(0)
                file.seek(0)
                response = f'⚠ {condition} zostało usunięte z listy'

            elif args[0].lower() == 'clear':
                data['lista'].clear()
                file.truncate(0)
                file.seek(0)
                response = f'📋 Lista została wyczyszczona'

            json.dump(data, file)

        await ctx.send(response)

    @commands.command()
    async def pogoda(self, ctx, *city):
        if not city:
            city = 'Milejów-Osada'
        else:
            city = ' '.join(city)

        data = getData(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}&lang=pl')

        if data['cod'] > 400:
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
    try:
        return requests.get(url).json()
    except:
        return None


def setup(client):
    client.add_cog(Example(client))
