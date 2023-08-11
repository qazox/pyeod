import os
import sys
import glob
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from discord.ext.bridge import AutoShardedBot
from discord.ext.commands import when_mentioned_or
from discord import Intents
from pyeod import config

if os.path.isfile(".token"):
    print("Loading token")
    with open(".token") as f:
        token = f.read().rstrip()
else:
    token = os.getenv("PYEOD_TOKEN", "")
if not token:
    print("Token not found")

opts = {
    "auto_sync_commands": True,
    "intents": Intents.all(),
    "command_prefix": when_mentioned_or("!"),
    "case_insensitive": True,
}

if "DEBUG_SERVER" in os.environ:
    opts["debug_guilds"] = config.main_server


def run():
    # Create new loop (since bot closes loop when quit)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    opts["loop"] = loop

    bot = AutoShardedBot(**opts)
    for file in glob.glob(
        os.path.join(config.package, "cogs", "**", "*.py"), recursive=True
    ):
        # Support packages under cogs/ for organization
        rel = os.path.relpath(file, config.package)
        submodule_name = rel.replace(".py", "").replace(os.path.sep, ".")
        print("Cog", submodule_name)
        bot.load_extension("pyeod." + submodule_name)

    try:
        loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt:
        print("Stopped")
        return False
    if os.path.isfile(config.stopfile):
        os.remove(config.stopfile)
        return False
    return True
