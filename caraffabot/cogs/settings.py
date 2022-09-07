import aioredis
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup

class SettingsCog(commands.Cog, name="Setting commands"):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.redis: aioredis.Redis = self.bot.redis
        
    settings = SlashCommandGroup(
        "settings", 
        """You have to be an **administrator** or the **bot owner** to use this command.""",
        checks=[commands.has_permissions(administrator=True).predicate]
    )

    @settings.command(name="help", hidden=True)
    async def _help(self, ctx):
        """
        Shows help for `setting` command.
        """
        botinfo: discord.AppInfo = await self.bot.application_info()
        e = discord.Embed(title="Settings help", )
        e.add_field(name= f"Bot uses only `slash` commands. To enable/disable command open `Server Settings > Integrations > {botinfo.name}`", value="""_ _""")
        await ctx.respond(embed=e)


    @commands.has_permissions(owner=True)
    @commands.slash_command(hidden=True)
    async def debug(self, ctx):
        self.bot.debugmode = not self.bot.debugmode
        embed = discord.Embed(title=f"Debug mode set to {self.bot.debugmode}")
        embed.color = 0x47243c
        await ctx.respond(embed=embed)
    

def setup(bot):
    bot.add_cog(SettingsCog(bot))