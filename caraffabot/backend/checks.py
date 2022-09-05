import json
import aioredis
from typing import TypeVar, Callable
from discord.ext import commands

T = TypeVar("T")

# class IsNotEnabled(Exception):
#     """
#     Thrown when a user is attempting something, but is not an owner of the bot.
#     """
#     def __init__(self, message="User is not an owner of the bot!"):
#         self.message = message
#         super().__init__(self.message)

def is_enabled() -> Callable[[T], T]:
    """This is a custom check to see if the command is enabled in redis database."""

    async def predicate(ctx: commands.Context) -> bool:
        bot = ctx.bot
        redis: aioredis.Redis = bot.redis
        if not await redis.hexists(str(ctx.guild.id), ctx.command.name.upper()):
            await redis.hset(str(ctx.guild.id), ctx.command.name.upper(), "TRUE")
            return
        else:
            if await redis.hget(str(ctx.guild.id), ctx.command.name.upper()) == "TRUE":
                return True
            else:
                raise commands.DisabledCommand

    return commands.check(predicate)