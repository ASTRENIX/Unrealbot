import discord
from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime, timedelta
from database import Database

class VoiceRewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # تحميل الإعدادات
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # تتبع أنشطة الصوت
        self.voice_sessions = {}
        
        # بدء المهام الدورية
        self.update_voice_rewards.start()
        self.daily_voice_summary.start()

    def cog_unload(self):
        """إنهاء المهام عند إلغاء تحميل الكوج"""
        self.update_voice_rewards.cancel()
        self.daily_voice_summary.cancel()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """متابعة تغييرات حالة الصوت"""
        if member.bot:
            return
        
        current_time = datetime.utcnow()
        user_id = member.id
        
        # العضو انضم لقناة صوتية
        if before.channel is None and after.channel is not None:
            self.voice_sessions[user_id] = {
                'channel_id': after.channel.id,
                'join_time': current_time,
                'total_time': 0
            }
            await self.on_voice_join(member, after.channel)
        
        # العضو غادر القناة الصوتية
        elif before.channel is not None and after.channel is None:
            if user_id in self.voice_sessions:
                session = self.voice_sessions[user_id]
                duration = (current_time - session['join_time']).total_seconds()
                
                # تسجيل الجلسة في قاعدة البيانات
                await self.db.log_voice_activity(
                    user_id, 
                    session['channel_id'], 
                    session['join_time'], 
                    current_time
                )
                
                await self.on_voice_leave(member, before.channel, duration)
                del self.voice_sessions[user_id]
        
        # العضو انتقل بين القنوات
        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            if user_id in self.voice_sessions:
                # إنهاء الجلسة في القناة السابقة
                session = self.voice_sessions[user_id]
                duration = (current_time - session['join_time']).total_seconds()
                
                await self.db.log_voice_activity(
                    user_id, 
                    session['channel_id'], 
                    session['join_time'], 
                    current_time
                )
                
                # بدء جلسة جديدة في القناة الجديدة
                self.voice_sessions[user_id] = {
                    'channel_id': after.channel.id,
                    'join_time': current_time,
                    'total_time': session.get('total_time', 0) + duration
                }

    async def on_voice_join(self, member, channel):
        """معالج انضمام العضو للقناة الصوتية"""
        # رسالة ترحيب (اختيارية)
        if self.config['voice_rewards']['enabled']:
            embed = discord.Embed(
                title="🎤 مرحباً بك!",
                description=f"{member.mention} انضم إلى {channel.name}\n"
                           f"ستحصل على {self.config['voice_rewards']['xp_per_minute']} نقطة لكل دقيقة!",
                color=0x00ff00
            )
            
            # البحث عن قناة مناسبة لإرسال الرسالة
            text_channel = None
            for ch in member.guild.text_channels:
                if ch.name in ['𝚂𝚙𝚢']:
                    text_channel = ch
                    break
            
            if text_channel and text_channel.permissions_for(member.guild.me).send_messages:
                await text_channel.send(embed=embed, delete_after=10)

    async def on_voice_leave(self, member, channel, duration_seconds):
        """معالج مغادرة العضو للقناة الصوتية"""
        if not self.config['voice_rewards']['enabled'] or duration_seconds < 60:
            return
        
        # حساب المكافآت
        minutes = int(duration_seconds // 60)
        base_xp = minutes * self.config['voice_rewards']['xp_per_minute']
        
        # مكافآت إضافية للقنوات الخاصة
        bonus_xp = 0
        bonus_channels = self.config['voice_rewards'].get('bonus_channels', {})
        if str(channel.id) in bonus_channels:
            bonus_multiplier = bonus_channels[str(channel.id)]
            bonus_xp = int(base_xp * bonus_multiplier - base_xp)
        
        total_xp = base_xp + bonus_xp
        
        # إضافة النقاط للمستخدم
        await self.db.update_user_xp(member.id, total_xp)
        
        # التحقق من الترقيات
        await self.check_voice_role_rewards(member, total_xp)
        
        # رسالة المكافأة
        embed = discord.Embed(
            title="🎉 مكافأة الصوت",
            description=f"{member.mention} حصل على مكافأة الصوت!",
            color=0x00ff00
        )
        
        embed.add_field(name="⏰ الوقت المقضي:", value=f"{minutes} دقيقة", inline=True)
        embed.add_field(name="📍 القناة:", value=channel.name, inline=True)
        embed.add_field(name="⭐ النقاط المكتسبة:", value=f"{total_xp} نقطة", inline=True)
        
        if bonus_xp > 0:
            embed.add_field(name="🎁 مكافأة إضافية:", value=f"+{bonus_xp} نقطة", inline=True)
        
        # البحث عن قناة مناسبة لإرسال الرسالة
        text_channel = None
        for ch in member.guild.text_channels:
            if ch.name in ['عام', 'general', 'chat', 'rewards']:
                text_channel = ch
                break
        
        if text_channel and text_channel.permissions_for(member.guild.me).send_messages:
            await text_channel.send(embed=embed, delete_after=15)

    async def check_voice_role_rewards(self, member, new_xp):
        """التحقق من استحقاق أدوار جديدة"""
        # الحصول على إجمالي النقاط
        user_data = await self.db.get_user(member.id)
        if not user_data:
            return
        
        total_xp = user_data[2]  # total_xp column
        reward_roles = self.config['voice_rewards'].get('reward_roles', {})
        
        for required_xp, role_name in reward_roles.items():
            required_xp = int(required_xp)
            
            # إذا كان المستخدم يستحق هذا الدور
            if total_xp >= required_xp:
                # البحث عن الدور أو إنشاؤه
                role = discord.utils.get(member.guild.roles, name=role_name)
                if not role:
                    try:
                        role = await member.guild.create_role(
                            name=role_name,
                            color=discord.Color.gold(),
                            reason="دور مكافأة صوتية تلقائي"
                        )
                    except:
                        continue
                
                # إعطاء الدور إذا لم يكن يملكه
                if role not in member.roles:
                    try:
                        await member.add_roles(role, reason=f"مكافأة صوتية - {total_xp} نقطة")
                        
                        # رسالة تهنئة
                        congrats_embed = discord.Embed(
                            title="🏆 تهانينا!",
                            description=f"{member.mention} حصل على دور جديد!",
                            color=0xffd700
                        )
                        congrats_embed.add_field(name="🎭 الدور الجديد:", value=role.mention, inline=True)
                        congrats_embed.add_field(name="⭐ النقاط المطلوبة:", value=f"{required_xp:,} نقطة", inline=True)
                        congrats_embed.add_field(name="📊 نقاطك الحالية:", value=f"{total_xp:,} نقطة", inline=True)
                        
                        # البحث عن قناة للإعلان
                        announce_channel = None
                        for ch in member.guild.text_channels:
                            if ch.name in ['إعلانات', 'announcements', 'general', 'عام']:
                                announce_channel = ch
                                break
                        
                        if announce_channel and announce_channel.permissions_for(member.guild.me).send_messages:
                            await announce_channel.send(embed=congrats_embed)
                    
                    except discord.Forbidden:
                        pass

    @tasks.loop(minutes=5)
    async def update_voice_rewards(self):
        """تحديث دوري لمكافآت الصوت للأعضاء المتصلين حالياً"""
        if not self.config['voice_rewards']['enabled']:
            return
        
        current_time = datetime.utcnow()
        
        for user_id, session in list(self.voice_sessions.items()):
            # حساب الوقت المنقضي منذ آخر تحديث
            time_diff = (current_time - session['join_time']).total_seconds()
            
            if time_diff >= 300:  # كل 5 دقائق
                minutes = int(time_diff // 60)
                xp_earned = minutes * self.config['voice_rewards']['xp_per_minute']
                
                # تحديث النقاط
                await self.db.update_user_xp(user_id, xp_earned)
                
                # إعادة تعيين وقت البداية
                session['join_time'] = current_time
                session['total_time'] = session.get('total_time', 0) + time_diff

    @update_voice_rewards.before_loop
    async def before_update_voice_rewards(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24)
    async def daily_voice_summary(self):
        """ملخص يومي لنشاط الصوت"""
        if not self.config['voice_rewards']['enabled']:
            return
        
        # الحصول على أفضل المستخدمين اليوم
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # البحث عن قناة الإعلانات
        announce_channel = None
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.name in ['تقارير-يومية', 'daily-reports', 'عام', 'general']:
                    announce_channel = channel
                    break
            if announce_channel:
                break
        
        if not announce_channel:
            return
        
        embed = discord.Embed(
            title="📊 ملخص النشاط الصوتي اليومي",
            description="إليكم أكثر الأعضاء نشاطاً في القنوات الصوتية اليوم:",
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        # الحصول على أفضل 5 أعضاء
        top_users = await self.db.get_top_users(5, 'voice_time')
        
        if top_users:
            for i, (user_id, username, voice_time) in enumerate(top_users, 1):
                hours = voice_time // 3600
                minutes = (voice_time % 3600) // 60
                
                embed.add_field(
                    name=f"#{i} {username}",
                    value=f"⏰ {hours}ساعة {minutes}دقيقة\n"
                         f"📍 في القنوات الصوتية",
                    inline=True
                )
        else:
            embed.add_field(
                name="لا توجد بيانات",
                value="لم يشارك أي عضو في القنوات الصوتية اليوم",
                inline=False
            )
        
        embed.set_footer(text="تفاعل في القنوات الصوتية لتظهر في التقرير القادم!")
        
        await announce_channel.send(embed=embed)

    @daily_voice_summary.before_loop
    async def before_daily_voice_summary(self):
        await self.bot.wait_until_ready()

    @commands.command(name='نشاط_الصوت', aliases=['voice_activity'])
    async def voice_activity(self, ctx, member: discord.Member = None):
        """عرض إحصائيات نشاط الصوت"""
        if member is None:
            member = ctx.author
        
        user_data = await self.db.get_user(member.id)
        if not user_data:
            embed = discord.Embed(
                title="❌ لا توجد بيانات",
                description=f"{member.display_name} لم يشارك في أي نشاط صوتي بعد",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        total_xp = user_data[2]
        voice_time = user_data[4]
        
        # تحويل الوقت
        hours = voice_time // 3600
        minutes = (voice_time % 3600) // 60
        
        embed = discord.Embed(
            title=f"🎤 نشاط الصوت - {member.display_name}",
            color=0x00ff00
        )
        
        embed.add_field(name="⏰ إجمالي الوقت:", value=f"{hours} ساعة {minutes} دقيقة", inline=True)
        embed.add_field(name="⭐ إجمالي النقاط:", value=f"{total_xp:,} نقطة", inline=True)
        
        # حساب متوسط الوقت اليومي (تقديري)
        if voice_time > 0:
            daily_average = voice_time // max(1, (datetime.utcnow() - datetime.fromisoformat(user_data[8])).days or 1)
            daily_hours = daily_average // 3600
            daily_minutes = (daily_average % 3600) // 60
            embed.add_field(name="📈 متوسط يومي:", value=f"{daily_hours}ساعة {daily_minutes}دقيقة", inline=True)
        
        # التحقق من الأدوار المتاحة
        reward_roles = self.config['voice_rewards'].get('reward_roles', {})
        next_reward = None
        current_rewards = []
        
        for required_xp, role_name in reward_roles.items():
            required_xp = int(required_xp)
            if total_xp >= required_xp:
                current_rewards.append(role_name)
            elif next_reward is None or required_xp < next_reward[0]:
                next_reward = (required_xp, role_name)
        
        if current_rewards:
            embed.add_field(
                name="🏆 الأدوار الحالية:",
                value="\n".join([f"• {role}" for role in current_rewards]),
                inline=False
            )
        
        if next_reward:
            remaining_xp = next_reward[0] - total_xp
            embed.add_field(
                name="🎯 الدور القادم:",
                value=f"**{next_reward[1]}**\n"
                     f"تحتاج {remaining_xp:,} نقطة إضافية",
                inline=False
            )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text="💡 امضي وقتاً أكثر في القنوات الصوتية لكسب المزيد من النقاط!")
        
        await ctx.send(embed=embed)

    @commands.command(name='لوحة_الصوت', aliases=['vc_leaderboard'])
    async def voice_leaderboard(self, ctx):
        """عرض لوحة المتصدرين في نشاط الصوت"""
        top_users = await self.db.get_top_users(10, 'voice_time')
        
        if not top_users:
            embed = discord.Embed(
                title="📊 لوحة المتصدرين - النشاط الصوتي",
                description="لا توجد بيانات متاحة حتى الآن",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="🏆 لوحة المتصدرين - النشاط الصوتي",
            description="أكثر الأعضاء نشاطاً في القنوات الصوتية:",
            color=0xffd700
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, username, voice_time) in enumerate(top_users):
            medal = medals[i] if i < 3 else f"#{i+1}"
            
            hours = voice_time // 3600
            minutes = (voice_time % 3600) // 60
            
            user = self.bot.get_user(user_id)
            display_name = user.display_name if user else username
            
            embed.add_field(
                name=f"{medal} {display_name}",
                value=f"⏰ {hours}ساعة {minutes}دقيقة",
                inline=True
            )
        
        embed.set_footer(text="💡 انضم للقنوات الصوتية لتكسب نقاط وتظهر في هذه القائمة!")
        
        await ctx.send(embed=embed)

    @commands.command(name='إعداد_مكافآت_الصوت', aliases=['setup_voice_rewards'])
    @commands.has_permissions(administrator=True)
    async def setup_voice_rewards(self, ctx, xp_per_minute: int = 2):
        """إعداد نظام مكافآت الصوت"""
        if xp_per_minute < 1 or xp_per_minute > 10:
            embed = discord.Embed(
                title="❌ خطأ",
                description="النقاط لكل دقيقة يجب أن تكون بين 1 و 10",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        self.config['voice_rewards']['enabled'] = True
        self.config['voice_rewards']['xp_per_minute'] = xp_per_minute
        
        # حفظ الإعدادات
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
        
        embed = discord.Embed(
            title="✅ تم إعداد مكافآت الصوت",
            description=f"**النقاط لكل دقيقة:** {xp_per_minute}\n"
                       f"**الحالة:** مفعّل\n\n"
                       f"الآن سيحصل الأعضاء على {xp_per_minute} نقطة لكل دقيقة يقضونها في القنوات الصوتية!",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🎭 الأدوار التلقائية:",
            value="سيتم إعطاء أدوار تلقائياً عند الوصول لنقاط معينة:\n"
                 "• 100 نقطة: متفاعل\n"
                 "• 500 نقطة: نشيط\n"
                 "• 1000 نقطة: عضو مميز\n"
                 "• 2500 نقطة: خبير الصوت",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VoiceRewards(bot))
