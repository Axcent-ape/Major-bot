import random
import os
from utils.major import MajorBot
from asyncio import sleep
from random import uniform
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio
from aiohttp.client_exceptions import ContentTypeError


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    major = MajorBot(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await sleep(uniform(*config.DELAYS['ACCOUNT']))
    await major.login()

    while True:
        try:
            if not await major.check_join_major_channel():
                chat = await major.join_in_channel('https://t.me/starsmajor')
                if chat:
                    logger.success(f"Thread {thread} | {account} | Join to channel {chat}")
                else:
                    logger.warning(f"Thread {thread} | {account} | Couldn't join to major channel.")

            if await major.visit():
                logger.success(f"Thread {thread} | {account} | Collect daily streak.")

            for task in await major.get_tasks():
                if task['title'] in config.TASKS['DAILY_BLACKLIST_TASK'] + config.TASKS['BLACKLIST_TASK'] or task['is_completed']: continue

                status, skip = await major.task(task['id'])
                await asyncio.sleep(random.uniform(*config.DELAYS['TASK']))
                if skip: continue
                if status:
                    logger.success(f"Thread {thread} | {account} | Completed task «{task['title']}» and got {task['award']} Stars")
                else:
                    logger.warning(f"Thread {thread} | {account} | Couldn't complete task «{task['title']}»")

            status, blocked_to_time_durov = await major.game_durov_success()
            if status:
                await asyncio.sleep(random.uniform(*config.DELAYS['PLAY_GAME_DUROV']))
                result = await major.game_durov_play()

                if result:
                    logger.success(f"Thread {thread} | {account} | Guessed in durov puzzle and got 5000 Stars. Choices: {result}")
                else:
                    logger.warning(f"Thread {thread} | {account} | Guessed wrong in durov puzzle :(")

            status, blocked_to_time_hodl = await major.game_hodl_success()
            if status:
                await asyncio.sleep(random.uniform(*config.DELAYS['PLAY_GAME_HODL']))

                coins = random.randint(*config.GAME_HOLD_COIN)
                if await major.game_hodl_play(coins):
                    logger.success(f"Thread {thread} | {account} | Got {coins} Stars from hold coin game")

            status, blocked_to_time_roulette = await major.game_roulette_success()
            if status:
                await asyncio.sleep(random.uniform(*config.DELAYS['PLAY_GAME_ROULETTE']))

                reward = await major.game_roulette_play()
                logger.success(f"Thread {thread} | {account} | Got {reward} Stars from roulette game")

            status, blocked_to_time_swipe_coin = await major.game_swipe_coin_success()
            if status:
                await asyncio.sleep(random.uniform(*config.DELAYS['PLAY_GAME_HODL']))

                coins = random.randint(*config.GAME_SWIPE_COIN)
                if await major.game_swipe_coin_play(coins):
                    logger.success(f"Thread {thread} | {account} | Got {coins} Stars from swipe coin game")

            min_time = min(blocked_to_time_durov, blocked_to_time_hodl, blocked_to_time_swipe_coin, blocked_to_time_roulette)
            if min_time > major.current_time():
                sleep_time = min_time - major.current_time()
                logger.info(f"Thread {thread} | {account} | Sleep {sleep_time} seconds...")

                await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(5)

            if random.random() > 0.3: await major.login()

    await major.logout()


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(MajorBot(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Stars', 'Rank', 'Referrals', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df['Name'] = df['Name'].astype(str)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
