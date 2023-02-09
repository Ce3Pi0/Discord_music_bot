from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.help_msg = """
        ```
        General commands:
        ?help - Display all the available commands
        ?(play/p) <key_word> - Finds the song on youtube and plays it in your current channel.
        ?(queue/q) - Displays the current music queue
        ?skip - Skips the current song being played
        ?(clear/c) - Stops the music and clears the queue
        ?(leave/disconnect/l/d) - Disconnects the bot from the current voice channel
        ?(pause/s) - Pauses the current song being played
        ?(info/i) - Gives info about the current song
        ?loop - Loops the next song that is in the queue (if queue empty you need to select a song)
        ```
        """

        self.text_channel_text = []

    """
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text.text_channels:
                self.text_channel_text.append(channel)

        await self.send_to_all(self.help_msg)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)
    """
    
    @commands.command(name="help", help="Display all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_msg)