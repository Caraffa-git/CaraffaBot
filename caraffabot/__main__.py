import os
import discord
import aioredis
import aiohttp
import psutil
from discord.ext import bridge

from datetime import datetime
from abc import ABC
import json
from pathlib import Path


#### static values ####
__name__ = "CaraffaBot"
__version__ = "1.0"
__author__ = "Caraffa and contributors"
__repo__ = ""

tempdir = "/tmp/"
data_dir = "/app/data/"
main_dir = "/app/caraffabot/"

enabled_ext = {
    "caraffabot.cogs.help",
    "caraffabot.cogs.settings",
    "caraffabot.cogs.electronics",
    "caraffabot.cogs.fun",
    "caraffabot.cogs.image",
    "caraffabot.cogs.info",
    "caraffabot.cogs.utilities",
    "caraffabot.backend.error_handler"
}

intents = discord.Intents.all()

# check if the settings.json file exists and if not, create it
if not Path(os.path.join(data_dir, "settings.json")).exists():
    print("settings.json doesn't exist. Creating one now.")

    settings_dict = {
        "discord token": "",
        "prefix": "+",
        "redis host name": "redis"
    }

    # write the dict as json
    with open(os.path.join(data_dir, "settings.json"), "x") as f:
        # dump the dict as json to the file with an indent of 4 and support for utf-8
        json.dump(settings_dict, f, indent=4, ensure_ascii=False)

    # make the user 1000 the owner of the file, so they can edit it
    os.chown(os.path.join(data_dir, "settings.json"), 1000, 1000)

    exit(1)

# load the settings.json file
with open(os.path.join(data_dir, "settings.json"), "r") as f:
    try:
        settings_dict = json.load(f)
        discord_token = settings_dict["discord token"]
        prefix = settings_dict["prefix"]
        redis_host = settings_dict["redis host name"]
    except Exception as e:
        exc = "{}: {}".format(type(e).__name__, e)
        print("Failed to load settings.json:\n\t{}".format(exc))
        exit(1)


class CaraffaBot(bridge.Bot, ABC):
    def __init__(self, command_prefix, dir_name, help_command=None, description=None,**options):
        super().__init__(command_prefix, help_command=help_command, description=description, **options)

        self.debugmode = False

        # static values 
        self.prefix = command_prefix
        self.dir_name = dir_name
        self.data_dir = data_dir
        self.temp_dir = tempdir
        self.redis_host = redis_host

        # info
        self.pid = os.getpid()
        self.process = psutil.Process(os.getpid())
        self.version = __version__
        self.start_time = datetime.now()

        # aiohttp 
        print("Starting aiohttp session...")
        self.aiohttp_session = None  # give the aiohttp session an initial value
        self.loop.run_until_complete(self.aiohttp_start())

        # redis database 
        # 4 - info command 
        print("Connecting to redis...")
        try:
            self.redis = aioredis.Redis(host=self.redis_host, db=1, decode_responses=True, port=6379)
            self.redis_info = aioredis.Redis(host=self.redis_host, db=4, decode_responses=True)
        except aioredis.ConnectionError:
            print("Redis connection failed. Check if redis is running.")
            exit(1)
        
    async def aiohttp_start(self):
        self.aiohttp_session = aiohttp.ClientSession()


# create bot instance
print(f"Starting {__name__} v{__version__}")
bot = CaraffaBot(prefix, main_dir, intents=intents, auto_sync_commands=True)

print(f"Loading {len(enabled_ext)} extensions (cogs):")
for cog in enabled_ext:
    try:
        print(f"\tloading {cog}")
        bot.load_extension(cog)
        a = discord.Bot()
    except Exception as e:
        exc = "{}: {}".format(type(e).__name__, e)
        print("Failed to load cog {}\n{}\n".format(cog, exc))
        exit(1)

print("All extensions loaded")


# start bot with token from settings.json
try:
    bot.run(discord_token)
    print("Bot is running")
except Exception as e:
    exc = "{}: {}".format(type(e).__name__, e)
    print(
        f"Login failed. Make sure your discord token in settings.json is correct. \n{exc}")
    exit(1)
