import discord
from discord.ext import commands
import asyncio
import json
import os
from database import Database
from utils.arabic_responses import ArabicResponses

# إعداد Bot مع الإعدادات المطلوبة
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents, help_command=None)

# تحميل الإعدادات
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# إعداد قاعدة البيانات
db = Database()

@bot.event
async def on_ready():
    print(f'🤖 البوت {bot.user} جاهز للعمل!')
    print(f'📊 متصل بـ {len(bot.guilds)} سيرفر')
    
    # إعداد قاعدة البيانات
    await db.ensure_setup()
    print("✅ تم إعداد قاعدة البيانات")
    
    # تحديث نشاط البوت
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="سيرفر Unreal | -help للمساعدة"
    )
    await bot.change_presence(activity=activity)
    
    # تحميل جميع الـ Cogs
    initial_extensions = [
        'cogs.music',
        'cogs.moderation',
        'cogs.games',
        'cogs.verification',
        'cogs.voice_rewards',
        'cogs.announcements',
        'cogs.general',
        'cogs.tickets'
    ]
    
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f'✅ تم تحميل {extension}')
        except Exception as e:
            print(f'❌ فشل في تحميل {extension}: {e}')

@bot.event
async def on_member_join(member):
    """رسالة الترحيب للأعضاء الجدد"""
    welcome_channel = bot.get_channel(config['welcome_channel_id'])
    if welcome_channel:
        embed = discord.Embed(
            title="🎉 مرحباً بك في سيرفر Unreal!",
            description=f"أهلاً وسهلاً {member.mention}!\n"
                       f"أنت العضو رقم **{member.guild.member_count}**\n\n"
                       f"📋 يرجى التوجه إلى قناة التحقق للحصول على الأدوار\n"
                       f"🎮 استمتع بوقتك معنا في المجتمع\n"
                       f"❓ استخدم `-help` للحصول على قائمة الأوامر",
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"سيرفر Unreal • {member.guild.name}")
        await welcome_channel.send(embed=embed)
    
    # إضافة العضو إلى قاعدة البيانات
    await db.add_user(member.id, member.name)

@bot.event
async def on_member_remove(member):
    """رسالة الوداع للأعضاء المغادرين"""
    leave_channel = bot.get_channel(config['welcome_channel_id'])
    if leave_channel:
        embed = discord.Embed(
            title="👋 وداعاً",
            description=f"غادر **{member.name}** السيرفر\n"
                       f"نتمنى له التوفيق 💙",
            color=0xff0000
        )
        embed.set_footer(text=f"سيرفر Unreal")
        await leave_channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """معالج الأخطاء العام"""
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ أمر غير موجود",
            description="هذا الأمر غير موجود. استخدم `-help` لرؤية جميع الأوامر المتاحة.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
    
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 صلاحيات غير كافية",
            description="ليس لديك الصلاحيات المطلوبة لاستخدام هذا الأمر.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
    
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ انتظار مطلوب",
            description=f"يجب الانتظار {error.retry_after:.2f} ثانية قبل استخدام هذا الأمر مرة أخرى.",
            color=0xffaa00
        )
        await ctx.send(embed=embed, delete_after=10)
    
    else:
        embed = discord.Embed(
            title="❌ خطأ غير متوقع",
            description="حدث خطأ أثناء تنفيذ الأمر. يرجى المحاولة مرة أخرى.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
        print(f"خطأ غير متوقع: {error}")

# تشغيل البوت
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN', 'MTM4OTM5OTQzNDI2NTIzMTQ1MQ.GlU8uy.0WO9wNOW13Y4-o1cLg1ajejPW0MGS53CndSWpE')
    bot.run(token)
