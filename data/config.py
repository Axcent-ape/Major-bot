# api id, hash
API_ID = 1488
API_HASH = 'abcde1488'


DELAYS = {
    "RELOGIN": [5, 7],  # delay after a login attempt
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
    'PLAY': [5, 15],   # delay between play in seconds
    'PLAY_GAME_DUROV': [6, 10],   # delay after play in a durov game
    'PLAY_GAME_HODL': [20, 30],  # delay after play in a hodl game
    'PLAY_GAME_ROULETTE': [2, 7],  # delay after play in a roulette game
    'PLAY_GAME_SWIPECOIN': [20, 30],  # delay after play in a swipe coin game
    'TASK': [5, 8],  # delay after completed the task
}

# Ordinal puzzle numbers.  example: [12, 1, 2, 10].Puzzle numbers - https://t.me/ApeSoftChat/9416
GAME_DUROV_CHOICES = [10, 4, 1, 16]

# Coins in a game hold coin. Max - 915
GAME_HOLD_COIN = [900, 915]

# Coins in a swipe coin game. Max - 3000
GAME_SWIPE_COIN = [2500, 3000]

TASKS = {
    # True - if need shuffle tasks or else - False
    'SHUFFLE_TASKS': False,

    # blacklist tasks
    'BLACKLIST_TASK': ['Status Purchase', 'One-time Stars Purchase', 'ne-time Stars Purchase', 'Binance x TON', 'Join the X Empire channel', 'Join MONEY DOGS', 'X Empire', 'Follow CATS Channel', 'Follow Metaton in Telegram', 'Follow Roxman in Telegram', 'Connect TON wallet', 'Join Clayton ', 'Join Clayton Game'],

    # daily blacklist tasks
    'DAILY_BLACKLIST_TASK': ['Extra Stars Purchase', 'Stars Purchase', 'Promote TON blockchain', 'Boost Major channel', 'Invite more Friends', 'Boost Roxman channel', 'Donate rating']
}


PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": "http",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "http"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30
