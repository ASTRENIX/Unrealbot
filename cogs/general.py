import discord
from discord.ext import commands
import json
import platform
import psutil
import asyncio
from datetime import datetime, timedelta
from database import Database
from utils.arabic_responses import ArabicResponses

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.responses = ArabicResponses()
        
        # تحميل الإعدادات
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @commands.command(name='مساعدة', aliases=['help'])
    async def help_command(self, ctx, category=None):
        """عرض قائمة الأوامر والمساعدة"""
        if category is None:
            # القائمة الرئيسية
            embed = discord.Embed(
                title="📚 مساعدة بوت Unreal",
                description="مرحباً بك في نظام المساعدة! اختر فئة للحصول على تفاصيل أكثر:",
                color=0x00aaff
            )
            
            embed.add_field(
                name="🎵 الموسيقى",
                value="`-مساعدة موسيقى`\n"
                     "تشغيل الموسيقى من YouTube",
                inline=True
            )
            
            embed.add_field(
                name="🎮 الألعاب",
                value="`-مساعدة ألعاب`\n"
                     "ألعاب تفاعلية ومسابقات",
                inline=True
            )
            
            embed.add_field(
                name="👮‍♂️ الإشراف",
                value="`-مساعدة إشراف`\n"
                     "أدوات الإشراف والتحكم",
                inline=True
            )
            
            embed.add_field(
                name="🔒 التحقق",
                value="`-مساعدة تحقق`\n"
                     "نظام التحقق من العضوية",
                inline=True
            )
            
            embed.add_field(
                name="🎤 مكافآت الصوت",
                value="`-مساعدة صوت`\n"
                     "نظام النقاط والمكافآت",
                inline=True
            )
            
            embed.add_field(
                name="📢 الإعلانات",
                value="`-مساعدة إعلانات`\n"
                     "إدارة الإعلانات",
                inline=True
            )
            
            embed.add_field(
                name="⚙️ عام",
                value="`-مساعدة عام`\n"
                     "معلومات السيرفر والمستخدمين",
                inline=True
            )
            
            embed.set_footer(text="💡 استخدم -مساعدة [الفئة] للحصول على تفاصيل أكثر")
            
        elif category.lower() in ['موسيقى', 'music']:
            embed = discord.Embed(
                title="🎵 أوامر الموسيقى",
                description="جميع أوامر تشغيل الموسيقى:",
                color=0x00ff00
            )
            
            embed.add_field(
                name="التشغيل والتحكم",
                value="`-تشغيل [اسم/رابط]` - تشغيل موسيقى\n"
                     "`-إيقاف` - إيقاف مؤقت\n"
                     "`-استكمال` - استكمال التشغيل\n"
                     "`-تخطي` - تخطي المقطع\n"
                     "`-توقف` - إيقاف كامل\n"
                     "`-تكرار` - تكرار المقطع",
                inline=False
            )
            
            embed.add_field(
                name="إدارة القائمة",
                value="`-قائمة` - عرض قائمة الانتظار\n"
                     "`-مسح_القائمة` - مسح القائمة\n"
                     "`-مستوى_الصوت [0-100]` - تعديل الصوت",
                inline=False
            )
            
        elif category.lower() in ['ألعاب', 'games']:
            embed = discord.Embed(
                title="🎮 أوامر الألعاب",
                description="جميع الألعاب المتاحة:",
                color=0xff6600
            )
            
            embed.add_field(
                name="الألعاب المتاحة",
                value="`-سؤال [الصعوبة]` - أسئلة ثقافية\n"
                     "`-تخمين_كلمة [الفئة]` - لعبة الكلمات\n"
                     "`-تخمين_رقم [الحد الأقصى]` - تخمين الأرقام\n"
                     "`-قائمة_الألعاب` - جميع الألعاب",
                inline=False
            )
            
            embed.add_field(
                name="الإحصائيات",
                value="`-إحصائيات_الألعاب [@المستخدم]` - إحصائيات اللعب",
                inline=False
            )
            
        elif category.lower() in ['إشراف', 'moderation']:
            embed = discord.Embed(
                title="👮‍♂️ أوامر الإشراف",
                description="أدوات الإشراف والتحكم:",
                color=0xff0000
            )
            
            embed.add_field(
                name="الإجراءات التأديبية",
                value="`-طرد [@المستخدم] [السبب]` - طرد عضو\n"
                     "`-حظر [@المستخدم] [السبب]` - حظر عضو\n"
                     "`-إلغاء_حظر [معرف] [السبب]` - إلغاء حظر\n"
                     "`-كتم [@المستخدم] [الدقائق] [السبب]` - كتم عضو\n"
                     "`-إلغاء_كتم [@المستخدم]` - إلغاء كتم",
                inline=False
            )
            
            embed.add_field(
                name="التحذيرات وإدارة الرسائل",
                value="`-تحذير [@المستخدم] [السبب]` - إعطاء تحذير\n"
                     "`-تحذيرات [@المستخدم]` - عرض التحذيرات\n"
                     "`-مسح [العدد] [@المستخدم]` - مسح رسائل",
                inline=False
            )
            
        elif category.lower() in ['تحقق', 'verification']:
            embed = discord.Embed(
                title="🔒 أوامر التحقق",
                description="نظام التحقق من العضوية:",
                color=0x00ff00
            )
            
            embed.add_field(
                name="إدارة التحقق",
                value="`-إعداد_التحقق [القناة] [الدور]` - إعداد النظام\n"
                     "`-تحقق_يدوي [@المستخدم]` - تحقق يدوي\n"
                     "`-إلغاء_تحقق [@المستخدم]` - إلغاء تحقق\n"
                     "`-حالة_التحقق [@المستخدم]` - عرض الحالة\n"
                     "`-إحصائيات_التحقق` - إحصائيات السيرفر",
                inline=False
            )
            
        elif category.lower() in ['صوت', 'voice']:
            embed = discord.Embed(
                title="🎤 أوامر مكافآت الصوت",
                description="نظام النقاط والمكافآت:",
                color=0xffd700
            )
            
            embed.add_field(
                name="المعلومات والإحصائيات",
                value="`-نشاط_الصوت [@المستخدم]` - إحصائيات الصوت\n"
                     "`-لوحة_الصوت` - لوحة المتصدرين\n"
                     "`-إعداد_مكافآت_الصوت [النقاط]` - إعداد النظام",
                inline=False
            )
            
        elif category.lower() in ['إعلانات', 'announcements']:
            embed = discord.Embed(
                title="📢 أوامر الإعلانات",
                description="إدارة الإعلانات:",
                color=0x00aaff
            )
            
            embed.add_field(
                name="إنشاء الإعلانات",
                value="`-إعلان [القناة] [المحتوى]` - إعلان عادي\n"
                     "`-إعلان_مُنسق` - إعلان تفاعلي منسق\n"
                     "`-إعلان_سريع [المحتوى]` - إعلان سريع\n"
                     "`-إعلان_مهم [القناة] [المحتوى]` - إعلان مع تنبيه\n"
                     "`-جدولة_إعلان [الدقائق] [القناة] [المحتوى]` - إعلان مجدول",
                inline=False
            )
            
            embed.add_field(
                name="إدارة الإعلانات",
                value="`-سجل_الإعلانات [العدد]` - سجل الإعلانات\n"
                     "`-حذف_إعلان [معرف الرسالة]` - حذف إعلان",
                inline=False
            )
            
        elif category.lower() in ['عام', 'general']:
            embed = discord.Embed(
                title="⚙️ الأوامر العامة",
                description="معلومات السيرفر والمستخدمين:",
                color=0x0099ff
            )
            
            embed.add_field(
                name="المعلومات",
                value="`-معلومات_السيرفر` - معلومات السيرفر\n"
                     "`-معلومات_المستخدم [@المستخدم]` - معلومات العضو\n"
                     "`-معلومات_البوت` - معلومات البوت\n"
                     "`-ping` - سرعة الاستجابة",
                inline=False
            )
            
            embed.add_field(
                name="الإحصائيات",
                value="`-إحصائيات` - إحصائيات عامة\n"
                     "`-لوحة_المتصدرين` - أفضل الأعضاء\n"
                     "`-نشاطي` - نشاطك الشخصي",
                inline=False
            )
            
        else:
            embed = discord.Embed(
                title="❌ فئة غير موجودة",
                description="الفئات المتاحة: موسيقى، ألعاب، إشراف، تحقق، صوت، إعلانات، عام",
                color=0xff0000
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='معلومات_السيرفر', aliases=['server_info'])
    async def server_info(self, ctx):
        """عرض معلومات السيرفر"""
        guild = ctx.guild
        
        # حساب الإحصائيات
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed = discord.Embed(
            title=f"📊 معلومات سيرفر {guild.name}",
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # معلومات أساسية
        embed.add_field(
            name="📋 معلومات أساسية",
            value=f"**الاسم:** {guild.name}\n"
                 f"**المعرف:** {guild.id}\n"
                 f"**المالك:** {guild.owner.mention}\n"
                 f"**تاريخ الإنشاء:** {guild.created_at.strftime('%Y-%m-%d')}",
            inline=True
        )
        
        # إحصائيات الأعضاء
        embed.add_field(
            name="👥 الأعضاء",
            value=f"**المجموع:** {total_members:,}\n"
                 f"**متصل:** {online_members:,}\n"
                 f"**بشر:** {humans:,}\n"
                 f"**بوتات:** {bots:,}",
            inline=True
        )
        
        # القنوات
        embed.add_field(
            name="📺 القنوات",
            value=f"**نصية:** {text_channels}\n"
                 f"**صوتية:** {voice_channels}\n"
                 f"**فئات:** {categories}\n"
                 f"**المجموع:** {text_channels + voice_channels}",
            inline=True
        )
        
        # معلومات إضافية
        embed.add_field(
            name="🛡️ مستوى التحقق",
            value=guild.verification_level.name,
            inline=True
        )
        
        embed.add_field(
            name="🎭 الأدوار",
            value=f"{len(guild.roles)} دور",
            inline=True
        )
        
        embed.add_field(
            name="😀 الإيموجي",
            value=f"{len(guild.emojis)} إيموجي",
            inline=True
        )
        
        # الميزات المفعلة
        features = guild.features
        if features:
            feature_names = {
                'COMMUNITY': 'مجتمع',
                'NEWS': 'أخبار',
                'DISCOVERABLE': 'قابل للاكتشاف',
                'MONETIZATION_ENABLED': 'تفعيل الربح',
                'PARTNER': 'شريك Discord',
                'VERIFIED': 'موثق'
            }
            
            enabled_features = []
            for feature in features:
                feature_name = feature_names.get(feature, feature)
                enabled_features.append(feature_name)
            
            if enabled_features:
                embed.add_field(
                    name="✨ الميزات المفعلة",
                    value="\n".join([f"• {feature}" for feature in enabled_features[:5]]),
                    inline=False
                )
        
        embed.set_footer(text=f"سيرفر Unreal • {guild.member_count} عضو")
        
        await ctx.send(embed=embed)

    @commands.command(name='معلومات_المستخدم', aliases=['user_info'])
    async def user_info(self, ctx, member: discord.Member = None):
        """عرض معلومات المستخدم"""
        if member is None:
            member = ctx.author
        
        # الحصول على بيانات من قاعدة البيانات
        user_data = await self.db.get_user(member.id)
        
        embed = discord.Embed(
            title=f"👤 معلومات المستخدم - {member.display_name}",
            color=member.color if member.color != discord.Color.default() else 0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # معلومات أساسية
        embed.add_field(
            name="📋 معلومات أساسية",
            value=f"**الاسم:** {member.name}\n"
                 f"**اللقب:** {member.display_name}\n"
                 f"**المعرف:** {member.id}\n"
                 f"**بوت:** {'نعم' if member.bot else 'لا'}",
            inline=True
        )
        
        # تواريخ مهمة
        embed.add_field(
            name="📅 التواريخ",
            value=f"**إنشاء الحساب:** {member.created_at.strftime('%Y-%m-%d')}\n"
                 f"**انضمام للسيرفر:** {member.joined_at.strftime('%Y-%m-%d') if member.joined_at else 'غير محدد'}",
            inline=True
        )
        
        # الحالة
        status_map = {
            discord.Status.online: "🟢 متصل",
            discord.Status.idle: "🟡 غائب",
            discord.Status.dnd: "🔴 مشغول",
            discord.Status.offline: "⚫ غير متصل"
        }
        
        embed.add_field(
            name="📱 الحالة",
            value=status_map.get(member.status, "❓ غير معروف"),
            inline=True
        )
        
        # الأدوار
        if len(member.roles) > 1:  # تجاهل دور @everyone
            roles = [role.mention for role in member.roles[1:][:10]]  # أول 10 أدوار
            roles_text = " ".join(roles)
            if len(member.roles) > 11:
                roles_text += f" وَ {len(member.roles) - 11} دور آخر..."
            
            embed.add_field(
                name=f"🎭 الأدوار ({len(member.roles) - 1})",
                value=roles_text,
                inline=False
            )
        
        # إحصائيات من قاعدة البيانات
        if user_data:
            total_xp = user_data[2]
            voice_time = user_data[4]
            messages_sent = user_data[5]
            games_won = user_data[6]
            is_verified = user_data[9]
            
            # تحويل وقت الصوت
            hours = voice_time // 3600
            minutes = (voice_time % 3600) // 60
            
            embed.add_field(
                name="📊 الإحصائيات",
                value=f"**النقاط:** {total_xp:,}\n"
                     f"**وقت الصوت:** {hours}ساعة {minutes}دقيقة\n"
                     f"**الرسائل:** {messages_sent:,}\n"
                     f"**الألعاب المكسوبة:** {games_won:,}\n"
                     f"**متحقق:** {'✅ نعم' if is_verified else '❌ لا'}",
                inline=True
            )
        
        # الصلاحيات المهمة
        important_perms = []
        if member.guild_permissions.administrator:
            important_perms.append("🔧 مدير")
        if member.guild_permissions.manage_guild:
            important_perms.append("⚙️ إدارة السيرفر")
        if member.guild_permissions.manage_channels:
            important_perms.append("📺 إدارة القنوات")
        if member.guild_permissions.manage_roles:
            important_perms.append("🎭 إدارة الأدوار")
        if member.guild_permissions.kick_members:
            important_perms.append("👮‍♂️ طرد الأعضاء")
        if member.guild_permissions.ban_members:
            important_perms.append("🔨 حظر الأعضاء")
        
        if important_perms:
            embed.add_field(
                name="🛡️ الصلاحيات المهمة",
                value="\n".join(important_perms),
                inline=True
            )
        
        # النشاط الحالي
        if member.activity:
            activity_type = {
                discord.ActivityType.playing: "🎮 يلعب",
                discord.ActivityType.streaming: "📺 يبث",
                discord.ActivityType.listening: "🎵 يستمع إلى",
                discord.ActivityType.watching: "👀 يشاهد"
            }
            
            activity_text = activity_type.get(member.activity.type, "📱 نشاط")
            embed.add_field(
                name="🎯 النشاط الحالي",
                value=f"{activity_text} {member.activity.name}",
                inline=False
            )
        
        embed.set_footer(text=f"معلومات من سيرفر {ctx.guild.name}")
        
        await ctx.send(embed=embed)

    @commands.command(name='معلومات_البوت', aliases=['bot_info'])
    async def ul_info(self, ctx):
        """عرض معلومات البوت"""
        # إحصائيات السيرفر
        total_guilds = len(self.bot.guilds)
        total_users = len(self.bot.users)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        
        # معلومات النظام
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # وقت التشغيل
        uptime = datetime.utcnow() - self.bot.start_time if hasattr(self.bot, 'start_time') else timedelta(0)
        
        embed = discord.Embed(
            title="🤖 معلومات البوت",
            description="بوت Unreal - بوت عربي شامل لإدارة المجتمعات",
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # معلومات أساسية
        embed.add_field(
            name="📋 معلومات أساسية",
            value=f"**الاسم:** {self.bot.user.name}\n"
                 f"**المعرف:** {self.bot.user.id}\n"
                 f"**إصدار Discord.py:** {discord.__version__}\n"
                 f"**إصدار Python:** {platform.python_version()}",
            inline=True
        )
        
        # إحصائيات
        embed.add_field(
            name="📊 الإحصائيات",
            value=f"**الخوادم:** {total_guilds:,}\n"
                 f"**المستخدمون:** {total_users:,}\n"
                 f"**القنوات:** {total_channels:,}\n"
                 f"**الأوامر:** {len(self.bot.commands)}",
            inline=True
        )
        
        # معلومات النظام
        embed.add_field(
            name="💻 النظام",
            value=f"**نظام التشغيل:** {platform.system()}\n"
                 f"**المعالج:** {cpu_percent}%\n"
                 f"**الذاكرة:** {memory.percent}%\n"
                 f"**التخزين:** {disk.percent}%",
            inline=True
        )
        
        # وقت التشغيل
        if uptime.total_seconds() > 0:
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            embed.add_field(
                name="⏰ وقت التشغيل",
                value=f"{days} يوم، {hours} ساعة، {minutes} دقيقة",
                inline=True
            )
        
        # المطور
        embed.add_field(
            name="👨‍💻 المطور",
            value="تم تطوير هذا البوت خصيصاً لسيرفر Unreal",
            inline=True
        )
        
        # البينغ
        latency = round(self.bot.latency * 1000)
        embed.add_field(
            name="🏓 البينغ",
            value=f"{latency} مللي ثانية",
            inline=True
        )
        
        # الميزات
        features = [
            "🎵 تشغيل موسيقى YouTube",
            "🎮 ألعاب تفاعلية",
            "👮‍♂️ أدوات إشراف شاملة",
            "🔒 نظام تحقق متطور",
            "🎤 مكافآت الصوت",
            "📢 نظام إعلانات",
            "📊 إحصائيات مفصلة",
            "🌐 واجهة عربية كاملة"
        ]
        
        embed.add_field(
            name="✨ الميزات",
            value="\n".join(features[:4]),
            inline=True
        )
        
        embed.add_field(
            name="🚀 ميزات إضافية",
            value="\n".join(features[4:]),
            inline=True
        )
        
        embed.set_footer(text="شكراً لاستخدام بوت Unreal!")
        
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx):
        """فحص سرعة استجابة البوت"""
        latency = round(self.bot.latency * 1000)
        
        # تحديد لون البينغ
        if latency < 100:
            color = 0x00ff00  # أخضر
            status = "ممتاز"
        elif latency < 200:
            color = 0xffaa00  # أصفر
            status = "جيد"
        else:
            color = 0xff0000  # أحمر
            status = "بطيء"
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**البينغ:** {latency} مللي ثانية\n**الحالة:** {status}",
            color=color
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='إحصائيات', aliases=['stats'])
    async def stats(self, ctx):
        """عرض إحصائيات عامة للسيرفر"""
        guild = ctx.guild
        
        # إحصائيات الأعضاء
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        
        # إحصائيات من قاعدة البيانات
        top_voice_users = await self.db.get_top_users(3, 'voice_time')
        top_xp_users = await self.db.get_top_users(3, 'total_xp')
        
        embed = discord.Embed(
            title="📈 إحصائيات السيرفر",
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        # إحصائيات عامة
        embed.add_field(
            name="👥 الأعضاء",
            value=f"**المجموع:** {total_members:,}\n"
                 f"**متصل الآن:** {online_members:,}\n"
                 f"**نسبة الاتصال:** {(online_members/total_members*100):.1f}%",
            inline=True
        )
        
        # القنوات
        embed.add_field(
            name="📺 القنوات",
            value=f"**نصية:** {len(guild.text_channels)}\n"
                 f"**صوتية:** {len(guild.voice_channels)}\n"
                 f"**المجموع:** {len(guild.channels)}",
            inline=True
        )
        
        # الأدوار
        embed.add_field(
            name="🎭 الأدوار",
            value=f"**العدد:** {len(guild.roles)}\n"
                 f"**أعلى دور:** {guild.roles[-1].name}",
            inline=True
        )
        
        # أفضل 3 في النشاط الصوتي
        if top_voice_users:
            voice_text = ""
            for i, (user_id, username, voice_time) in enumerate(top_voice_users, 1):
                hours = voice_time // 3600
                voice_text += f"{i}. {username} - {hours}ساعة\n"
            
            embed.add_field(
                name="🎤 أكثر نشاطاً صوتياً",
                value=voice_text,
                inline=True
            )
        
        # أفضل 3 في النقاط
        if top_xp_users:
            xp_text = ""
            medals = ["🥇", "🥈", "🥉"]
            for i, (user_id, username, total_xp) in enumerate(top_xp_users):
                medal = medals[i] if i < 3 else f"{i+1}."
                xp_text += f"{medal} {username} - {total_xp:,} نقطة\n"
            
            embed.add_field(
                name="⭐ أعلى نقاط",
                value=xp_text,
                inline=True
            )
        
        # إحصائيات البوت
        bot_stats = f"**الأوامر:** {len(self.bot.commands)}\n"
        bot_stats += f"**الكوجز:** {len(self.bot.cogs)}\n"
        bot_stats += f"**البينغ:** {round(self.bot.latency * 1000)} مللي ثانية"
        
        embed.add_field(
            name="🤖 البوت",
            value=bot_stats,
            inline=True
        )
        
        embed.set_footer(text=f"إحصائيات {guild.name}")
        
        await ctx.send(embed=embed)

    @commands.command(name='لوحة_المتصدرين', aliases=['leaderboard'])
    async def leaderboard(self, ctx, category='نقاط'):
        """عرض لوحة المتصدرين"""
        if category.lower() in ['نقاط', 'xp', 'points']:
            top_users = await self.db.get_top_users(10, 'total_xp')
            title = "🏆 لوحة المتصدرين - النقاط"
            emoji = "⭐"
            unit = "نقطة"
        elif category.lower() in ['صوت', 'voice']:
            top_users = await self.db.get_top_users(10, 'voice_time')
            title = "🎤 لوحة المتصدرين - النشاط الصوتي"
            emoji = "⏰"
            unit = "دقيقة"
        elif category.lower() in ['رسائل', 'messages']:
            top_users = await self.db.get_top_users(10, 'messages_sent')
            title = "💬 لوحة المتصدرين - الرسائل"
            emoji = "📝"
            unit = "رسالة"
        else:
            embed = discord.Embed(
                title="❌ فئة غير صحيحة",
                description="الفئات المتاحة: `نقاط`, `صوت`, `رسائل`",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        if not top_users:
            embed = discord.Embed(
                title=title,
                description="لا توجد بيانات متاحة حتى الآن",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=title,
            color=0xffd700,
            timestamp=datetime.utcnow()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, username, value) in enumerate(top_users):
            medal = medals[i] if i < 3 else f"#{i+1}"
            
            # تنسيق القيمة
            if category.lower() in ['صوت', 'voice']:
                hours = value // 3600
                minutes = (value % 3600) // 60
                formatted_value = f"{hours}ساعة {minutes}دقيقة"
            else:
                formatted_value = f"{value:,} {unit}"
            
            user = self.bot.get_user(user_id)
            display_name = user.display_name if user else username
            
            embed.add_field(
                name=f"{medal} {display_name}",
                value=f"{emoji} {formatted_value}",
                inline=True
            )
        
        embed.set_footer(text="💡 كن نشطاً لتظهر في هذه القائمة!")
        
        await ctx.send(embed=embed)

    @commands.command(name='نشاطي', aliases=['my_activity'])
    async def my_activity(self, ctx):
        """عرض نشاط المستخدم الشخصي"""
        user_data = await self.db.get_user(ctx.author.id)
        
        if not user_data:
            embed = discord.Embed(
                title="❌ لا توجد بيانات",
                description="لم نتمكن من العثور على بياناتك. تفاعل في السيرفر لبناء ملف نشاطك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        total_xp = user_data[2]
        voice_time = user_data[4]
        messages_sent = user_data[5]
        games_won = user_data[6]
        
        # تحويل وقت الصوت
        hours = voice_time // 3600
        minutes = (voice_time % 3600) // 60
        
        embed = discord.Embed(
            title=f"📊 نشاطك في {ctx.guild.name}",
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        
        # النشاط العام
        embed.add_field(
            name="⭐ النقاط",
            value=f"{total_xp:,} نقطة",
            inline=True
        )
        
        embed.add_field(
            name="🎤 النشاط الصوتي",
            value=f"{hours} ساعة {minutes} دقيقة",
            inline=True
        )
        
        embed.add_field(
            name="💬 الرسائل",
            value=f"{messages_sent:,} رسالة",
            inline=True
        )
        
        embed.add_field(
            name="🎮 الألعاب المكسوبة",
            value=f"{games_won:,} لعبة",
            inline=True
        )
        
        # ترتيب المستخدم
        # النقاط
        all_xp_users = await self.db.get_top_users(1000, 'total_xp')
        xp_rank = next((i+1 for i, (uid, _, _) in enumerate(all_xp_users) if uid == ctx.author.id), "غير محدد")
        
        # الصوت
        all_voice_users = await self.db.get_top_users(1000, 'voice_time')
        voice_rank = next((i+1 for i, (uid, _, _) in enumerate(all_voice_users) if uid == ctx.author.id), "غير محدد")
        
        embed.add_field(
            name="🏆 ترتيبك",
            value=f"**النقاط:** #{xp_rank}\n**الصوت:** #{voice_rank}",
            inline=True
        )
        
        # حساب المستوى التقديري
        level = int((total_xp / 100) ** 0.5) + 1
        xp_for_next = ((level) ** 2) * 100
        xp_needed = xp_for_next - total_xp
        
        embed.add_field(
            name="📈 المستوى",
            value=f"**المستوى:** {level}\n"
                 f"**للمستوى القادم:** {xp_needed:,} نقطة",
            inline=True
        )
        
        embed.set_footer(text="💡 استمر في التفاعل لزيادة نشاطك!")
        
        await ctx.send(embed=embed)

    @commands.command(name='وقت', aliases=['time'])
    async def time_command(self, ctx):
        """عرض الوقت الحالي"""
        now = datetime.utcnow()
        
        embed = discord.Embed(
            title="🕐 الوقت الحالي",
            color=0x00aaff,
            timestamp=now
        )
        
        embed.add_field(
            name="التوقيت العالمي (UTC)",
            value=now.strftime("%Y-%m-%d %H:%M:%S"),
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    # إضافة وقت بدء البوت
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.utcnow()
    
    await bot.add_cog(General(bot))
