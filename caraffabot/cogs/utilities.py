import discord
import psutil
import si_prefix
from datetime import datetime
from discord.ext import commands, bridge
from caraffabot.backend import checks

class UtilityCog(commands.Cog, name="Utility commands"):
    """
    Informational commands for the bot.
    """

    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.redis = self.bot.redis

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="status", aliases=["uptime", "load"])
    async def status(self, ctx):
        """
        Displays the status of the bot.
        """
        process = psutil.Process(self.bot.pid)
        mem = process.memory_info()[0]
        redismem = (await self.redis.info())["used_memory"]

        cpu = psutil.cpu_percent(interval=None)
        ping = round(self.bot.latency * 1000, 1)
        uptime = str(datetime.now() - self.bot.start_time).split(".")[0]
        total_users = sum([users.member_count for users in self.bot.guilds])
        guilds = len(self.bot.guilds)

        embed = discord.Embed()
        embed.add_field(name="System status",
                        value=f"""RAM usage: **{si_prefix.si_format(mem + redismem)}B**
                                CPU usage: **{cpu} %**
                                uptime: **{uptime}**
                                ping: **{ping} ms**""")

        embed.add_field(name="Bot stats",
                        value=f"""guilds: **{guilds}**
                                extensions loaded: **{len(self.bot.extensions)}**
                                total users: **{total_users}**
                                bot version: **{self.bot.version}**
                                """, inline=False)

        embed.set_thumbnail(url=str(self.bot.user.avatar.url))

        if not self.bot.debugmode:
            if cpu >= 90.0:
                embed.color = 0xbb1e10
                embed.set_footer(text="Warning: CPU usage over 90%")
            else:
                embed.color = 0x00b51a
        else:
            embed.color = 0x47243c
        await ctx.respond(embed=embed)

    @commands.slash_command(name="invite")
    async def invite(self, ctx):
        """
        Sends invite for the bot.
        """
        await ctx.respond(f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=275418311744&scope=bot%20applications.commands")

def setup(bot):
    bot.add_cog(UtilityCog(bot))
