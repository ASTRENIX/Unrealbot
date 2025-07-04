import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl

# إعداد yt-dlp والـ ffmpeg
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # IPv4 فقط
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        stream_url = data['url']
        return cls(discord.FFmpegPCMAudio(stream_url, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play', aliases=['تشغيل', 'شغل'])
    async def play(self, ctx, *, url):
        """يشغل رابط من يوتيوب"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            if not ctx.voice_client:
                if ctx.author.voice:
                    await ctx.author.voice.channel.connect()
                else:
                    return await ctx.send("❌ يجب أن تكون في قناة صوتية أولاً.")
            ctx.voice_client.play(player, after=lambda e: print(f'❌ خطأ في التشغيل: {e}') if e else None)
        await ctx.send(f"🎶 يتم الآن تشغيل: **{player.title}**")

    @commands.command(name='stop', aliases=['ايقاف', 'قف'])
    async def stop(self, ctx):
        """يوقف التشغيل ويفصل"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("🛑 تم الإيقاف وفصل البوت من القناة.")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """إيقاف مؤقت للمقطع"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ تم الإيقاف المؤقت.")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """استئناف التشغيل"""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ تم الاستئناف.")

    @commands.command(name='skip', aliases=['تخطي'])
    async def skip(self, ctx):
        """تخطي المقطع الحالي"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ تم التخطي.")

# تحميل الـ Cog
async def setup(bot):
    bot.add_cog(Music(bot))
