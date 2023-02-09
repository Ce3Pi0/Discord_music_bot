import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        self.is_looping = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.current_song = {
            "url":None,
            "name":None
        }

        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}


    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            self.current_song["name"] = self.music_queue[0][0]['title']
            self.current_song["url"] = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    def play_current(self):
        if self.is_looping:
            self.vc.play(discord.FFmpegPCMAudio(self.current_song["url"], **self.FFMPEG_OPTIONS), after=lambda e: self.play_current())
        else:
            self.play_next()

    # infinite loop checking 
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            if self.current_song["name"] == None and self.current_song["url"] == None:
                self.current_song["name"] = self.music_queue[0][0]['title']
                self.current_song["url"] = self.music_queue[0][0]['source']
            
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            if self.is_looping:
                self.play_current()
            else:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused and self.current_song["name"] != None and args == ():
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword or no current song detected")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False and self.is_paused == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", aliases = ["s"], help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if ctx.voice_client.is_playing():
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            if len(self.music_queue) > 0:
                self.current_song["name"] = self.music_queue[0][0]['title']
                self.current_song["url"] = self.music_queue[0][0]['source']

                await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if (i > 4): break
            retval += self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="clear", aliases=["c"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name="info", aliases = ["i"], help = "Shows the current song's title")
    async def info(self, ctx, *args):
        if ctx.voice_client.is_playing() or self.is_paused:
            await ctx.send(self.current_song["name"])
        else:
            await ctx.send("No current song detected")

    @commands.command(name="loop", help = "Loops the next song that will be played")
    async def loop(self, ctx, *args):
        if self.is_looping:
            self.is_looping = False
            await ctx.send("Looping disabled")
        else:
            self.is_looping = True
            await ctx.send("Looping next song")