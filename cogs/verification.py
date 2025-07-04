import discord
from discord.ext import commands
import json
from database import Database

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # تحميل الإعدادات
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @commands.command(name='إعداد_التحقق', aliases=['setup_verification'])
    @commands.has_permissions(administrator=True)
    async def setup_verification(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
        """إعداد نظام التحقق"""
        if channel is None:
            channel = ctx.channel
        
        if role is None:
            # إنشاء دور العضو المتحقق
            role = await ctx.guild.create_role(
                name="عضو متحقق",
                color=discord.Color.green(),
                permissions=discord.Permissions(
                    send_messages=True,
                    read_messages=True,
                    connect=True,
                    speak=True
                ),
                reason="دور التحقق التلقائي"
            )
        
        # تحديث الإعدادات
        self.config['verification_channel_id'] = channel.id
        self.config['verified_role_id'] = role.id
        
        # حفظ الإعدادات
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
        
        # إرسال رسالة التحقق
        verification_embed = discord.Embed(
            title="🔒 التحقق من العضوية",
            description=self.config['verification']['message'],
            color=0x00ff00
        )
        verification_embed.add_field(
            name="كيفية التحقق:",
            value="اضغط على ✅ للحصول على دور العضو المتحقق\n"
                 "هذا سيمنحك الوصول لجميع قنوات السيرفر",
            inline=False
        )
        verification_embed.set_footer(text=f"سيرفر {ctx.guild.name}")
        
        verification_msg = await channel.send(embed=verification_embed)
        await verification_msg.add_reaction("✅")
        
        # رسالة التأكيد للمشرف
        setup_embed = discord.Embed(
            title="✅ تم إعداد التحقق",
            description=f"**القناة:** {channel.mention}\n"
                       f"**الدور:** {role.mention}\n"
                       f"**رسالة التحقق:** [اذهب إلى الرسالة]({verification_msg.jump_url})",
            color=0x00ff00
        )
        await ctx.send(embed=setup_embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """معالج التفاعل مع رسالة التحقق"""
        # تجاهل تفاعلات البوت
        if payload.user_id == self.bot.user.id:
            return
        
        # التحقق من أن التفاعل في قناة التحقق
        if payload.channel_id != self.config.get('verification_channel_id'):
            return
        
        # التحقق من الإيموجي الصحيح
        if str(payload.emoji) != self.config['verification']['emoji']:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # الحصول على دور التحقق
        verified_role_id = self.config.get('verified_role_id')
        if not verified_role_id:
            return
        
        verified_role = guild.get_role(verified_role_id)
        if not verified_role:
            return
        
        # التحقق من أن العضو لا يملك الدور بالفعل
        if verified_role in member.roles:
            return
        
        try:
            # إعطاء دور التحقق
            await member.add_roles(verified_role, reason="التحقق التلقائي")
            
            # تحديث قاعدة البيانات
            await self.db.verify_user(member.id)
            
            # إرسال رسالة ترحيب خاصة
            welcome_embed = discord.Embed(
                title="🎉 مرحباً بك!",
                description=f"تم التحقق من عضويتك بنجاح {member.mention}!\n"
                           f"يمكنك الآن الوصول لجميع قنوات السيرفر والاستمتاع بالمحتوى.",
                color=0x00ff00
            )
            welcome_embed.add_field(
                name="🎮 ماذا يمكنك فعله الآن؟",
                value="• المشاركة في جميع القنوات النصية\n"
                     "• الانضمام للقنوات الصوتية\n"
                     "• لعب الألعاب وكسب النقاط\n"
                     "• استخدام أوامر الموسيقى\n"
                     "• المشاركة في الفعاليات",
                inline=False
            )
            welcome_embed.add_field(
                name="❓ تحتاج مساعدة؟",
                value="استخدم الأمر `-help` لرؤية جميع الأوامر المتاحة",
                inline=False
            )
            welcome_embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            welcome_embed.set_footer(text=f"سيرفر {guild.name}")
            
            # محاولة إرسال رسالة خاصة
            try:
                await member.send(embed=welcome_embed)
            except:
                # إذا فشل الإرسال الخاص، إرسال في القناة
                channel = self.bot.get_channel(payload.channel_id)
                if channel:
                    await channel.send(embed=welcome_embed, delete_after=30)
            
            # تسجيل في قناة السجلات
            await self.log_verification(guild, member)
            
        except discord.Forbidden:
            # لا توجد صلاحيات كافية
            pass
        except Exception as e:
            print(f"خطأ في التحقق: {e}")

    @commands.command(name='تحقق_يدوي', aliases=['manual_verify'])
    @commands.has_permissions(manage_roles=True)
    async def manual_verify(self, ctx, member: discord.Member):
        """تحقق يدوي من عضو"""
        verified_role_id = self.config.get('verified_role_id')
        if not verified_role_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم إعداد نظام التحقق بعد. استخدم `-إعداد_التحقق` أولاً.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        verified_role = ctx.guild.get_role(verified_role_id)
        if not verified_role:
            embed = discord.Embed(
                title="❌ خطأ",
                description="دور التحقق غير موجود.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        if verified_role in member.roles:
            embed = discord.Embed(
                title="⚠️ تنبيه",
                description=f"{member.mention} متحقق بالفعل.",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        try:
            await member.add_roles(verified_role, reason=f"تحقق يدوي بواسطة {ctx.author}")
            await self.db.verify_user(member.id)
            
            embed = discord.Embed(
                title="✅ تم التحقق",
                description=f"تم التحقق من {member.mention} بنجاح بواسطة {ctx.author.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
            # تسجيل في قناة السجلات
            await self.log_verification(ctx.guild, member, manual_by=ctx.author)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لدي صلاحيات كافية لإعطاء الأدوار.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    @commands.command(name='إلغاء_تحقق', aliases=['unverify'])
    @commands.has_permissions(manage_roles=True)
    async def unverify(self, ctx, member: discord.Member, *, reason="لم يتم تحديد سبب"):
        """إلغاء تحقق عضو"""
        verified_role_id = self.config.get('verified_role_id')
        if not verified_role_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم إعداد نظام التحقق بعد.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        verified_role = ctx.guild.get_role(verified_role_id)
        if not verified_role or verified_role not in member.roles:
            embed = discord.Embed(
                title="⚠️ تنبيه",
                description=f"{member.mention} غير متحقق.",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        try:
            await member.remove_roles(verified_role, reason=f"إلغاء تحقق بواسطة {ctx.author} - {reason}")
            
            embed = discord.Embed(
                title="❌ تم إلغاء التحقق",
                description=f"تم إلغاء تحقق {member.mention}\n**السبب:** {reason}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لدي صلاحيات كافية لإزالة الأدوار.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    @commands.command(name='حالة_التحقق', aliases=['verification_status'])
    async def verification_status(self, ctx, member: discord.Member = None):
        """عرض حالة التحقق لعضو"""
        if member is None:
            member = ctx.author
        
        verified_role_id = self.config.get('verified_role_id')
        is_verified = False
        
        if verified_role_id:
            verified_role = ctx.guild.get_role(verified_role_id)
            if verified_role and verified_role in member.roles:
                is_verified = True
        
        # الحصول على بيانات من قاعدة البيانات
        user_data = await self.db.get_user(member.id)
        
        embed = discord.Embed(
            title=f"🔍 حالة التحقق - {member.display_name}",
            color=0x00ff00 if is_verified else 0xff0000
        )
        
        status_text = "✅ متحقق" if is_verified else "❌ غير متحقق"
        embed.add_field(name="الحالة:", value=status_text, inline=True)
        
        if user_data:
            join_date = user_data[8] if len(user_data) > 8 else "غير محدد"
            embed.add_field(name="تاريخ الانضمام:", value=join_date[:10] if join_date != "غير محدد" else join_date, inline=True)
            
            total_xp = user_data[2] if len(user_data) > 2 else 0
            embed.add_field(name="إجمالي النقاط:", value=f"{total_xp} نقطة", inline=True)
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        if not is_verified:
            verification_channel_id = self.config.get('verification_channel_id')
            if verification_channel_id:
                verification_channel = ctx.guild.get_channel(verification_channel_id)
                if verification_channel:
                    embed.add_field(
                        name="كيفية التحقق:",
                        value=f"اذهب إلى {verification_channel.mention} واضغط على ✅",
                        inline=False
                    )
        
        await ctx.send(embed=embed)

    @commands.command(name='إحصائيات_التحقق', aliases=['verification_stats'])
    @commands.has_permissions(manage_guild=True)
    async def verification_stats(self, ctx):
        """عرض إحصائيات التحقق في السيرفر"""
        verified_role_id = self.config.get('verified_role_id')
        
        total_members = ctx.guild.member_count
        verified_count = 0
        
        if verified_role_id:
            verified_role = ctx.guild.get_role(verified_role_id)
            if verified_role:
                verified_count = len(verified_role.members)
        
        unverified_count = total_members - verified_count
        verification_rate = (verified_count / total_members * 100) if total_members > 0 else 0
        
        embed = discord.Embed(
            title="📊 إحصائيات التحقق",
            color=0x00ff00
        )
        
        embed.add_field(name="إجمالي الأعضاء:", value=f"{total_members:,}", inline=True)
        embed.add_field(name="الأعضاء المتحققون:", value=f"{verified_count:,}", inline=True)
        embed.add_field(name="الأعضاء غير المتحققين:", value=f"{unverified_count:,}", inline=True)
        embed.add_field(name="معدل التحقق:", value=f"{verification_rate:.1f}%", inline=True)
        
        if verified_role_id:
            verified_role = ctx.guild.get_role(verified_role_id)
            embed.add_field(name="دور التحقق:", value=verified_role.mention if verified_role else "غير موجود", inline=True)
        
        verification_channel_id = self.config.get('verification_channel_id')
        if verification_channel_id:
            verification_channel = ctx.guild.get_channel(verification_channel_id)
            embed.add_field(name="قناة التحقق:", value=verification_channel.mention if verification_channel else "غير موجودة", inline=True)
        
        embed.set_footer(text=f"سيرفر {ctx.guild.name}")
        
        await ctx.send(embed=embed)

    async def log_verification(self, guild, member, manual_by=None):
        """تسجيل عملية التحقق في قناة السجلات"""
        log_channel_id = self.config.get('moderation', {}).get('log_channel_id')
        if not log_channel_id:
            return
        
        log_channel = guild.get_channel(log_channel_id)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="✅ تحقق جديد",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="العضو:", value=f"{member.mention}\n({member.name}#{member.discriminator})", inline=True)
        embed.add_field(name="معرف العضو:", value=member.id, inline=True)
        
        if manual_by:
            embed.add_field(name="تحقق بواسطة:", value=manual_by.mention, inline=True)
            embed.add_field(name="نوع التحقق:", value="يدوي", inline=True)
        else:
            embed.add_field(name="نوع التحقق:", value="تلقائي", inline=True)
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"سيرفر {guild.name}")
        
        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Verification(bot))
