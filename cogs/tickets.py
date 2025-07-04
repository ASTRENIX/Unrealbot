import discord
from discord.ext import commands
import json
import asyncio
import random
import string
from datetime import datetime
from database import Database

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # تحميل الإعدادات
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # فئات التذاكر
        self.ticket_categories = {
            'دعم_فني': {
                'name': 'دعم فني',
                'emoji': '🔧',
                'description': 'مشاكل تقنية وأخطاء'
            },
            'شكوى': {
                'name': 'شكوى',
                'emoji': '⚠️',
                'description': 'الإبلاغ عن مخالفات أو مشاكل'
            },
            'اقتراح': {
                'name': 'اقتراح',
                'emoji': '💡',
                'description': 'اقتراحات لتحسين السيرفر'
            },
            'استفسار': {
                'name': 'استفسار عام',
                'emoji': '❓',
                'description': 'أسئلة عامة ومعلومات'
            },
            'طلب_دور': {
                'name': 'طلب دور',
                'emoji': '🎭',
                'description': 'طلب أدوار خاصة'
            },
            'أخرى': {
                'name': 'أخرى',
                'emoji': '📝',
                'description': 'مواضيع أخرى'
            }
        }

    def generate_ticket_id(self):
        """توليد معرف تذكرة فريد"""
        return 'ticket-' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    @commands.command(name='إعداد_التذاكر', aliases=['setup_tickets'])
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx, category: discord.CategoryChannel = None):
        """إعداد نظام التذاكر"""
        if category is None:
            # إنشاء فئة جديدة للتذاكر
            category = await ctx.guild.create_category(
                name="نظام التكت",
                reason="إعداد نظام التذاكر"
            )
        
        # تحديث الإعدادات
        self.config['tickets'] = {
            'enabled': True,
            'category_id': category.id,
            'support_role_ids': [],
            'log_channel_id': None,
            'max_tickets_per_user': 3
        }
        
        # حفظ الإعدادات
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
        
        # إنشاء قناة إنشاء التذاكر
        ticket_channel = await category.create_text_channel(
            name="إنشاء-تذكرة",
            topic="اضغط على الرقم المناسب لإنشاء تذكرة دعم"
        )
        
        # رسالة إنشاء التذاكر
        embed = discord.Embed(
            title="🎫 نظام التذاكر",
            description="مرحباً بك في نظام التذاكر!\n"
                       "اختر نوع التذكرة المناسب لطلبك:",
            color=0x00aaff
        )
        
        # إضافة الفئات
        for category_id, info in self.ticket_categories.items():
            embed.add_field(
                name=f"{info['emoji']} {info['name']}",
                value=info['description'],
                inline=True
            )
        
        embed.add_field(
            name="📋 كيفية الاستخدام",
            value="• اضغط على الرقم المناسب أسفل هذه الرسالة\n"
                 "• سيتم إنشاء قناة خاصة لك\n"
                 "• اشرح مشكلتك أو طلبك بالتفصيل\n"
                 "• انتظر رد فريق الدعم",
            inline=False
        )
        
        embed.set_footer(text="يمكنك إنشاء حتى 3 تذاكر في نفس الوقت")
        
        message = await ticket_channel.send(embed=embed)
        
        # إضافة ردود الأفعال
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
        for i, reaction in enumerate(reactions[:len(self.ticket_categories)]):
            await message.add_reaction(reaction)
        
        # رسالة تأكيد
        setup_embed = discord.Embed(
            title="✅ تم إعداد نظام التذاكر",
            description=f"**الفئة:** {category.mention}\n"
                       f"**قناة الإنشاء:** {ticket_channel.mention}\n"
                       f"**عدد الفئات:** {len(self.ticket_categories)}",
            color=0x00ff00
        )
        await ctx.send(embed=setup_embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """معالج إنشاء التذاكر عبر التفاعل"""
        # تجاهل تفاعلات البوت
        if payload.user_id == self.bot.user.id:
            return
        
        # التحقق من نظام التذاكر
        if not self.config.get('tickets', {}).get('enabled', False):
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # التحقق من القناة
        channel = guild.get_channel(payload.channel_id)
        if not channel or channel.name != "إنشاء-تذكرة":
            return
        
        # التحقق من التفاعل
        reaction_map = {
            '1️⃣': 'دعم_فني',
            '2️⃣': 'شكوى',
            '3️⃣': 'اقتراح',
            '4️⃣': 'استفسار',
            '5️⃣': 'طلب_دور',
            '6️⃣': 'أخرى'
        }
        
        category_key = reaction_map.get(str(payload.emoji))
        if not category_key:
            return
        
        # إزالة التفاعل
        try:
            await channel.get_partial_message(payload.message_id).remove_reaction(payload.emoji, member)
        except:
            pass
        
        # التحقق من عدد التذاكر المفتوحة
        user_tickets = await self.db.get_user_tickets(member.id, 'open')
        max_tickets = self.config.get('tickets', {}).get('max_tickets_per_user', 3)
        
        if len(user_tickets) >= max_tickets:
            try:
                embed = discord.Embed(
                    title="❌ تجاوز الحد الأقصى",
                    description=f"لديك {len(user_tickets)} تذاكر مفتوحة بالفعل.\n"
                               f"الحد الأقصى هو {max_tickets} تذاكر.\n"
                               "يرجى إغلاق إحدى التذاكر أولاً.",
                    color=0xff0000
                )
                await member.send(embed=embed)
            except:
                pass
            return
        
        # إنشاء التذكرة
        await self.create_ticket(member, category_key)

    async def create_ticket(self, member, category_key):
        """إنشاء تذكرة جديدة"""
        guild = member.guild
        category_info = self.ticket_categories[category_key]
        ticket_id = self.generate_ticket_id()
        
        # الحصول على فئة التذاكر
        tickets_category_id = self.config.get('tickets', {}).get('category_id')
        tickets_category = guild.get_channel(tickets_category_id) if tickets_category_id else None
        
        if not tickets_category:
            return
        
        # إنشاء القناة
        channel_name = f"🎫┃{category_info['name']}-{member.display_name}"[:100]
        
        # إعدادات الصلاحيات
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_messages=True,
                read_message_history=True
            )
        }
        
        # إضافة أدوار الدعم
        support_roles = self.config.get('tickets', {}).get('support_role_ids', [])
        for role_id in support_roles:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
        
        try:
            ticket_channel = await tickets_category.create_text_channel(
                name=channel_name,
                topic=f"تذكرة {category_info['name']} - {member.display_name} | ID: {ticket_id}",
                overwrites=overwrites
            )
            
            # حفظ في قاعدة البيانات
            await self.db.create_ticket(
                ticket_id=ticket_id,
                user_id=member.id,
                channel_id=ticket_channel.id,
                category=category_key,
                title=f"تذكرة {category_info['name']}",
                description=f"تذكرة {category_info['name']} من {member.display_name}"
            )
            
            # رسالة الترحيب في التذكرة
            welcome_embed = discord.Embed(
                title=f"{category_info['emoji']} تذكرة {category_info['name']}",
                description=f"مرحباً {member.mention}!\n"
                           f"تم إنشاء تذكرتك بنجاح.\n\n"
                           f"**معرف التذكرة:** `{ticket_id}`\n"
                           f"**النوع:** {category_info['name']}\n\n"
                           f"يرجى شرح مشكلتك أو طلبك بالتفصيل.\n"
                           f"سيقوم فريق الدعم بالرد عليك في أقرب وقت.",
                color=0x00ff00
            )
            
            welcome_embed.add_field(
                name="🔧 أوامر مفيدة",
                value="`-إغلاق_تذكرة` - إغلاق التذكرة\n"
                     "`-معلومات_تذكرة` - معلومات التذكرة\n"
                     "`-إضافة_مستخدم @المستخدم` - إضافة مستخدم للتذكرة",
                inline=False
            )
            
            welcome_embed.set_footer(text="نقدر صبرك وسنساعدك في أقرب وقت")
            
            await ticket_channel.send(embed=welcome_embed)
            
            # إشعار للمستخدم
            try:
                dm_embed = discord.Embed(
                    title="🎫 تم إنشاء تذكرتك",
                    description=f"تم إنشاء تذكرة {category_info['name']} بنجاح!\n"
                               f"يمكنك الوصول إليها في {ticket_channel.mention}",
                    color=0x00ff00
                )
                await member.send(embed=dm_embed)
            except:
                pass
            
            # إضافة رسالة نظام للتذكرة
            await self.db.add_ticket_message(
                ticket_id=ticket_id,
                user_id=self.bot.user.id,
                message_content=f"تم إنشاء التذكرة - النوع: {category_info['name']}",
                message_type='system'
            )
            
        except Exception as e:
            # رسالة خطأ للمستخدم
            try:
                error_embed = discord.Embed(
                    title="❌ خطأ في إنشاء التذكرة",
                    description="حدث خطأ أثناء إنشاء التذكرة. يرجى المحاولة مرة أخرى أو التواصل مع الإدارة.",
                    color=0xff0000
                )
                await member.send(embed=error_embed)
            except:
                pass

    @commands.command(name='إغلاق_تذكرة', aliases=['close_ticket'])
    async def close_ticket(self, ctx, *, reason="لم يتم تحديد سبب"):
        """إغلاق التذكرة الحالية"""
        # التحقق من أن القناة تذكرة
        if not ctx.channel.topic or 'ID:' not in ctx.channel.topic:
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذه القناة ليست تذكرة دعم.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # استخراج معرف التذكرة
        try:
            ticket_id = ctx.channel.topic.split('ID: ')[1].strip()
        except:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكن العثور على معرف التذكرة.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # الحصول على التذكرة من قاعدة البيانات
        ticket_data = await self.db.get_ticket(ticket_id)
        if not ticket_data:
            embed = discord.Embed(
                title="❌ خطأ",
                description="التذكرة غير موجودة في قاعدة البيانات.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # التحقق من الصلاحيات
        is_ticket_owner = ctx.author.id == ticket_data[2]  # user_id
        is_staff = ctx.author.guild_permissions.manage_messages
        
        if not (is_ticket_owner or is_staff):
            embed = discord.Embed(
                title="❌ غير مسموح",
                description="يمكن فقط لصاحب التذكرة أو الموظفين إغلاق التذكرة.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # تأكيد الإغلاق
        confirm_embed = discord.Embed(
            title="⚠️ تأكيد إغلاق التذكرة",
            description=f"هل أنت متأكد من إغلاق هذه التذكرة؟\n\n"
                       f"**السبب:** {reason}\n\n"
                       f"اكتب `نعم` للتأكيد أو `لا` للإلغاء",
            color=0xffaa00
        )
        await ctx.send(embed=confirm_embed)
        
        def check(m):
            return (m.author == ctx.author and 
                   m.channel == ctx.channel and
                   m.content.lower() in ['نعم', 'yes', 'y', 'لا', 'no', 'n'])
        
        try:
            response = await self.bot.wait_for('message', timeout=30.0, check=check)
            
            if response.content.lower() in ['نعم', 'yes', 'y']:
                await self.finalize_ticket_closure(ctx, ticket_id, reason)
            else:
                await ctx.send("❌ تم إلغاء إغلاق التذكرة.")
                
        except asyncio.TimeoutError:
            await ctx.send("⏰ انتهت مهلة التأكيد. تم إلغاء إغلاق التذكرة.")

    async def finalize_ticket_closure(self, ctx, ticket_id, reason):
        """إنهاء إغلاق التذكرة"""
        # تحديث حالة التذكرة في قاعدة البيانات
        await self.db.update_ticket_status(ticket_id, 'closed', ctx.author.id)
        
        # إضافة رسالة إغلاق
        await self.db.add_ticket_message(
            ticket_id=ticket_id,
            user_id=ctx.author.id,
            message_content=f"تم إغلاق التذكرة - السبب: {reason}",
            message_type='system'
        )
        
        # رسالة إغلاق
        close_embed = discord.Embed(
            title="🔒 تم إغلاق التذكرة",
            description=f"تم إغلاق التذكرة بواسطة {ctx.author.mention}\n"
                       f"**السبب:** {reason}\n\n"
                       f"سيتم حذف القناة خلال 10 ثوان...",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=close_embed)
        
        # انتظار ثم حذف القناة
        await asyncio.sleep(10)
        try:
            await ctx.channel.delete(reason=f"تذكرة مغلقة - {reason}")
        except:
            pass

    @commands.command(name='معلومات_تذكرة', aliases=['ticket_info'])
    async def ticket_info(self, ctx):
        """عرض معلومات التذكرة الحالية"""
        # التحقق من أن القناة تذكرة
        if not ctx.channel.topic or 'ID:' not in ctx.channel.topic:
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذه القناة ليست تذكرة دعم.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # استخراج معرف التذكرة
        try:
            ticket_id = ctx.channel.topic.split('ID: ')[1].strip()
        except:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكن العثور على معرف التذكرة.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # الحصول على التذكرة من قاعدة البيانات
        ticket_data = await self.db.get_ticket(ticket_id)
        if not ticket_data:
            embed = discord.Embed(
                title="❌ خطأ",
                description="التذكرة غير موجودة في قاعدة البيانات.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # تحليل بيانات التذكرة
        ticket_user = self.bot.get_user(ticket_data[2])
        category_info = self.ticket_categories.get(ticket_data[4], {'name': 'غير محدد', 'emoji': '❓'})
        
        assigned_user = None
        if ticket_data[9]:  # assigned_to
            assigned_user = self.bot.get_user(ticket_data[9])
        
        # إنشاء الإيمبد
        embed = discord.Embed(
            title=f"{category_info['emoji']} معلومات التذكرة",
            color=0x00aaff,
            timestamp=datetime.fromisoformat(ticket_data[10])  # created_at
        )
        
        embed.add_field(name="🆔 معرف التذكرة", value=f"`{ticket_id}`", inline=True)
        embed.add_field(name="👤 صاحب التذكرة", value=ticket_user.mention if ticket_user else "مستخدم محذوف", inline=True)
        embed.add_field(name="📂 الفئة", value=category_info['name'], inline=True)
        
        embed.add_field(name="📋 العنوان", value=ticket_data[5] or "غير محدد", inline=True)
        embed.add_field(name="🔄 الحالة", value=ticket_data[7].replace('open', 'مفتوحة').replace('closed', 'مغلقة'), inline=True)
        embed.add_field(name="⚡ الأولوية", value=ticket_data[8].replace('low', 'منخفضة').replace('medium', 'متوسطة').replace('high', 'عالية'), inline=True)
        
        if assigned_user:
            embed.add_field(name="👨‍💼 مُعين إلى", value=assigned_user.mention, inline=True)
        
        embed.add_field(name="📅 تاريخ الإنشاء", value=ticket_data[10][:16], inline=True)
        embed.add_field(name="🔄 آخر تحديث", value=ticket_data[11][:16], inline=True)
        
        if ticket_data[6]:  # description
            embed.add_field(name="📝 الوصف", value=ticket_data[6][:1000], inline=False)
        
        embed.set_footer(text=f"تذكرة في سيرفر {ctx.guild.name}")
        
        await ctx.send(embed=embed)

    @commands.command(name='تذاكري', aliases=['my_tickets'])
    async def my_tickets(self, ctx):
        """عرض تذاكر المستخدم"""
        user_tickets = await self.db.get_user_tickets(ctx.author.id)
        
        if not user_tickets:
            embed = discord.Embed(
                title="📋 تذاكرك",
                description="ليس لديك أي تذاكر حتى الآن.",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"📋 تذاكر {ctx.author.display_name}",
            description=f"إجمالي التذاكر: {len(user_tickets)}",
            color=0x00aaff
        )
        
        open_tickets = [t for t in user_tickets if t[7] == 'open']
        closed_tickets = [t for t in user_tickets if t[7] == 'closed']
        
        if open_tickets:
            open_list = []
            for ticket in open_tickets[:5]:  # أول 5 تذاكر مفتوحة
                category_info = self.ticket_categories.get(ticket[4], {'name': 'غير محدد', 'emoji': '❓'})
                open_list.append(f"{category_info['emoji']} `{ticket[1]}` - {category_info['name']}")
            
            embed.add_field(
                name=f"🟢 التذاكر المفتوحة ({len(open_tickets)})",
                value="\n".join(open_list),
                inline=False
            )
        
        if closed_tickets:
            closed_list = []
            for ticket in closed_tickets[:3]:  # أول 3 تذاكر مغلقة
                category_info = self.ticket_categories.get(ticket[4], {'name': 'غير محدد', 'emoji': '❓'})
                closed_list.append(f"{category_info['emoji']} `{ticket[1]}` - {category_info['name']}")
            
            embed.add_field(
                name=f"🔴 التذاكر المغلقة ({len(closed_tickets)})",
                value="\n".join(closed_list),
                inline=False
            )
        
        embed.set_footer(text="استخدم -معلومات_تذكرة في قناة التذكرة للمزيد من التفاصيل")
        
        await ctx.send(embed=embed)

    @commands.command(name='قائمة_التذاكر', aliases=['list_tickets'])
    @commands.has_permissions(manage_messages=True)
    async def list_tickets(self, ctx, status=None):
        """عرض قائمة التذاكر للموظفين"""
        if status and status not in ['open', 'closed', 'مفتوحة', 'مغلقة']:
            status = None
        
        # تحويل الحالة للإنجليزية
        if status == 'مفتوحة':
            status = 'open'
        elif status == 'مغلقة':
            status = 'closed'
        
        all_tickets = await self.db.get_all_tickets(status=status, limit=20)
        
        if not all_tickets:
            status_text = f" ال{status.replace('open', 'مفتوحة').replace('closed', 'مغلقة')}" if status else ""
            embed = discord.Embed(
                title="📋 قائمة التذاكر",
                description=f"لا توجد تذاكر{status_text} حالياً.",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="📋 قائمة التذاكر",
            description=f"عرض آخر {len(all_tickets)} تذكرة:",
            color=0x00aaff
        )
        
        for ticket in all_tickets[:10]:  # أول 10 تذاكر
            ticket_user = self.bot.get_user(ticket[2])
            category_info = self.ticket_categories.get(ticket[4], {'name': 'غير محدد', 'emoji': '❓'})
            
            status_emoji = "🟢" if ticket[7] == 'open' else "🔴"
            priority_emoji = {"low": "🟦", "medium": "🟨", "high": "🟥"}.get(ticket[8], "⬜")
            
            embed.add_field(
                name=f"{status_emoji} {category_info['emoji']} `{ticket[1]}`",
                value=f"**المستخدم:** {ticket_user.display_name if ticket_user else 'محذوف'}\n"
                     f"**الفئة:** {category_info['name']} {priority_emoji}\n"
                     f"**التاريخ:** {ticket[10][:10]}",
                inline=True
            )
        
        if len(all_tickets) > 10:
            embed.add_field(
                name="📊 المجموع",
                value=f"و {len(all_tickets) - 10} تذكرة إضافية...",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='تعيين_تذكرة', aliases=['assign_ticket'])
    @commands.has_permissions(manage_messages=True)
    async def assign_ticket(self, ctx, member: discord.Member = None):
        """تعيين التذكرة الحالية لموظف"""
        if member is None:
            member = ctx.author
        
        # التحقق من أن القناة تذكرة
        if not ctx.channel.topic or 'ID:' not in ctx.channel.topic:
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذه القناة ليست تذكرة دعم.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # استخراج معرف التذكرة
        try:
            ticket_id = ctx.channel.topic.split('ID: ')[1].strip()
        except:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكن العثور على معرف التذكرة.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # تعيين التذكرة
        await self.db.assign_ticket(ticket_id, member.id)
        
        # إضافة رسالة للتذكرة
        await self.db.add_ticket_message(
            ticket_id=ticket_id,
            user_id=ctx.author.id,
            message_content=f"تم تعيين التذكرة إلى {member.display_name}",
            message_type='system'
        )
        
        embed = discord.Embed(
            title="👨‍💼 تم تعيين التذكرة",
            description=f"تم تعيين هذه التذكرة إلى {member.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Tickets(bot))