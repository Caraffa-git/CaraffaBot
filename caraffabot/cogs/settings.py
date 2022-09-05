import aioredis
import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import SlashCommandGroup
from caraffabot.backend.util import errormsg

ignored_settings = {
    "status",
    "help",
    "settings",
    "debug"
}

async def get_possible_settings(bot: discord.Bot):
    perms = []
    for command in bot.application_commands:
        if not (command.name in ignored_settings):
            perms.append(command.name.upper())

    return perms


class SettingsCog(commands.Cog, name="Setting commands"):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.redis: aioredis.Redis = self.bot.redis
        
    settings = SlashCommandGroup(
        "settings", 
        """You have to be an **administrator** or the **bot owner** to use this command.""",
        checks=[commands.has_permissions(administrator=True).predicate]
    )

    async def get_command_names(self, ctx: discord.AutocompleteContext):
        command_settings = await get_possible_settings(ctx.bot)
        return [command for command in command_settings if command.startswith(ctx.value.upper())]

    async def get_values(self, ctx:discord.AutocompleteContext):
        values = {"True", "False"}
        return [value for value in values if value.lower().startswith(ctx.value.lower())]       

    @commands.cooldown(3, 10, commands.BucketType.user)
    @settings.command(name="set", aliases=["update"], hidden=True)
    async def _set(
        self, 
        ctx: commands.Context, 
        command_name: Option(str, "Select command that you want to enable/disable", required = True, autocomplete=get_command_names), 
        value: Option(str, required = True, autocomplete=get_values)):
        """
        This command changes the value of a setting.
        """
        yes_choices = ["y", "yes"]

        if not command_name.upper() in await get_possible_settings(self.bot):
            await errormsg(ctx, f"This seems to be an invalid setting! Execute `/settings list` to see all availible settings.")
            return

        if (not value.lower() == "true") and (not value.lower() == "false") :
            await errormsg(ctx, "This seems to be invalid setting value!")
            return 

        await ctx.respond(f"Set the value `{value.upper()}` to setting named `{command_name.upper()}`? (y/n)")
        msg = await self.bot.wait_for("message", timeout=10)

        if msg.content.lower() in yes_choices:
            if value.lower() == "true":
                await self.redis.hset(ctx.guild.id, command_name.upper(), "TRUE")
            elif value.lower() == "false":
                await self.redis.hset(ctx.guild.id, command_name.upper(), "FALSE")
                await ctx.send("Done.")
        else:
            await ctx.send("Cancelled.")
    


    @settings.command(name="list", aliases=["ls"], hidden=True)
    async def _list(self, ctx):
        """
        Lists all the settings for the current guild.
        """
        settings = await self.redis.hgetall(ctx.guild.id)
        e = discord.Embed(title=f"Settings for **guild {str(ctx.guild)}**")
        for setting in settings:
            e.add_field(name=setting, value=settings.get(setting))
        await ctx.respond(embed=e)



    @settings.command(name="help", hidden=True)
    async def _help(self, ctx):
        """
        Shows help for `setting` command.
        """
        e = discord.Embed(title="Settings help", )
        e.add_field(name= """
        You have to be an **administrator** or the **bot owner** to use this command.
        You should use one of the following subcommands: set, list, help.
        """, value="""_ _""")
        await ctx.respond(embed=e)


    @commands.has_permissions(administrator=True)
    @commands.slash_command(hidden=True)
    async def debug(self, ctx):
        self.bot.debugmode = not self.bot.debugmode
        embed = discord.Embed(title=f"Debug mode set to {self.bot.debugmode}")
        embed.color = 0x47243c
        await ctx.respond(embed=embed)
    

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        settings = await get_possible_settings(self.bot)
        init_dict = {settings[i]: "TRUE" for i in range(0, len(settings))}
        # check if there already are settings for the guild present
        if not await self.redis.hexists(guild.id, "PFP"):
            # set the settings that were defined in init_dict
            await self.redis.hmset(guild.id, init_dict)

def setup(bot):
    bot.add_cog(SettingsCog(bot))