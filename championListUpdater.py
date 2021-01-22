import requests
import json


def getNewestVersion():
    apiLink = 'https://ddragon.leagueoflegends.com/api/versions.json'
    version = getData(apiLink)[0]
    return version


def saveUpdatedDict(updatedDictStr: str):
    with open('champions.json', 'w') as file:
        file.truncate(0)
        json.dump(json.loads(updatedDictStr), file)


def getChampionsDict():
    data = getData('https://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json'.format(getNewestVersion()))
    champions = data['data']
    s = str()
    for champion in champions.values():
        s += f'"{champion["key"]}": "{champion["id"]}", '
    s = '{{ {} }}'.format(s[:-2])
    print(s)
    saveUpdatedDict(s)


def getData(url: str):
    return requests.get(url).json()
