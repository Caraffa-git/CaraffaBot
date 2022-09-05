import discord
from discord.ext import commands
from typing import Optional

class ImageCog(commands.Cog, name="Image commands"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot


    @commands.cooldown(3, 10, commands.BucketType.channel)
    @commands.slash_command(name="pfp")
    async def pfp(self, ctx, user: Optional[discord.Member] = None):
        """
        This sends someone's profile picture
        """
        
        if user is None:
            user = ctx.author
        embed = discord.Embed(title=f"{user.name}'s profile picture", color=user.color)
        embed.set_image(url=user.avatar.url)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(ImageCog(bot))
