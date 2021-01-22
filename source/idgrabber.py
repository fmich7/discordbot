import requests
import json


def getChampionsDict(url: str):
    data = requests.get(url).json()
    champions = data['data']
    s = '{'
    for champion in champions.values():
        s += f'{champion["key"]}: "{champion["id"]}", '
    s = s[:-2] + '}'
    print(s)


getChampionsDict('https://ddragon.leagueoflegends.com/cdn/10.14.1/data/en_US/champion.json')