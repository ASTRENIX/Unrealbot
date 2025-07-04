import discord
import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Optional, List, Union

class Helpers:
    """مساعدات وأدوات مشتركة للبوت"""
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """تحويل الثواني إلى تنسيق وقت قابل للقراءة"""
        if seconds < 60:
            return f"{seconds} ثانية"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes} دقيقة"
            return f"{minutes} دقيقة و {remaining_seconds} ثانية"
        elif seconds < 86400:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours} ساعة"
            return f"{hours} ساعة و {remaining_minutes} دقيقة"
        else:
            days = seconds // 86400
            remaining_hours = (seconds % 86400) // 3600
            if remaining_hours == 0:
                return f"{days} يوم"
            return f"{days} يوم و {remaining_hours} ساعة"
    
    @staticmethod
    def format_number(number: int) -> str:
        """تنسيق الأرقام مع فواصل"""
        return f"{number:,}".replace(",", "٬")
    
    @staticmethod
    def parse_time(time_str: str) -> Optional[int]:
        """تحويل نص الوقت إلى ثوان"""
        time_str = time_str.lower().strip()
        
        # البحث عن أنماط الوقت
        patterns = {
            r'(\d+)\s*(?:ثانية|ثواني|ث|s|sec|seconds?)': 1,
            r'(\d+)\s*(?:دقيقة|دقائق|د|m|min|minutes?)': 60,
            r'(\d+)\s*(?:ساعة|ساعات|س|h|hour|hours?)': 3600,
            r'(\d+)\s*(?:يوم|أيام|ي|d|day|days?)': 86400,
            r'(\d+)\s*(?:أسبوع|أسابيع|أ|w|week|weeks?)': 604800
        }
        
        total_seconds = 0
        
        for pattern, multiplier in patterns.items():
            matches = re.findall(pattern, time_str)
            for match in matches:
                total_seconds += int(match) * multiplier
        
        return total_seconds if total_seconds > 0 else None
    
    @staticmethod
    def create_progress_bar(current: int, maximum: int, length: int = 20) -> str:
        """إنشاء شريط تقدم نصي"""
        if maximum == 0:
            return "▱" * length
        
        progress = min(current / maximum, 1.0)
        filled = int(progress * length)
        
        bar = "▰" * filled + "▱" * (length - filled)
        percentage = int(progress * 100)
        
        return f"{bar} {percentage}%"
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """قص النص إذا كان أطول من الحد المسموح"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def clean_text(text: str) -> str:
        """تنظيف النص من الأحرف غير المرغوب فيها"""
        # إزالة أكواد Discord
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', '', text)
        
        # إزالة الروابط
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # إزالة المنشنز
        text = re.sub(r'<@[!&]?\d+>', '', text)
        text = re.sub(r'<#\d+>', '', text)
        text = re.sub(r'<:\w+:\d+>', '', text)
        
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_id_from_mention(mention: str) -> Optional[int]:
        """استخراج المعرف من المنشن"""
        patterns = [
            r'<@!?(\d+)>',  # user mention
            r'<#(\d+)>',    # channel mention
            r'<@&(\d+)>',   # role mention
        ]
        
        for pattern in patterns:
            match = re.match(pattern, mention)
            if match:
                return int(match.group(1))
        
        # إذا كان رقم مباشر
        if mention.isdigit():
            return int(mention)
        
        return None
    
    @staticmethod
    def create_embed(title: str, description: str = None, color: int = 0x00aaff, 
                    fields: List[dict] = None, footer: str = None, 
                    thumbnail: str = None, image: str = None) -> discord.Embed:
        """إنشاء embed مُنسق"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', 'بدون عنوان'),
                    value=field.get('value', 'بدون قيمة'),
                    inline=field.get('inline', True)
                )
        
        if footer:
            embed.set_footer(text=footer)
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        return embed
    
    @staticmethod
    def paginate_text(text: str, max_length: int = 2000) -> List[str]:
        """تقسيم النص الطويل إلى صفحات"""
        if len(text) <= max_length:
            return [text]
        
        pages = []
        current_page = ""
        
        lines = text.split('\n')
        
        for line in lines:
            if len(current_page) + len(line) + 1 <= max_length:
                current_page += line + '\n'
            else:
                if current_page:
                    pages.append(current_page.strip())
                current_page = line + '\n'
        
        if current_page:
            pages.append(current_page.strip())
        
        return pages
    
    @staticmethod
    async def send_paginated_embed(ctx, embeds: List[discord.Embed], timeout: int = 300):
        """إرسال embeds متعددة مع نظام تنقل"""
        if not embeds:
            return
        
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        
        current_page = 0
        
        # إضافة أرقام الصفحات
        for i, embed in enumerate(embeds):
            embed.set_footer(text=f"الصفحة {i + 1} من {len(embeds)}")
        
        message = await ctx.send(embed=embeds[current_page])
        
        # إضافة ردود الأفعال للتنقل
        if len(embeds) > 1:
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            await message.add_reaction("❌")
        
        def check(reaction, user):
            return (user == ctx.author and 
                   reaction.message.id == message.id and
                   str(reaction.emoji) in ["◀️", "▶️", "❌"])
        
        while True:
            try:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
                
                if str(reaction.emoji) == "▶️":
                    current_page = (current_page + 1) % len(embeds)
                elif str(reaction.emoji) == "◀️":
                    current_page = (current_page - 1) % len(embeds)
                elif str(reaction.emoji) == "❌":
                    await message.delete()
                    return
                
                await message.edit(embed=embeds[current_page])
                await message.remove_reaction(reaction, user)
                
            except asyncio.TimeoutError:
                try:
                    await message.clear_reactions()
                except:
                    pass
                break
    
    @staticmethod
    def get_level_from_xp(xp: int) -> int:
        """حساب المستوى من النقاط"""
        return int((xp / 100) ** 0.5) + 1
    
    @staticmethod
    def get_xp_for_level(level: int) -> int:
        """حساب النقاط المطلوبة للمستوى"""
        return ((level - 1) ** 2) * 100
    
    @staticmethod
    def format_permission_name(permission: str) -> str:
        """تحويل أسماء الصلاحيات للعربية"""
        permission_map = {
            'administrator': 'مدير',
            'manage_guild': 'إدارة السيرفر',
            'manage_channels': 'إدارة القنوات',
            'manage_roles': 'إدارة الأدوار',
            'manage_messages': 'إدارة الرسائل',
            'kick_members': 'طرد الأعضاء',
            'ban_members': 'حظر الأعضاء',
            'mute_members': 'كتم الأعضاء',
            'deafen_members': 'إصمات الأعضاء',
            'move_members': 'نقل الأعضاء',
            'mention_everyone': 'منشن الجميع',
            'send_messages': 'إرسال رسائل',
            'read_messages': 'قراءة الرسائل',
            'connect': 'الاتصال الصوتي',
            'speak': 'التحدث',
            'use_voice_activation': 'استخدام الصوت',
            'view_audit_log': 'عرض سجل التدقيق'
        }
        
        return permission_map.get(permission, permission)
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """التحقق من صحة رابط YouTube"""
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    @staticmethod
    def extract_youtube_id(url: str) -> Optional[str]:
        """استخراج معرف الفيديو من رابط YouTube"""
        patterns = [
            r'youtube\.com/watch\?v=([^&\n?#]+)',
            r'youtu\.be/([^&\n?#]+)',
            r'youtube\.com/embed/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def is_staff_member(member: discord.Member, config: dict) -> bool:
        """التحقق من كون العضو من الإدارة"""
        admin_roles = config.get('admin_role_ids', [])
        mod_roles = config.get('moderator_role_ids', [])
        
        if member.guild_permissions.administrator:
            return True
        
        user_role_ids = [role.id for role in member.roles]
        
        return any(role_id in user_role_ids for role_id in admin_roles + mod_roles)
    
    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        """إنشاء embed للنجاح"""
        return discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """إنشاء embed للخطأ"""
        return discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def create_warning_embed(title: str, description: str) -> discord.Embed:
        """إنشاء embed للتحذير"""
        return discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xffaa00,
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def create_info_embed(title: str, description: str) -> discord.Embed:
        """إنشاء embed للمعلومات"""
        return discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=0x00aaff,
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    async def confirm_action(ctx, message: str, timeout: int = 30) -> bool:
        """طلب تأكيد من المستخدم"""
        embed = discord.Embed(
            title="⚠️ تأكيد الإجراء",
            description=f"{message}\n\n"
                       "اكتب **نعم** للتأكيد أو **لا** للإلغاء",
            color=0xffaa00
        )
        
        await ctx.send(embed=embed)
        
        def check(m):
            return (m.author == ctx.author and 
                   m.channel == ctx.channel and
                   m.content.lower() in ['نعم', 'yes', 'y', 'لا', 'no', 'n'])
        
        try:
            response = await ctx.bot.wait_for('message', timeout=timeout, check=check)
            return response.content.lower() in ['نعم', 'yes', 'y']
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة",
                description="تم إلغاء الإجراء بسبب انتهاء المهلة",
                color=0xff0000
            )
            await ctx.send(embed=timeout_embed)
            return False
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """تأمين اسم الملف من الأحرف الخطيرة"""
        # إزالة أو استبدال الأحرف الخطيرة
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        filename = ''.join(c if c in safe_chars else '_' for c in filename)
        
        # تجنب الأسماء المحجوزة
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
        if filename.upper() in reserved_names:
            filename = f"_{filename}"
        
        return filename[:255]  # حد أقصى 255 حرف
