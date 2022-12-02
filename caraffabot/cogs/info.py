import discord
import aioredis
import os
import json
from emoji import replace_emoji
from discord.ext import commands
from discord.ui import Select, View, Button
from discord.commands import Option

class InfoCog(commands.Cog, name="Info"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.redis: aioredis.Redis = bot.redis_info
        self.current_embed = None

        self.dropdown_view = None
        self.main_view = None

        # setup buttons and buttons callback
        self.buttons = [
            Button(
                emoji="⬅️",
                style= discord.ButtonStyle.gray,
                custom_id="prev"
            ),
            Button(
                emoji="➡️",
                style= discord.ButtonStyle.gray,
                custom_id="next",

            )
        ]

        for button in self.buttons: button.callback = self.button_callback


    async def get_sections(self, ctx: discord.AutocompleteContext):
        config = json.loads(await self.redis.get(ctx.interaction.guild_id))
        return config.keys()

    @commands.slash_command(name="info")
    async def info(self, ctx, section: Option(str, "Pick a section!", required = False, autocomplete=get_sections) = None):
        """
        Sends YT channels, documents, books etc related to chosen science topic arranged in convenient way.
        """
        config = await self.redis.get(ctx.interaction.guild_id)

        # make sure that config exists in database
        if not config:
            with open(os.path.join(self.bot.data_dir, "info_defaults.json"), "r") as f:
                await self.redis.set(ctx.interaction.guild.id, json.dumps(json.load(f)))
                config = json.loads(await self.redis.get(ctx.interaction.guild_id))
        else:
            config = json.loads(config)
        
        # set up view for dropdown menu
        self.dropdown_view = View()
        dropdown = Select(options=[ discord.SelectOption(label=f'{key}. {config[key]["name"]}', emoji=config[key]["emoji"]) for key in config.keys() ])
        dropdown.callback = self.dropdown_callback
        self.dropdown_view.add_item(dropdown)

        # set up view for embeds
        self.main_view = View()
        self.main_view.add_item(dropdown)
        for button in self.buttons: self.main_view.add_item(button)

        if section != None:
            try:
                await ctx.respond(embed=self.embeds[section], view=self.main_view)
            except:
                await ctx.respond("Incorrect section name!")
        else:
            await ctx.respond("Choose a section!", view=self.dropdown_view)

    # get selected embed from database
    async def get_embed(self, config: dict ,ID: str):
        name = config[ID]["name"]
        embed = discord.Embed(title = f'{ID}. {name} {config[ID]["emoji"]}', color = discord.Color.random())
        fields = config[ID]["fields"]
        for field in fields:
            embed.add_field(name=field["name"], value="".join(f"{line}\n" for line in field["lines"]), inline=field["inline"])
        return embed

    # get next/previous embed from list
    async def get_next_embed(self, config, step: int):
        new_index = int(self.current_embed) + step
        if new_index > len(config.keys()):
            new_index = 1 
        elif new_index <= 0:
            new_index = len(config.keys())
        return await self.get_embed(config, str(new_index))

    async def button_callback(self, intr: discord.Interaction):
        config = json.loads(await self.redis.get(intr.guild_id))
        new_embed = await self.get_next_embed(config, 1 if intr.custom_id == "next" else -1)
        self.current_embed = new_embed.title.split(".")[0]
        await intr.response.edit_message(embed=new_embed, view=self.main_view, content=None)

    async def dropdown_callback(self, intr: discord.Interaction):
        intr.user.id
        config = json.loads(await self.redis.get(intr.guild_id))
        id = intr.data["values"][0].split(".")[0]
        new_embed = await self.get_embed(config, id)
        self.current_embed = id
        await intr.response.edit_message(embed=new_embed, view=self.main_view)

    # upload the default settings to the database after entering the server
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not await self.redis.get(guild.id):
            with open(os.path.join(self.bot.data_dir, "info_defaults.json"), "r") as f:
                await self.redis.set(guild.id, json.dumps(json.load(f)))

def setup(bot):
    bot.add_cog(InfoCog(bot))
