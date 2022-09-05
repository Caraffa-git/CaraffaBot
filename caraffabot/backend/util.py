import asyncio
import discord

async def errormsg(ctx=None, msg: str="", exc="", embed_only=False, delete_after = None):
    if not embed_only:
        embed = discord.Embed(title="**ERROR!**", description=msg)
        embed.color = discord.Color.red()
        embed.set_footer(text=exc)
        if delete_after:
            await ctx.respond(embed=embed, delete_after=delete_after)
        else: 
            await ctx.respond(embed=embed, delete_after=5.0)
        await asyncio.sleep(5.0)
    else:
        embed = discord.Embed(title="**ERROR!**", description=msg)
        embed.color = discord.Color.red()
        embed.set_footer(text=exc)
        return embed