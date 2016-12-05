import asyncio
import random
from . import database
from . import exceptions

async def payday(author):
    db = database.DatabaseConnection()
    amount = db.payday(author)
    return amount

async def balance(author):
    db = database.DatabaseConnection()
    balance = db.get_coins(author)
    return balance

async def flip_coin(author, bet):
    coin = random.randint(0, 1)
    db = database.DatabaseConnection()
    balance = db.get_coins(author)
    if balance >= bet:
        if bet > 0:
            if coin == 1:
                db.add_coins(author, bet)
                return "{mention} Heads! You won {coins} coins.".format(mention=author.mention, coins=bet)
            else:
                amount = bet * -1
                db.add_coins(author, amount)
                return "{mention} Tails! You lost your bet.".format(mention=author.mention)
        else:
            if coin == 1:
                return "Heads!"
            else:
                return "Tails!"
    else:
        return "{mention} You don't have enough coins to bet that much!".format(mention=author.mention)
    return 0

async def slots(author, bet):
    reels = [[random.randint(0, 5) for x in range(3)] for y in range(3)]
    for x in range(3):
        for y in range(3):
            pass
    return

