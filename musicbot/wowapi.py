import requests
import asyncio
from urllib.parse import quote

API_KEY = "j88tvn636suzns4x97z4u5w6xzktce9s"

wow_races = {1:'Human',2:'Orc',3:'Dwarf',4:'Night Elf',5:'Undead',6:'Tauren',7:'Gnome',8:'Troll',9:'Goblin',10:'Blood Elf',11:'Draenei',22:'Worgen',24:'Pandaren',25:'Pandaren',26:'Pandaren'}
wow_classes = {1:'Warrior',2:'Paladin',3:'Hunter',4:'Rogue',5:'Priest',6:'Death Knight',7:'Shaman',8:'Mage',9:'Warlock',10:'Monk',11:'Druid',12:'Demon Hunter'}
wow_factions = {0:'Alliance',1:'Horde'}

async def apiCharacterRequest(realm, character, region, fields):

    uri = "https://us.api.battle.net/wow/character/{0}/{1}?fields={3}&locale={2}&apikey={api_key}".format(realm, character, region, fields, api_key="j88tvn636suzns4x97z4u5w6xzktce9s")

    r = requests.get(uri)

    return r.json()

async def apiInfoRequest(region, dataType, dataSubType=None):

    uri = "https://us.api.battle.net/wow/data/{data}"
    if dataSubType == None:
        subTypeString = ''
    else:
        subTypeString = '/' + dataSubType

    uri += subTypeString + "?locale={locale}&apikey={apikey}".format(locale=region, apikey=API_KEY)

    r = requests.get(uri)

    return r.json()

def basicInfoParse(chardata):
    basicinfo = "__**{name}-{realm}**__".format(name=chardata['name'], realm=chardata['realm'])
    if "guild" in chardata:
        basicinfo += " **[{guild}]**\n".format(guild=chardata['guild']['name'])
    else:
        basicinfo += "\n"
    basicinfo += "**{level} {race} ".format(level=chardata['level'], race=wow_races[chardata['race']])
    if chardata['level'] >= 15 and "talents" in chardata:
        basicinfo += "{spec} ".format(spec=chardata['talents'][0]['spec']['name'])
    basicinfo += "{wowclass} [{faction}]**\n".format(wowclass=wow_classes[chardata['class']], faction=wow_factions[chardata['faction']])
    if "items" in chardata and "averageItemLevel" in chardata['items'] and "averageItemLevelEquipped" in chardata['items']:
        basicinfo += "**ILVL {equipilvl} ({ilvl})**\n".format(equipilvl=chardata['items']['averageItemLevelEquipped'],
                ilvl=chardata['items']['averageItemLevel'])
    roleIcons = {'DPS': ':crossed_swords:', 'TANK': ':shield:', 'HEALING': ':syringe:'}
    if chardata['level'] >= 15 and "talents" in chardata:
        basicinfo += "**Role: {role}** {icon}\n".format(role=chardata['talents'][0]['spec']['role'], icon=roleIcons[chardata['talents'][0]['spec']['role']])
    if 11194 in chardata['achievements']['achievementsCompleted']:
        basicinfo += ":white_check_mark: **AOTC: Xavius**\n"
    else:
        basicinfo += ":x:**AOTC: Xavius**\n"
    basicinfo += "<http://us.battle.net/wow/en/character/{realm}/{name}/simple>".format(realm=quote(chardata['realm']),
            name=chardata['name'])
    return basicinfo

async def basicInfo(realm, character, region):
    chardata = await apiCharacterRequest(realm, character, region, 'guild,items,talents,achievements')
    basicinfo = basicInfoParse(chardata)
    return basicinfo


async def statInfo(realm, character, region):
    chardata = await apiCharacterRequest(realm, character, region, 'guild,items,stats,talents,achievements')
    charstats = chardata['stats']

    statinfo = "```\nStats\n-----\nStrength: {strength}\nAgility: {agility}\nIntelligence: {intelligence}\nStamina: {stamina}\n-----\nCrit: {crit:.2f}%\nSpell Crit: {spellcrit:.2f}%\nHaste: {haste:.2f}%\nMastery: {mastery:.2f}%\nVersatility: {versatility}\n----- \nArmor: {armor}\nDodge: {dodge:.2f}%\nParry: {parry:.2f}%\nBlock: {block:.2f}%```".format(
            strength=charstats['str'],agility=charstats['agi'],intelligence=charstats['int'],stamina=charstats['sta'],crit=charstats['crit'],spellcrit=charstats['spellCrit'],haste=charstats['haste'],mastery=charstats['mastery'],
            versatility=charstats['versatility'],armor=charstats['armor'],dodge=charstats['dodge'],parry=charstats['parry'],block=charstats['block'])

    return '\n'.join([basicInfoParse(chardata), statinfo])

def parseItem(slot, itemdata):
    iteminfo = "{itemslot}: \n**{name}** `{ilvl}`\n<http://wowhead.com/item={itemid}>".format(itemslot=slot.title(), ilvl=itemdata['ilvl'], name=itemdata['name'], itemid=itemdata['id'])
    return iteminfo

async def equipInfo(realm, character, region):
    chardata = await apiCharacterRequest(realm, character, region, 'guild,items,talents,achievements')

    equipdata = dict()
    equips = list()

    for key in chardata['items'].keys():
        if key != 'averageItemLevel' and key != 'averageItemLevelEquipped':
            equipdata[key] = {'name':chardata['items'][key]['name'], 'id':chardata['items'][key]['id'], 'ilvl':chardata['items'][key]['itemLevel'], 'quality':chardata['items'][key]['quality']}
            equips.append(parseItem(key, equipdata[key]))

    equipinfo = "-----\nEquipment:\n" + "\n".join(equips)

    equipinfo = '\n'.join([basicInfoParse(chardata), equipinfo])

    return equipinfo

def findTier(tier, activetalents):
    for talent in activetalents:
        if talent['tier'] == tier:
            return talent
    return False

async def talentInfo(realm, character, region):
    chardata = await apiCharacterRequest(realm, character, region, 'guild,items,talents,achievements')

    activetalents = chardata['talents'][0]['talents']

    talents = list()

    for i in range(0,7):
        talent = findTier(i, activetalents)
        if talent != False:
            talents.append(talent['spell']['name'])
        else:
            talents.append("None")

    talentinfo = "`Talents:`\n"

    if chardata['class'] != 12:
        talentinfo += "`15` `{0[0]}`\n`30` `{0[1]}`\n`45` `{0[2]}`\n`60` `{0[3]}`\n`75` `{0[4]}`\n`90` `{0[5]}`\n`100` `{0[6]}`".format(talents)
    else:
        talentinfo += "`99` `{0[0]}`\n`100` `{0[1]}`\n`102` `{0[2]}`\n`104` `{0[3]}`\n`106` `{0[4]}`\n`108` `{0[5]}`\n`110` `{0[6]}`".format(talents)

    talentinfo = '\n'.join([basicInfoParse(chardata), talentinfo])

    return talentinfo
