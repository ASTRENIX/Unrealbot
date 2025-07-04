import random
from typing import Dict, List

class ArabicResponses:
    """مجموعة شاملة من الردود والرسائل العربية للبوت"""
    
    def __init__(self):
        # رسائل الترحيب
        self.welcome_messages = [
            "أهلاً وسهلاً بك في سيرفر Unreal! 🎉",
            "مرحباً بك معنا! نتمنى لك قضاء وقت ممتع 😊",
            "أهلاً بالعضو الجديد! مرحباً بك في عائلة Unreal 🌟",
            "مرحباً! سعداء بانضمامك إلينا في سيرفر Unreal 🎊",
            "أهلاً وسهلاً! نرحب بك في مجتمعنا الرائع 🚀"
        ]
        
        # رسائل الوداع
        self.goodbye_messages = [
            "وداعاً {name}! نتمنى لك التوفيق 👋",
            "سنفتقدك {name}! أتمنى أن نراك مرة أخرى 💙",
            "إلى اللقاء {name}! الأبواب مفتوحة دائماً للعودة 🌟",
            "وداعاً {name}! شكراً لكونك جزءاً من مجتمعنا 🙏"
        ]
        
        # رسائل التشجيع للألعاب
        self.game_encouragement = [
            "أحسنت! استمر هكذا! 🎉",
            "رائع! أداء ممتاز! 👏",
            "مبدع! واصل التقدم! ⭐",
            "عظيم! أنت تتحسن! 🚀",
            "ممتاز! استمر في اللعب! 🎮",
            "بارك الله فيك! إنجاز رائع! 🌟",
            "مذهل! قدراتك تتطور! 💪",
            "ولا أروع! استمر في التفوق! 🏆"
        ]
        
        # رسائل الخسارة المشجعة
        self.game_consolation = [
            "لا بأس! المحاولة القادمة ستكون أفضل! 💪",
            "تقريباً! أنت على الطريق الصحيح! 🎯",
            "جيد! استمر في المحاولة! 🌟",
            "لا تيأس! الممارسة تؤدي للإتقان! 📈",
            "قريب جداً! حاول مرة أخرى! 🎮",
            "أداء جيد! المرة القادمة بإذن الله! 🙏",
            "مجهود رائع! لا تستسلم! 💯",
            "تحسن واضح! واصل المحاولة! ⬆️"
        ]
        
        # رسائل الإنجازات
        self.achievement_messages = [
            "تهانينا! لقد حققت إنجازاً رائعاً! 🏆",
            "مبروك! وصلت لمستوى جديد! 🎊",
            "عظيم! إنجاز يستحق التقدير! 🌟",
            "ممتاز! استمر في التقدم! 📈",
            "رائع! أداء استثنائي! 💎",
            "مذهل! نجاح يستحق الاحتفال! 🎉",
            "بارك الله فيك! إنجاز مميز! 🙌",
            "فخورون بك! واصل التميز! ⭐"
        ]
        
        # رسائل الأخطاء الودودة
        self.error_messages = [
            "عذراً، حدث خطأ! يرجى المحاولة مرة أخرى 😅",
            "أوه! شيء لم يسر كما هو مخطط له 🤔",
            "عفواً، واجهنا مشكلة صغيرة! 🔧",
            "للأسف، لم أتمكن من تنفيذ الطلب 😞",
            "يبدو أن هناك خطأ ما! دعني أحاول مرة أخرى 🔄"
        ]
        
        # رسائل التحفيز اليومية
        self.daily_motivation = [
            "اجعل هذا اليوم مميزاً! 🌅",
            "أنت قادر على تحقيق المستحيل! 💪",
            "كل يوم فرصة جديدة للإبداع! ✨",
            "ابدأ يومك بطاقة إيجابية! ⚡",
            "النجاح يبدأ بخطوة واحدة! 👣",
            "أنت أقوى مما تتخيل! 🦁",
            "اليوم مليء بالفرص الذهبية! 🌟",
            "ثق بنفسك وستصل للقمة! 🏔️"
        ]
        
        # رسائل نشاط الصوت
        self.voice_activity = [
            "مرحباً بك في القناة الصوتية! 🎤",
            "أهلاً! استمتع بوقتك معنا! 🗣️",
            "مرحباً! نورت القناة! ✨",
            "أهلاً وسهلاً! وقت ممتع! 🎵",
            "مرحباً بك! تفاعل رائع! 👥"
        ]
        
        # رسائل مكافآت الصوت
        self.voice_rewards = [
            "رائع! حصلت على مكافأة الصوت! 🎁",
            "ممتاز! نقاط إضافية لنشاطك الصوتي! ⭐",
            "عظيم! مكافأة التفاعل الصوتي! 🏆",
            "أحسنت! نقاط مستحقة للنشاط! 💎",
            "مبدع! مكافأة الوقت المقضي! 🕐"
        ]
        
        # رسائل التحقق
        self.verification_messages = [
            "مرحباً بك! تم التحقق من عضويتك بنجاح! ✅",
            "أهلاً! أصبحت الآن عضواً متحققاً! 🔒",
            "تهانينا! تم تفعيل حسابك بنجاح! 🎉",
            "مرحباً! يمكنك الآن الوصول لجميع القنوات! 🚪",
            "عظيم! التحقق مكتمل! مرحباً بك معنا! 🌟"
        ]
        
        # ردود فعل الموسيقى
        self.music_responses = [
            "🎵 موسيقى رائعة! استمتعوا!",
            "🎶 أغنية جميلة! صوت عذب!",
            "🎼 اختيار موفق! نغم جميل!",
            "🎤 صوت رائع! موسيقى هادئة!",
            "🎧 جودة عالية! استمتعوا بالاستماع!"
        ]
        
        # رسائل الإشراف
        self.moderation_responses = {
            'kick': [
                "تم تنفيذ الطرد بنجاح ✅",
                "العضو مطرود من السيرفر 👮‍♂️",
                "تم الطرد وفقاً للقوانين 📋"
            ],
            'ban': [
                "تم تنفيذ الحظر بنجاح 🔨",
                "العضو محظور من السيرفر ⛔",
                "تم الحظر للحفاظ على أمان السيرفر 🛡️"
            ],
            'mute': [
                "تم كتم العضو مؤقتاً 🔇",
                "الكتم نافذ المفعول 🤐",
                "تم تطبيق الكتم بنجاح ✅"
            ],
            'warn': [
                "تم إعطاء تحذير للعضو ⚠️",
                "التحذير مسجل في النظام 📝",
                "تحذير موثق بنجاح ✅"
            ]
        }
        
        # رسائل الحالة
        self.status_messages = [
            "سيرفر Unreal | -help للمساعدة",
            "مجتمع Unreal النشط | -مساعدة",
            "بوت عربي شامل | -help",
            "مرحباً بكم في Unreal | -مساعدة",
            "نخدمكم على مدار الساعة | -help"
        ]
        
        # عبارات الشكر
        self.thanks_messages = [
            "شكراً لك! 🙏",
            "بارك الله فيك! 🌟",
            "جزاك الله خيراً! ✨",
            "أحسن الله إليك! 💙",
            "وفقك الله! 🤲",
            "الله يعطيك العافية! 💪",
            "شكراً جزيلاً! 🙌",
            "تسلم يدك! 👏"
        ]
        
        # تحيات مختلفة حسب الوقت
        self.time_greetings = {
            'morning': [
                "صباح الخير! ☀️",
                "صباح النور! 🌅",
                "أهلاً وسهلاً! صباح مبارك! 🌻",
                "مرحباً! نهار سعيد! 🌞"
            ],
            'afternoon': [
                "مساء الخير! 🌇",
                "مساء النور! ✨",
                "أهلاً! مساء مبارك! 🌆",
                "مرحباً! أمسية سعيدة! 🌙"
            ],
            'night': [
                "مساء الخير! 🌙",
                "ليلة سعيدة! ⭐",
                "أهلاً! ليلة مباركة! 🌌",
                "مرحباً في هذه الليلة الجميلة! 🌟"
            ]
        }
    
    def get_random_welcome(self) -> str:
        """الحصول على رسالة ترحيب عشوائية"""
        return random.choice(self.welcome_messages)
    
    def get_random_goodbye(self, name: str = "") -> str:
        """الحصول على رسالة وداع عشوائية"""
        message = random.choice(self.goodbye_messages)
        return message.format(name=name) if name else message.replace(" {name}", "")
    
    def get_game_encouragement(self) -> str:
        """الحصول على رسالة تشجيع للألعاب"""
        return random.choice(self.game_encouragement)
    
    def get_game_consolation(self) -> str:
        """الحصول على رسالة مواساة للخسارة"""
        return random.choice(self.game_consolation)
    
    def get_achievement_message(self) -> str:
        """الحصول على رسالة إنجاز"""
        return random.choice(self.achievement_messages)
    
    def get_error_message(self) -> str:
        """الحصول على رسالة خطأ ودودة"""
        return random.choice(self.error_messages)
    
    def get_daily_motivation(self) -> str:
        """الحصول على رسالة تحفيز يومية"""
        return random.choice(self.daily_motivation)
    
    def get_voice_greeting(self) -> str:
        """الحصول على تحية للنشاط الصوتي"""
        return random.choice(self.voice_activity)
    
    def get_voice_reward_message(self) -> str:
        """الحصول على رسالة مكافأة صوتية"""
        return random.choice(self.voice_rewards)
    
    def get_verification_message(self) -> str:
        """الحصول على رسالة تحقق"""
        return random.choice(self.verification_messages)
    
    def get_music_response(self) -> str:
        """الحصول على رد فعل موسيقي"""
        return random.choice(self.music_responses)
    
    def get_moderation_response(self, action_type: str) -> str:
        """الحصول على رد فعل إشرافي"""
        if action_type in self.moderation_responses:
            return random.choice(self.moderation_responses[action_type])
        return "تم تنفيذ الإجراء بنجاح ✅"
    
    def get_status_message(self) -> str:
        """الحصول على رسالة حالة للبوت"""
        return random.choice(self.status_messages)
    
    def get_thanks_message(self) -> str:
        """الحصول على عبارة شكر"""
        return random.choice(self.thanks_messages)
    
    def get_time_greeting(self, time_period: str = 'morning') -> str:
        """الحصول على تحية حسب الوقت"""
        if time_period in self.time_greetings:
            return random.choice(self.time_greetings[time_period])
        return random.choice(self.time_greetings['morning'])
    
    def get_command_descriptions(self) -> Dict[str, str]:
        """أوصاف الأوامر بالعربية"""
        return {
            # أوامر الموسيقى
            'تشغيل': 'تشغيل موسيقى من YouTube',
            'إيقاف': 'إيقاف الموسيقى مؤقتاً',
            'استكمال': 'استكمال تشغيل الموسيقى',
            'تخطي': 'تخطي المقطع الحالي',
            'توقف': 'إيقاف التشغيل نهائياً',
            'قائمة': 'عرض قائمة الانتظار',
            'تكرار': 'تكرار المقطع الحالي',
            'مستوى_الصوت': 'تعديل مستوى الصوت',
            
            # أوامر الألعاب
            'سؤال': 'لعبة الأسئلة الثقافية',
            'تخمين_كلمة': 'لعبة تخمين الكلمة',
            'تخمين_رقم': 'لعبة تخمين الرقم',
            'إحصائيات_الألعاب': 'عرض إحصائيات الألعاب',
            
            # أوامر الإشراف
            'طرد': 'طرد عضو من السيرفر',
            'حظر': 'حظر عضو من السيرفر',
            'كتم': 'كتم عضو مؤقتاً',
            'تحذير': 'إعطاء تحذير لعضو',
            'مسح': 'مسح عدد من الرسائل',
            'تحذيرات': 'عرض تحذيرات عضو',
            
            # أوامر التحقق
            'إعداد_التحقق': 'إعداد نظام التحقق',
            'تحقق_يدوي': 'تحقق يدوي من عضو',
            'حالة_التحقق': 'عرض حالة التحقق',
            
            # أوامر الصوت
            'نشاط_الصوت': 'عرض إحصائيات الصوت',
            'لوحة_الصوت': 'لوحة متصدري الصوت',
            
            # أوامر عامة
            'مساعدة': 'عرض قائمة المساعدة',
            'معلومات_السيرفر': 'معلومات السيرفر',
            'معلومات_المستخدم': 'معلومات المستخدم',
            'معلومات_البوت': 'معلومات البوت',
            'ping': 'فحص سرعة الاستجابة',
            'إحصائيات': 'إحصائيات عامة للسيرفر'
        }
    
    def get_permission_names(self) -> Dict[str, str]:
        """أسماء الصلاحيات بالعربية"""
        return {
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
            'use_voice_activation': 'استخدام الصوت'
        }
    
    def format_duration(self, seconds: int) -> str:
        """تنسيق المدة بالعربية"""
        if seconds < 60:
            return f"{seconds} ثانية"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining = seconds % 60
            if remaining == 0:
                return f"{minutes} دقيقة"
            return f"{minutes} دقيقة و {remaining} ثانية"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours} ساعة"
            return f"{hours} ساعة و {remaining_minutes} دقيقة"
    
    def format_number(self, number: int) -> str:
        """تنسيق الأرقام بالعربية"""
        return f"{number:,}".replace(",", "٬")
    
    def get_random_emoji_set(self, category: str) -> List[str]:
        """الحصول على مجموعة إيموجي عشوائية"""
        emoji_sets = {
            'celebration': ['🎉', '🎊', '🥳', '🎈', '🍾', '✨', '🌟', '💫'],
            'success': ['✅', '✔️', '☑️', '✨', '🌟', '⭐', '💯', '🏆'],
            'error': ['❌', '❎', '⛔', '🚫', '💢', '⚠️', '🔴', '💥'],
            'music': ['🎵', '🎶', '🎼', '🎤', '🎧', '🔊', '📻', '🎸'],
            'games': ['🎮', '🕹️', '🎯', '🎲', '🃏', '🧩', '🏁', '🎪'],
            'heart': ['❤️', '💙', '💚', '💛', '💜', '🧡', '🤍', '🖤'],
            'nature': ['🌸', '🌺', '🌻', '🌷', '🌹', '💐', '🌿', '☘️']
        }
        
        return emoji_sets.get(category, ['✨', '🌟', '⭐'])
