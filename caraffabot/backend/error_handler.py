import discord
from discord.ext import commands

from caraffabot.backend.util import errormsg

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: commands.Context, error: commands.CommandError):
        ##
        # The event triggered when an error is raised while invoking a command.
        ##

        if self.bot.debugmode:
            print(error)
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await errormsg(ctx, f'This command has been disabled.')

        if isinstance(error, commands.CommandOnCooldown):
            await errormsg(ctx, 'This command is on a %.2fs cooldown' % error.retry_after, delete_after=error.retry_after)

        if isinstance(error, commands.MissingPermissions):
            await errormsg(ctx, str(error))


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
