import discord
from discord.ext import commands
import json
from datetime import datetime, timedelta
from database import Database

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # تحميل الإعدادات
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @commands.command(name='برا', aliases=['kick'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="لم يتم تحديد سبب"):
        """طرد عضو من السيرفر"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك طرد نفسك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك طرد عضو له رتبة أعلى أو مساوية لرتبتك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        try:
            # إرسال رسالة للعضو
            dm_embed = discord.Embed(
                title="👮‍♂️ تم طردك من السيرفر",
                description=f"**السيرفر:** {ctx.guild.name}\n"
                           f"**السبب:** {reason}\n"
                           f"**المشرف:** {ctx.author.mention}",
                color=0xff0000
            )
            await member.send(embed=dm_embed)
        except:
            pass
        
        # طرد العضو
        await member.kick(reason=f"بواسطة {ctx.author} - {reason}")
        
        # رسالة التأكيد
        embed = discord.Embed(
            title="👮‍♂️ تم الطرد",
            description=f"**العضو:** {member.mention}\n"
                       f"**السبب:** {reason}\n"
                       f"**المشرف:** {ctx.author.mention}",
            color=0xff6600
        )
        await ctx.send(embed=embed)
        
        # تسجيل في قناة السجلات
        await self.log_action(ctx.guild, "طرد", ctx.author, member, reason)

    @commands.command(name='بنعالي', aliases=['ban'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="لم يتم تحديد سبب"):
        """حظر عضو من السيرفر"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك حظر نفسك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك حظر عضو له رتبة أعلى أو مساوية لرتبتك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        try:
            # إرسال رسالة للعضو
            dm_embed = discord.Embed(
                title="🔨 تم حظرك من السيرفر",
                description=f"**السيرفر:** {ctx.guild.name}\n"
                           f"**السبب:** {reason}\n"
                           f"**المشرف:** {ctx.author.mention}",
                color=0xff0000
            )
            await member.send(embed=dm_embed)
        except:
            pass
        
        # حظر العضو
        await member.ban(reason=f"بواسطة {ctx.author} - {reason}")
        
        # رسالة التأكيد
        embed = discord.Embed(
            title="🔨 تم الحظر",
            description=f"**العضو:** {member.mention}\n"
                       f"**السبب:** {reason}\n"
                       f"**المشرف:** {ctx.author.mention}",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        
        # تسجيل في قناة السجلات
        await self.log_action(ctx.guild, "حظر", ctx.author, member, reason)

    @commands.command(name='سماح', aliases=['unban'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="لم يتم تحديد سبب"):
        """إلغاء حظر مستخدم"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=f"بواسطة {ctx.author} - {reason}")
            
            embed = discord.Embed(
                title="✅ تم إلغاء الحظر",
                description=f"**المستخدم:** {user.name}#{user.discriminator}\n"
                           f"**السبب:** {reason}\n"
                           f"**المشرف:** {ctx.author.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
            # تسجيل في قناة السجلات
            await self.log_action(ctx.guild, "إلغاء حظر", ctx.author, user, reason)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا المستخدم غير محظور أو غير موجود",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    @commands.command(name='اسكت', aliases=['mute'])
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 10, *, reason="لم يتم تحديد سبب"):
        """كتم عضو لفترة محددة (بالدقائق)"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك كتم نفسك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك كتم عضو له رتبة أعلى أو مساوية لرتبتك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # البحث عن دور الكتم أو إنشاؤه
        mute_role = discord.utils.get(ctx.guild.roles, name="مكتوم")
        if not mute_role:
            mute_role = await ctx.guild.create_role(
                name="مكتوم",
                permissions=discord.Permissions(send_messages=False, speak=False),
                reason="دور الكتم التلقائي"
            )
            
            # تطبيق إعدادات الكتم على جميع القنوات
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        
        # إضافة دور الكتم
        await member.add_roles(mute_role, reason=f"بواسطة {ctx.author} - {reason}")
        
        # رسالة التأكيد
        embed = discord.Embed(
            title="🔇 تم الكتم",
            description=f"**العضو:** {member.mention}\n"
                       f"**المدة:** {duration} دقيقة\n"
                       f"**السبب:** {reason}\n"
                       f"**المشرف:** {ctx.author.mention}",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        
        # إزالة الكتم تلقائياً بعد انتهاء المدة
        await asyncio.sleep(duration * 60)
        try:
            await member.remove_roles(mute_role, reason="انتهاء مدة الكتم")
            
            unmute_embed = discord.Embed(
                title="🔊 تم إلغاء الكتم",
                description=f"تم إلغاء كتم {member.mention} تلقائياً",
                color=0x00ff00
            )
            await ctx.send(embed=unmute_embed)
        except:
            pass
        
        # تسجيل في قناة السجلات
        await self.log_action(ctx.guild, "كتم", ctx.author, member, f"{reason} - {duration} دقيقة")

    @commands.command(name='تكلم', aliases=['unmute'])
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason="لم يتم تحديد سبب"):
        """إلغاء كتم عضو"""
        mute_role = discord.utils.get(ctx.guild.roles, name="مكتوم")
        
        if not mute_role or mute_role not in member.roles:
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا العضو غير مكتوم",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        await member.remove_roles(mute_role, reason=f"بواسطة {ctx.author} - {reason}")
        
        embed = discord.Embed(
            title="🔊 تم إلغاء الكتم",
            description=f"**العضو:** {member.mention}\n"
                       f"**السبب:** {reason}\n"
                       f"**المشرف:** {ctx.author.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        
        # تسجيل في قناة السجلات
        await self.log_action(ctx.guild, "إلغاء كتم", ctx.author, member, reason)

    @commands.command(name='عيب', aliases=['warn'])
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="لم يتم تحديد سبب"):
        """إعطاء تحذير لعضو"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك تحذير نفسك!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # إضافة التحذير إلى قاعدة البيانات
        await self.db.add_warning(member.id, ctx.author.id, reason)
        
        # الحصول على عدد التحذيرات
        warnings = await self.db.get_warnings(member.id)
        warn_count = len(warnings)
        
        embed = discord.Embed(
            title="⚠️ تحذير",
            description=f"**العضو:** {member.mention}\n"
                       f"**السبب:** {reason}\n"
                       f"**المشرف:** {ctx.author.mention}\n"
                       f"**عدد التحذيرات:** {warn_count}",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        
        # التحقق من الحد الأقصى للتحذيرات
        max_warns = self.config['moderation']['max_warns']
        if warn_count >= max_warns:
            # كتم تلقائي أو طرد حسب الإعدادات
            await self.auto_punish(ctx, member, warn_count)
        
        # تسجيل في قناة السجلات
        await self.log_action(ctx.guild, "تحذير", ctx.author, member, f"{reason} (التحذير رقم {warn_count})")

    @commands.command(name='عيوب', aliases=['warnings'])
    async def warnings(self, ctx, member: discord.Member = None):
        """عرض تحذيرات عضو"""
        if member is None:
            member = ctx.author
        
        warnings = await self.db.get_warnings(member.id)
        
        if not warnings:
            embed = discord.Embed(
                title="✅ لا توجد تحذيرات",
                description=f"{member.mention} ليس لديه أي تحذيرات",
                color=0x00ff00
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"⚠️ تحذيرات {member.display_name}",
            color=0xffaa00
        )
        
        for i, warning in enumerate(warnings[:10], 1):  # عرض آخر 10 تحذيرات
            moderator = self.bot.get_user(warning[2])
            mod_name = moderator.name if moderator else "مجهول"
            
            embed.add_field(
                name=f"التحذير رقم {i}",
                value=f"**السبب:** {warning[3]}\n"
                     f"**المشرف:** {mod_name}\n"
                     f"**التاريخ:** {warning[4][:10]}",
                inline=False
            )
        
        if len(warnings) > 10:
            embed.add_field(
                name="📊 المجموع",
                value=f"المجموع الكلي: {len(warnings)} تحذير",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='مسح', aliases=['clear', 'purge'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10, member: discord.Member = None):
        """مسح رسائل (افتراضي: 10 رسائل)"""
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن يكون عدد الرسائل بين 1 و 100",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        def check(message):
            if member:
                return message.author == member
            return True
        
        deleted = await ctx.channel.purge(limit=amount + 1, check=check)
        actual_deleted = len(deleted) - 1  # استثناء رسالة الأمر
        
        if member:
            description = f"تم مسح {actual_deleted} رسالة من {member.mention}"
        else:
            description = f"تم مسح {actual_deleted} رسالة"
        
        embed = discord.Embed(
            title="🗑️ تم مسح الرسائل",
            description=description,
            color=0x00ff00
        )
        
        # رسالة مؤقتة تختفي بعد 5 ثوان
        temp_msg = await ctx.send(embed=embed, delete_after=5)
        
        # تسجيل في قناة السجلات
        target_name = member.display_name if member else "الجميع"
        await self.log_action(ctx.guild, "مسح رسائل", ctx.author, None, f"تم مسح {actual_deleted} رسالة من {target_name}")

    async def auto_punish(self, ctx, member, warn_count):
        """معاقبة تلقائية عند الوصول للحد الأقصى من التحذيرات"""
        if warn_count == 3:
            # كتم لمدة ساعة
            mute_role = discord.utils.get(ctx.guild.roles, name="مكتوم")
            if mute_role:
                await member.add_roles(mute_role, reason="تجاوز الحد الأقصى للتحذيرات")
                
                embed = discord.Embed(
                    title="🔇 كتم تلقائي",
                    description=f"تم كتم {member.mention} تلقائياً لمدة ساعة بسبب تجاوز الحد الأقصى للتحذيرات",
                    color=0xff6600
                )
                await ctx.send(embed=embed)
                
                # إزالة الكتم بعد ساعة
                await asyncio.sleep(3600)
                try:
                    await member.remove_roles(mute_role, reason="انتهاء الكتم التلقائي")
                except:
                    pass
        
        elif warn_count >= 5:
            # طرد تلقائي
            try:
                await member.kick(reason="تجاوز الحد الأقصى للتحذيرات (5 تحذيرات)")
                
                embed = discord.Embed(
                    title="👮‍♂️ طرد تلقائي",
                    description=f"تم طرد {member.mention} تلقائياً بسبب تجاوز الحد الأقصى للتحذيرات (5 تحذيرات)",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
            except:
                pass

    async def log_action(self, guild, action, moderator, target, reason):
        """تسجيل إجراءات الإشراف في قناة السجلات"""
        log_channel_id = self.config['moderation']['log_channel_id']
        if not log_channel_id:
            return
        
        log_channel = guild.get_channel(log_channel_id)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"📋 إجراء إشرافي: {action}",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="المشرف", value=moderator.mention, inline=True)
        if target:
            embed.add_field(name="الهدف", value=target.mention, inline=True)
        embed.add_field(name="السبب", value=reason, inline=False)
        
        embed.set_footer(text=f"معرف المشرف: {moderator.id}")
        
        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
