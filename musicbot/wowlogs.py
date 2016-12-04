import requests
import asyncio
from . import wowapi
from . import exceptions

API_KEY_PUBLIC="29496a8c76aff43d5c76d286896ec12e"
API_KEY_PRIVATE=

async def fetch_zones():
    uri = "https://www.warcraftlogs.com:443/v1/zones?api_key={apikey}".format(apikey=API_KEY_PUBLIC)
    r = requests.get(uri)
    return r.json()

def find_bracket(ilvl, zone, zoneInfo):
    searchZone = zoneInfo[zone]
    for bracket in searchZone['brackets']:
        levelRange = bracket['name'].split('-')
        if ilvl >= int(levelRange[0]) and ilvl <= int(levelRange[1]):
            return bracket['id']
    return 0

async def rank_info(character, realm, region, zone=10, metric='dps', ilvl=False):
    validMetrics = ['dps', 'hps', 'bossdps', 'tankhps', 'playerspeed', 'krsi']

    if metric not in validMetrics:
        raise exception.CommandError("Invalid metric. Valid metrics are: {0}".format(", ".join(validMetrics)), expire_in=20)

    rawZoneInfo = await fetch_zones()
    zoneInfo = dict()

    minZoneID = 9999
    maxZoneID = -1

    for i in range(0, len(rawZoneInfo)):
        if rawZoneInfo[i]['id'] > maxZoneID:
            maxZoneID = rawZoneInfo[i]['id']
        if rawZoneInfo[i]['id'] < minZoneID:
            minZoneID = rawZoneInfo[i]['id']

    if zone < minZoneID or zone > maxZoneID:
        raise exception.CommandError("Invalid Zone. Zone IDs range from {0} to {1}.".format(minZoneID, maxZoneID), expire_in=20)

    zoneInfo = {'name':rawZoneInfo[zone]['name'], 'frozen':rawZoneInfo[zone]['frozen'], 'encounters':dict()}

    for encounter in rawZoneInfo[zone]['encounters']:
        zoneInfo['encounters'][encounter['id']] = encounter['name']

    uri = "https://www.warcraftlogs.com:443/v1/rankings/character/{charname}/{server}/{reg}?zone={zone}&metric={metric}&bracket=0&api_key={apikey}".format(
        charname=character, server=realm, reg=region, zone=zone, metric=metric, apikey=API_KEY_PUBLIC)

    r = requests.get(uri)
    rankData = r.json()

    specInfo = wowapi.apiInfoRequest("en_US", "talents")


    if len(rankData) == 0:
        raise exception.CommandError("Warcraftlogs.com ranking information is currently unavailable. Try again later.", expire_in=20)
    encounters = list()

    for ranking in rankData:
        encounter = {'encounterName':zoneInfo['encounters'][ranking['encounter']]['name'], 'reportLink':"https://www.warcraftlogs.com/reports/{report}".format(report=ranking['reportID']),  'metric':ranking['total'],
            'spec':specInfo[str(ranking['class'])]['specs'][ranking['spec']], 'ilvl':ranking['itemLevel']}
        if ilvl == False:
            encounter['rank'] = ranking['rank']
            encounter['total'] = ranking['outOf']
            encounter['percentile'] = (float(encounter['total']) - float(encounter['rank'])) / float(encounter['total'])
        else
            encounter['ilvl']
            encounteruri = "https://www.warcraftlogs.com:443/v1/rankings/character/{charname}/{server}/{reg}?zone={zone}&encounter={eID}&metric={metric}&bracket={bracket}&api_key={apikey}".format(
                    charname=character, server=realm, reg=region, zone=zone, eID=ranking['encounter'], metric='dps',
            r = requests.get(encounteruri)
            encounterdata = r.json()




