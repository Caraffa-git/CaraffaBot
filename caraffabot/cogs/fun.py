import discord
from discord import application_command
import aiohttp
from discord.ext import commands

from caraffabot.backend import checks
from caraffabot.backend import url

def can_send_image(ctx):
    can_attach = ctx.channel.permissions_for(ctx.author).attach_files
    can_embed = ctx.channel.permissions_for(ctx.author).embed_links
    return can_attach and can_embed


class FunCog(commands.Cog, name="Fun stuff"):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.session: aiohttp.ClientSession = bot.aiohttp_session

    @checks.is_enabled()
    @commands.check(can_send_image)
    @commands.slash_command(name="cat")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def catphoto(self, ctx):    
        """
        Sends random cat photo with fun fact.
        """
        
        json = await url.get_animal_image(self.session, "cat")
        e = discord.Embed(title="Kitty Cat :cat2:", color = discord.Color.random())
        e.set_image(url=json["image"])
        e.set_footer(text=f"""Fun fact: {json["fact"]}""")
        await ctx.respond(embed=e)

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.check(can_send_image)
    @commands.slash_command(name="dog")
    @checks.is_enabled()
    async def dogphoto(self, ctx):
        """
        Sends random dog photo with fun fact.
        """
        
        json = await url.get_animal_image(self.session, "dog")
        e = discord.Embed(title="Doggo :dog:", color = discord.Color.random())
        e.set_image(url=json["image"])
        e.set_footer(text=f"""Fun fact: {json["fact"]}""")
        await ctx.respond(embed=e)

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.check(can_send_image)
    @commands.slash_command(name="surprise")
    @checks.is_enabled()
    async def animalphoto(self, ctx, arg = None):
        """
        Sends random animal photo with fun fact.
        """
        
        e = discord.Embed(title=":see_no_evil:", color = discord.Color.random())
        try:
            json = await url.get_animal_image(self.session, arg)
            e.set_image(url=json["image"])
            e.set_footer(text=f"""Fun fact: {json["fact"]}""")
        except KeyError:
            await ctx.send(text="This animal isn't listed.", delete_after=2)
        await ctx.respond(embed=e)

def setup(bot):
    bot.add_cog(FunCog(bot))
