import discord
import si_prefix
import math
from types import NoneType
from random import randint
from discord.ext import commands
from caraffabot.backend.checks import is_enabled


class TooFewArgsError(Exception):
    pass

def parse_input(s):
    """
    Simple function that parses a string to extract values
    """
    if type(s) == NoneType: return s

    s = s.replace("=", " ").split(" ")
    s_dict = dict(zip(s[::2], s[1::2]))
    for key in s_dict.keys():
        old = s_dict[key]
        new = old.replace("v", "").replace("V", "").replace(
            "u", "µ").replace("Ω", "").replace("ohm", "").replace("Hz", "").replace(
            "%","").replace("S", "").replace("s","").replace("H", "").replace("F", "")
        s_dict.update({key: new})
    return s_dict


class VoltageDivider:
    def __init__(self, d: dict):
        # d = parse_input(d)
        self.r1 = si_prefix.si_parse(d.get("r1")) if d.get("r1") else None
        self.r2 = si_prefix.si_parse(d.get("r2")) if d.get("r2") else None
        self.vin = si_prefix.si_parse(d.get("vin")) if d.get("vin") else None
        self.vout = si_prefix.si_parse(
            d.get("vout")) if d.get("vout") else None
        self.status = None

    def setPrefixes(self):
        self.r1 = si_prefix.si_format(self.r1)
        self.r2 = si_prefix.si_format(self.r2)
        self.vout = si_prefix.si_format(self.vout)
        self.vin = si_prefix.si_format(self.vin)

    def calculateOutput(self):
        if self.r1 and self.r2 and self.vin and not self.vout:
            self.vout = self.vin * self.r2 / (self.r1 + self.r2)
            self.status = "calc"
        elif self.r2 and self.vin and self.vout and not self.r1:
            self.r1 = self.r2 * (self.vin - self.vout) / self.vout
            self.status = "calc"
        elif self.r1 and self.vin and self.vout and not self.r2:
            self.r2 = self.vout * self.r1 / (self.vin - self.vout)
            self.status = "calc"
        else:
            raise TooFewArgsError()

        self.setPrefixes()

    def randomize(self):
        self.r1 = randint(1, 999999)
        self.r2 = randint(1, 999999)
        self.vin = randint(1, 500)

    def getEmbed(self):
        try:
            self.calculateOutput()
        except TooFewArgsError:
            self.randomize()
            self.calculateOutput()
            self.status = None

        embed = discord.Embed(
            title="Voltage divider calculator", color=discord.Colour.purple())
        match self.status:
            case None:
                embed.add_field(
                    name="Output:",
                    value=f"R1 =  {self.r1}Ω\nR2 = {self.r2}Ω\nVin = {self.vin}V\nVout = {self.vout}V")
                embed.add_field(name="How to use this?",
                                value="""This command will help you find out diffetent values of **unloaded** voltage divider
                For instance, `divider vin=5v r1=10k vout=3.3v` might be used to determine R2.
                The bot will try to figure out what you are looking for, based on the value you didn't enter.
                Except for Vin, you can repeat the same process for every value.
                This is compatible with any SI-prefix, including k, m, M, µ
                You can write "v" after voltages as well as "ohm" after resistance, but don't use "R" because it just confuses the bot""")
                embed.set_footer(
                    text="Note: the above voltage divider is randomly generated")
                return embed
            case "calc":
                embed.add_field(
                    name="Output:",
                    value=f"R1 =  {self.r1}Ω\nR2 = {self.r2}Ω\nVin = {self.vin}V\nVout = {self.vout}V")
                return embed


class LC_Freq:
    def __init__(self, d: dict):
        self.f = si_prefix.si_parse(d.get("f")) if d.get("f") else None
        self.c = si_prefix.si_parse(d.get("c")) if d.get("c") else None
        self.l = si_prefix.si_parse(d.get("l")) if d.get("l") else None
        self.status = None

    def setPrefixes(self):
        self.f = si_prefix.si_format(self.f)
        self.c = si_prefix.si_format(self.c)
        self.l = si_prefix.si_format(self.l)


    def calculateOutput(self):
        if self.f and self.c and not self.l:
            self.l = 1/(4*math.pi*math.pi*self.f*self.f*self.c)
        elif self.f and self.l and not self.c:
            self.c = 1/(4*math.pi*math.pi*self.f*self.f*self.l)
        elif self.c and self.l and not self.f:
            self.f = 1/math.sqrt(4*math.pi*math.pi*self.l*self.c)
        else: raise TooFewArgsError()
            

        self.status = "calc"

    def randomize(self):
        self.l = randint(1, 800)/1000000.0
        self.c = randint(1, 800)/1000000.0

    def getEmbed(self):
        try:
            self.calculateOutput()
        except:
            self.randomize()
            self.calculateOutput()
            self.status = None

        embed = discord.Embed(title="LC calculator",
                              color=discord.Colour.purple())

        match self.status:
            case None:
                embed.add_field(
                    name="Output:",
                    value=f"""f = {(self.f/1000.0):.3f}kHz\nl = {(self.l*1000000.0):.3f}µH\nc = {(self.c*1000000.0):.3f}µF""")
                embed.add_field(
                    name="How to use this?",
                    value="""This command will help you find different LC oscillator values.
                    For example: `lc l=10uH c=5nF` will display the resonant frequency of the circuit.
                    The bot will try to figure out what you're looking for based on a value you didn't enter.
                    You have to enter two values, no less no more. (frequency(f), inductance(l), capacitance(c))
                    This is compatible with any SI prefix, including k, m, M, µ""")
                embed.set_footer(
                    text="Note: the LC oscillator is randomly generated")
                return embed
            case "calc":
                embed.add_field(
                    name="Output:",
                    value=f"""f = {(self.f/1000.0):.3f}kHz\nl = {(self.l*1000000.0):.3f}µH\nc = {(self.c*1000000.0):.3f}µF""")
                embed.set_footer(
                    text="Note: the above values are approximation")
                return embed

        return embed


class ElectronicsCog(commands.Cog, name="Electronics commands"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @is_enabled()
    @commands.slash_command(name="div")
    async def divider(self, ctx, *, args=None):
        """
        Calculates values of an unloaded voltage divider. Run the command for more details.
        """
        
        try:
            div = VoltageDivider(d=parse_input(args))
        except:
            div = VoltageDivider(d={})
        await ctx.send(embed=div.getEmbed())

    @is_enabled()
    @commands.slash_command(name="lc", aliases=["rf", "rfreq", "resfreq"])
    async def frequency(self, ctx, *, args=None):
        """
        Calculates values of an LC circuit. Run the command for more details.
        """

        try:
            out = LC_Freq(d=parse_input(args))
        except:
            out = LC_Freq(d={})
        await ctx.send(embed=out.getEmbed())

def setup(bot):
    bot.add_cog(ElectronicsCog(bot))
