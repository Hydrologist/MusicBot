import asyncio
import random
from . import exceptions

async def flip_coin():
    random.randint(0, 1)

