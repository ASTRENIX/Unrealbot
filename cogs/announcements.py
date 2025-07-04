import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime
from database import Database

class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # تحميل الإعدادات
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @commands.command(name='إعلان', aliases=['announce'])
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx, channel: discord.TextChannel = None, *, message):
        """إرسال إعلان في قناة محددة"""
        if channel is None:
            channel = ctx.channel
        
        # التحقق من الصلاحيات في القناة المحددة
        if not channel.permissions_for(ctx.guild.me).send_messages:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"ليس لدي صلاحيات للكتابة في {channel.mention}",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # إنشاء الإعلان
        announcement_embed = discord.Embed(
            title="📢 إعلان من الإدارة",
            description=message,
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        announcement_embed.set_author(
            name=f"{ctx.author.display_name} - إدارة {ctx.guild.name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        
        announcement_embed.set_footer(
            text=f"سيرفر {ctx.guild.name}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        # إرسال الإعلان
        announcement_msg = await channel.send(embed=announcement_embed)
        
        # حفظ الإعلان في قاعدة البيانات
        await self.save_announcement(ctx.author.id, message, channel.id, announcement_msg.id)
        
        # رسالة تأكيد للمشرف
        if channel != ctx.channel:
            confirm_embed = discord.Embed(
                title="✅ تم إرسال الإعلان",
                description=f"تم إرسال الإعلان بنجاح في {channel.mention}\n"
                           f"[الذهاب للإعلان]({announcement_msg.jump_url})",
                color=0x00ff00
            )
            await ctx.send(embed=confirm_embed, delete_after=10)
        
        # حذف رسالة الأمر إذا كان مفعلاً
        if self.config.get('moderation', {}).get('auto_delete_commands', True):
            try:
                await ctx.message.delete()
            except:
                pass

    @commands.command(name='إعلان_مُنسق', aliases=['announce_embed'])
    @commands.has_permissions(manage_messages=True)
    async def announce_embed(self, ctx, channel: discord.TextChannel = None):
        """إنشاء إعلان منسق تفاعلي"""
        if channel is None:
            channel = ctx.channel
        
        # رسالة الإرشادات
        setup_embed = discord.Embed(
            title="📝 إنشاء إعلان منسق",
            description="سأقوم بسؤالك عن تفاصيل الإعلان خطوة بخطوة.\n"
                       "يمكنك كتابة 'إلغاء' في أي وقت لإلغاء العملية.",
            color=0x00aaff
        )
        await ctx.send(embed=setup_embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            # العنوان
            await ctx.send("**1️⃣ أدخل عنوان الإعلان:**")
            title_msg = await self.bot.wait_for('message', timeout=300.0, check=check)
            if title_msg.content.lower() == 'إلغاء':
                return await ctx.send("❌ تم إلغاء إنشاء الإعلان.")
            title = title_msg.content
            
            # المحتوى
            await ctx.send("**2️⃣ أدخل محتوى الإعلان:**")
            content_msg = await self.bot.wait_for('message', timeout=300.0, check=check)
            if content_msg.content.lower() == 'إلغاء':
                return await ctx.send("❌ تم إلغاء إنشاء الإعلان.")
            content = content_msg.content
            
            # اللون
            await ctx.send("**3️⃣ أدخل لون الإعلان (اختياري):**\n"
                          "أمثلة: أحمر، أزرق، أخضر، أصفر، بنفسجي، أو اتركه فارغاً للون الافتراضي")
            color_msg = await self.bot.wait_for('message', timeout=120.0, check=check)
            if color_msg.content.lower() == 'إلغاء':
                return await ctx.send("❌ تم إلغاء إنشاء الإعلان.")
            
            # تحديد اللون
            color_map = {
                'أحمر': 0xff0000,
                'أزرق': 0x0000ff,
                'أخضر': 0x00ff00,
                'أصفر': 0xffff00,
                'بنفسجي': 0x800080,
                'برتقالي': 0xffa500,
                'وردي': 0xffc0cb,
                'أبيض': 0xffffff,
                'أسود': 0x000000
            }
            
            color = color_map.get(color_msg.content.lower(), 0x00aaff)
            
            # إضافة صورة (اختياري)
            await ctx.send("**4️⃣ أدخل رابط صورة للإعلان (اختياري):**\n"
                          "أو اكتب 'لا' للتخطي")
            image_msg = await self.bot.wait_for('message', timeout=120.0, check=check)
            if image_msg.content.lower() == 'إلغاء':
                return await ctx.send("❌ تم إلغاء إنشاء الإعلان.")
            
            image_url = None
            if image_msg.content.lower() not in ['لا', 'تخطي', 'skip']:
                if image_msg.content.startswith('http'):
                    image_url = image_msg.content
            
            # إنشاء الإعلان النهائي
            final_embed = discord.Embed(
                title=title,
                description=content,
                color=color,
                timestamp=datetime.utcnow()
            )
            
            final_embed.set_author(
                name=f"{ctx.author.display_name} - إدارة {ctx.guild.name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            if image_url:
                final_embed.set_image(url=image_url)
            
            final_embed.set_footer(
                text=f"سيرفر {ctx.guild.name}",
                icon_url=ctx.guild.icon.url if ctx.guild.icon else None
            )
            
            # معاينة الإعلان
            preview_embed = discord.Embed(
                title="👀 معاينة الإعلان",
                description="هل تريد إرسال هذا الإعلان؟\n"
                           "اكتب 'نعم' للإرسال أو 'لا' للإلغاء",
                color=0xffaa00
            )
            
            await ctx.send(embed=preview_embed)
            await ctx.send(embed=final_embed)
            
            confirm_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            
            if confirm_msg.content.lower() in ['نعم', 'yes', 'y']:
                # إرسال الإعلان
                announcement_msg = await channel.send(embed=final_embed)
                
                # حفظ في قاعدة البيانات
                await self.save_announcement(ctx.author.id, f"{title}\n{content}", channel.id, announcement_msg.id)
                
                success_embed = discord.Embed(
                    title="✅ تم إرسال الإعلان",
                    description=f"تم إرسال الإعلان بنجاح في {channel.mention}\n"
                               f"[الذهاب للإعلان]({announcement_msg.jump_url})",
                    color=0x00ff00
                )
                await ctx.send(embed=success_embed)
            else:
                await ctx.send("❌ تم إلغاء إرسال الإعلان.")
                
        except asyncio.TimeoutError:
            await ctx.send("⏰ انتهت مهلة إنشاء الإعلان.")

    @commands.command(name='إعلان_سريع', aliases=['quick_announce'])
    @commands.has_permissions(manage_messages=True)
    async def quick_announce(self, ctx, *, message):
        """إعلان سريع في القناة الحالية"""
        # حذف رسالة الأمر
        try:
            await ctx.message.delete()
        except:
            pass
        
        # إرسال الإعلان البسيط
        embed = discord.Embed(
            description=f"📢 **{message}**",
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(
            text=f"بواسطة {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        
        announcement_msg = await ctx.send(embed=embed)
        
        # حفظ في قاعدة البيانات
        await self.save_announcement(ctx.author.id, message, ctx.channel.id, announcement_msg.id)

    @commands.command(name='إعلان_مهم', aliases=['important_announce'])
    @commands.has_permissions(administrator=True)
    async def important_announce(self, ctx, channel: discord.TextChannel = None, *, message):
        """إعلان مهم مع تنبيه الجميع"""
        if channel is None:
            channel = ctx.channel
        
        # التحقق من الصلاحيات
        if not channel.permissions_for(ctx.guild.me).mention_everyone:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لدي صلاحيات لتنبيه الجميع في هذه القناة",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # إنشاء الإعلان المهم
        important_embed = discord.Embed(
            title="🚨 إعلان مهم",
            description=message,
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        
        important_embed.set_author(
            name=f"إدارة {ctx.guild.name}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        important_embed.set_footer(text="مهم")
        
        # إرسال مع تنبيه الجميع
        announcement_msg = await channel.send("@everyone", embed=important_embed)
        
        # حفظ في قاعدة البيانات
        await self.save_announcement(ctx.author.id, f"[مهم] {message}", channel.id, announcement_msg.id)
        
        # رسالة تأكيد
        if channel != ctx.channel:
            confirm_embed = discord.Embed(
                title="🚨 تم إرسال الإعلان المهم",
                description=f"تم إرسال الإعلان مع تنبيه الجميع في {channel.mention}",
                color=0xff0000
            )
            await ctx.send(embed=confirm_embed, delete_after=10)

    @commands.command(name='سجل_الإعلانات', aliases=['announcement_history'])
    @commands.has_permissions(manage_messages=True)
    async def announcement_history(self, ctx, limit: int = 10):
        """عرض سجل الإعلانات الأخيرة"""
        if limit < 1 or limit > 50:
            limit = 10
        
        # الحصول على الإعلانات من قاعدة البيانات
        async with self.db.db_path and __import__('aiosqlite').connect(self.db.db_path) as db:
            cursor = await db.execute('''
                SELECT author_id, title, content, channel_id, message_id, timestamp 
                FROM announcements 
                WHERE author_id IN (SELECT user_id FROM users)
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            announcements = await cursor.fetchall()
        
        if not announcements:
            embed = discord.Embed(
                title="📋 سجل الإعلانات",
                description="لا توجد إعلانات محفوظة",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="📋 سجل الإعلانات الأخيرة",
            description=f"آخر {len(announcements)} إعلان:",
            color=0x00aaff
        )
        
        for i, (author_id, title, content, channel_id, message_id, timestamp) in enumerate(announcements, 1):
            author = self.bot.get_user(author_id)
            channel = self.bot.get_channel(channel_id)
            
            author_name = author.display_name if author else "مستخدم محذوف"
            channel_name = channel.mention if channel else "قناة محذوفة"
            
            # قص المحتوى إذا كان طويلاً
            preview = content[:100] + "..." if len(content) > 100 else content
            
            embed.add_field(
                name=f"{i}. {title if title else 'إعلان'}",
                value=f"**المرسل:** {author_name}\n"
                     f"**القناة:** {channel_name}\n"
                     f"**المحتوى:** {preview}\n"
                     f"**التاريخ:** {timestamp[:16]}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='حذف_إعلان', aliases=['delete_announcement'])
    @commands.has_permissions(manage_messages=True)
    async def delete_announcement(self, ctx, message_id: int):
        """حذف إعلان باستخدام معرف الرسالة"""
        try:
            # البحث عن الرسالة في جميع القنوات النصية
            message = None
            for channel in ctx.guild.text_channels:
                try:
                    message = await channel.fetch_message(message_id)
                    break
                except:
                    continue
            
            if not message:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="لم أتمكن من العثور على الرسالة المحددة",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
            
            # التحقق من أن الرسالة من البوت
            if message.author != self.bot.user:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="لا يمكنني حذف رسالة لم أرسلها",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
            
            # حذف الرسالة
            await message.delete()
            
            embed = discord.Embed(
                title="✅ تم الحذف",
                description=f"تم حذف الإعلان من {message.channel.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed, delete_after=10)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ خطأ",
                description="الرسالة غير موجودة أو تم حذفها مسبقاً",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لدي صلاحيات كافية لحذف هذه الرسالة",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    @commands.command(name='جدولة_إعلان', aliases=['schedule_announcement'])
    @commands.has_permissions(administrator=True)
    async def schedule_announcement(self, ctx, delay_minutes: int, channel: discord.TextChannel = None, *, message):
        """جدولة إعلان ليتم إرساله بعد وقت محدد"""
        if delay_minutes < 1 or delay_minutes > 10080:  # أسبوع كحد أقصى
            embed = discord.Embed(
                title="❌ خطأ",
                description="التأخير يجب أن يكون بين 1 دقيقة و 7 أيام (10080 دقيقة)",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        if channel is None:
            channel = ctx.channel
        
        # رسالة تأكيد الجدولة
        scheduled_time = datetime.utcnow().timestamp() + (delay_minutes * 60)
        
        embed = discord.Embed(
            title="⏰ تم جدولة الإعلان",
            description=f"سيتم إرسال الإعلان في {channel.mention} بعد {delay_minutes} دقيقة",
            color=0x00aaff
        )
        embed.add_field(name="المحتوى:", value=message[:200] + "..." if len(message) > 200 else message, inline=False)
        embed.add_field(name="وقت الإرسال:", value=f"<t:{int(scheduled_time)}:F>", inline=False)
        
        await ctx.send(embed=embed)
        
        # انتظار الوقت المحدد
        await asyncio.sleep(delay_minutes * 60)
        
        # إرسال الإعلان المجدول
        scheduled_embed = discord.Embed(
            title="📅 إعلان مجدول",
            description=message,
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
        
        scheduled_embed.set_author(
            name=f"{ctx.author.display_name} - إدارة {ctx.guild.name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        
        scheduled_embed.set_footer(text="إعلان مجدول")
        
        announcement_msg = await channel.send(embed=scheduled_embed)
        
        # حفظ في قاعدة البيانات
        await self.save_announcement(ctx.author.id, f"[مجدول] {message}", channel.id, announcement_msg.id)

    async def save_announcement(self, author_id, content, channel_id, message_id):
        """حفظ الإعلان في قاعدة البيانات"""
        try:
            async with __import__('aiosqlite').connect(self.db.db_path) as db:
                await db.execute('''
                    INSERT INTO announcements (author_id, title, content, channel_id, message_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (author_id, "إعلان", content, channel_id, message_id))
                await db.commit()
        except Exception as e:
            print(f"خطأ في حفظ الإعلان: {e}")

async def setup(bot):
    await bot.add_cog(Announcements(bot))
