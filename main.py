import discord
import asyncio
from discord.ext import commands

from help_cog import help_cog
from music_cog import music_cog

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

bot.remove_command("help")

async def main():
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))

asyncio.run(main())


bot.run("OTk2OTIzNzE1MjI2OTc2MzE4.Gc7vhQ.TVDOOgEOzDMA4MWLxswY5p3_DDTS-OL5hJyHl0")