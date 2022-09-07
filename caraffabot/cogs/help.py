import discord
from discord.ext import commands
from discord.commands import Option

from caraffabot.backend.util import errormsg

class HelpCog(commands.Cog, name="Help commands"):
    """
    Shows help info about commands.
    """

    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.bot.help_command = None

    def empty_space(self, embed):
        embed.add_field(name='** **', value='** **', inline=False)

    async def get_options(self, ctx:discord.AutocompleteContext):
        options = []
        
        for name in ctx.bot.cogs:
            if len(ctx.bot.cogs[name].get_commands()) > 0:
                options.append(name)
                for command in ctx.bot.cogs[name].get_commands(): 
                    options.append(command.name)
        
        return [option for option in options if option.lower().startswith(ctx.value.lower()) ]

    async def get_instance(self,input: str):
        if self.bot.get_cog(input):
            return self.bot.get_cog(input)
        elif self.bot.get_application_command(input):
            return self.bot.get_application_command(input)
        else: 
            return self.bot.get_application_command(input, type=discord.commands.SlashCommandGroup) 

    def get_command_signature(self, command: discord.commands.SlashCommand): 
        signature = ""
        for option in command.options:
            signature += f"<{option.name}> "
        return f"`{command.name} {signature}`"

    async def get_cog_help(self, cog: commands.Cog):
        e = discord.Embed(title=cog.qualified_name)
        e.add_field(name='`in_code`', value=f'`{cog.__class__.__name__}`', inline=True)
        e.add_field(name='Commands', value='_ _', inline=False)
        for cmd in cog.get_commands():
            cmd: discord.commands.SlashCommand
            e.add_field(name=cmd.name, value=(cmd.description or '[no description]'), inline=False)
        return e

    async def get_group_help(self, group: discord.commands.SlashCommandGroup):
        e = discord.Embed(title=group.qualified_name)
        e.add_field(name='Command Group', value=group.qualified_name, inline=True)
        e.add_field(name='Help', value=(group.description or '[no description]'), inline=False)
        e.add_field(name='Subcommands', value='_ _', inline=False)
        for command in group.walk_commands():
            command: discord.commands.SlashCommand
            e.add_field(name=self.get_command_signature(command), value=(command.description or '[no description]'), inline=False)
        return e

    async def get_command_help(self, command: discord.commands.SlashCommand):
        e = discord.Embed(title=(command.qualified_name or command.name))
        e.add_field(name='Signature', value=(self.get_command_signature(command)), inline=False)
        e.add_field(name='Description', value=(command.description or '[no description]'), inline=False)
        return e

    @commands.slash_command()
    async def help(self, ctx, command: Option(str, "Select command/cog/group", required = True, autocomplete=get_options)):
        selected = await self.get_instance(command)

        if isinstance(selected, discord.commands.SlashCommand):
            await ctx.respond(embed=await self.get_command_help(selected))
        elif isinstance(selected, commands.Cog):
            await ctx.respond(embed=await self.get_cog_help(selected))
        elif isinstance(selected, discord.commands.SlashCommandGroup):
            await ctx.respond(embed= await self.get_group_help(selected))
        else:
            await errormsg(ctx, "Something that shouldn't happen just happened")

        

def setup(bot):
    bot.add_cog(HelpCog(bot))