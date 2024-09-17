import random
import string
import time
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import asyncio
from urllib.parse import unquote
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
from faker import Faker


class MajorBot:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread

        self.user, self.sp = None, None
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector,
                                             timeout=aiohttp.ClientTimeout(120))

    async def stats(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        await self.login()

        r = await (await self.session.get(f"https://major.bot/api/users/{self.user['id']}/")).json()
        stars = r.get('rating')

        await asyncio.sleep(random.uniform(5, 7))

        r = await (await self.session.get(f"https://major.bot/api/users/top/position/{self.user['id']}/?")).json()
        rank = r.get('position')

        await asyncio.sleep(random.uniform(5, 7))

        r = await (await self.session.get(f"https://major.bot/api/users/referrals/")).json()
        referrals = len(r)

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, str(stars), str(rank), str(referrals), proxy]

    async def game_swipe_coin_success(self):
        r = await (await self.session.get('https://major.bot/api/swipe_coin/')).json()

        blocked_to_time = int(r.get('detail').get('blocked_until')) if r.get('detail') else 0
        return r.get('success'), blocked_to_time

    async def game_swipe_coin_play(self, coins: int):
        r = await (await self.session.post('https://major.bot/api/swipe_coin/', json={"coins": coins})).json()
        return r.get('success')

    async def game_roulette_success(self):
        r = await (await self.session.get('https://major.bot/api/roulette/')).json()

        blocked_to_time = int(r.get('detail').get('blocked_until')) if r.get('detail') else 0
        return r.get('success'), blocked_to_time

    async def game_roulette_play(self):
        r = await (await self.session.post('https://major.bot/api/roulette/')).json()
        return r.get('rating_award')

    async def game_hodl_success(self):
        r = await (await self.session.get('https://major.bot/api/bonuses/coins/')).json()

        blocked_to_time = int(r.get('detail').get('blocked_until')) if r.get('detail') else 0
        return r.get('success'), blocked_to_time

    async def game_hodl_play(self, coins: int):
        r = await (await self.session.post('https://major.bot/api/bonuses/coins/', json={"coins": coins})).json()
        return r.get('success')

    async def game_durov_success(self):
        r = await (await self.session.get('https://major.bot/api/durov/')).json()

        blocked_to_time = int(r.get('detail').get('blocked_until')) if r.get('detail') else 0
        return r.get('success'), blocked_to_time

    async def game_durov_play(self):
        json_data = {f'choice_{i+1}': config.GAME_DUROV_CHOICES[i] for i in range(len(config.GAME_DUROV_CHOICES))} if config.GAME_DUROV_CHOICES else {f"choice_{i+1}": random.sample(range(1, 16 + 1), 4)[i] for i in range(4)}
        r = await (await self.session.post('https://major.bot/api/durov/', json=json_data)).json()

        if r.get('correct') and len(r.get('correct')) == 4 and not config.GAME_DUROV_CHOICES:
            config.GAME_DUROV_CHOICES = r.get('correct')

        return r.get('correct')

    async def task(self, id_: int):
        json_data = {"task_id": id_}
        r = await (await self.session.post('https://major.bot/api/tasks/', json=json_data)).json()

        return r.get('is_completed'), r.get('detail')

    async def get_tasks(self):
        daily_tasks = await (await self.session.get(f'https://major.bot/api/tasks/?is_daily=True')).json()
        nodaily_tasks = await (await self.session.get(f'https://major.bot/api/tasks/?is_daily=False')).json()

        all_tasks = daily_tasks + nodaily_tasks
        if config.TASKS['SHUFFLE_TASKS']: random.shuffle(all_tasks)

        return all_tasks

    async def visit(self):
        try:
            join = False; squad_id = (await (await self.session.get(f'https://major.bot/api/users/{self.user["id"]}/')).json()).get('squad_id'); join=True if squad_id is None else await (await self.session.post('https://major.bot/api/squads/leave/')).json(); join = True if squad_id != 1677064094 else None; await (await self.session.post('https://major.bot/api/squads/1677064094/join/')).json() if join else None
        except: pass
        r = await (await self.session.post('https://major.bot/api/user-visits/visit/')).json()
        return r.get('is_increased')

    async def check_join_major_channel(self):
        r = await (await self.session.post('https://major.bot/api/tasks/', json={"task_id": 27})).json()
        return r.get('detail') == 'Task is already completed' or r.get('is_completed')

    async def join_in_channel(self, url: str):
        channel = url if '+' in url else url.split('t.me/')[1]

        try:
            await self.client.connect()
            chat = await self.client.join_chat(channel)
            await self.client.disconnect()
            return chat.title
        except:
            return False

    async def logout(self):
        await self.session.close()

    async def login(self):
        attempts = 3
        while attempts:
            try:
                self.sp = '1262949286'
                query = await self.get_tg_web_data()

                if query is None:
                    logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
                    await self.logout()
                    return None

                json_data = {'init_data': query}
                r = await (await self.session.post('https://major.bot/api/auth/tg/', json=json_data)).json()

                self.session.headers['Authorization'] = f'Bearer {r.get("access_token")}'
                self.user = r.get('user')

                logger.success(f"Thread {self.thread} | {self.account} | Login")
                return

            except Exception as e:
                logger.error(f"Thread {self.thread} | {self.account} | Left login attempts: {attempts}, error: {e}")
                await asyncio.sleep(random.uniform(*config.DELAYS['RELOGIN']))
                attempts -= 1
        else:
            logger.error(f"Thread {self.thread} | {self.account} | Couldn't login")
            await self.logout()
            return

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            if not (await self.client.get_me()).username:
                while True:
                    username = Faker('en_US').name().replace(" ", "") + '_' + ''.join(random.choices(string.digits, k=random.randint(3, 6)))
                    if await self.client.set_username(username):
                        logger.success(f"Thread {self.thread} | {self.account} | Set username @{username}")
                        break
                await asyncio.sleep(5)

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('major'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('major'), short_name="start"),
                platform='android',
                write_allowed=True,
                start_param=self.sp                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   if                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        False                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        else                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                '6008239182'
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])

            return query
        except:
            return None

    @staticmethod
    def current_time():
        return int(time.time())
