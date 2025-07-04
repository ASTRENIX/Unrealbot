import discord
from discord.ext import commands
import random
import json
import asyncio
from database import Database

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # تحميل الإعدادات
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # أسئلة الثقافة العامة
        self.trivia_questions = [
            {
                "question": "ما هي عاصمة فرنسا؟",
                "options": ["باريس", "لندن", "برلين", "روما"],
                "answer": 0,
                "difficulty": "سهل"
            },
            {
                "question": "كم عدد أيام السنة الكبيسة؟",
                "options": ["365", "366", "364", "367"],
                "answer": 1,
                "difficulty": "سهل"
            },
            {
                "question": "ما هو أكبر كوكب في المجموعة الشمسية؟",
                "options": ["الأرض", "المريخ", "المشتري", "زحل"],
                "answer": 2,
                "difficulty": "متوسط"
            },
            {
                "question": "في أي عام تم اختراع الإنترنت؟",
                "options": ["1989", "1991", "1969", "1995"],
                "answer": 2,
                "difficulty": "صعب"
            },
            {
                "question": "ما هو العنصر الكيميائي لرمز 'Au'؟",
                "options": ["الفضة", "الذهب", "النحاس", "الحديد"],
                "answer": 1,
                "difficulty": "متوسط"
            },
            {
                "question": "كم عدد عضلات جسم الإنسان؟",
                "options": ["206", "639", "500", "800"],
                "answer": 1,
                "difficulty": "صعب"
            },
            {
                "question": "ما هي أطول سلسلة جبال في العالم؟",
                "options": ["الهيمالايا", "الأنديز", "الألب", "القوقاز"],
                "answer": 1,
                "difficulty": "متوسط"
            },
            {
                "question": "في أي قارة تقع مصر؟",
                "options": ["آسيا", "أفريقيا", "أوروبا", "أمريكا"],
                "answer": 1,
                "difficulty": "سهل"
            }
        ]
        
        # كلمات لعبة التخمين
        self.word_categories = {
            "حيوانات": ["أسد", "فيل", "قطة", "كلب", "حصان", "نمر", "دب", "غزال"],
            "فواكه": ["تفاح", "موز", "برتقال", "عنب", "فراولة", "أناناس", "مانجو", "كيوي"],
            "بلدان": ["مصر", "السعودية", "الإمارات", "الكويت", "قطر", "الأردن", "لبنان", "سوريا"],
            "ألوان": ["أحمر", "أزرق", "أخضر", "أصفر", "بنفسجي", "برتقالي", "وردي", "أسود"]
        }
        
        # متغيرات الألعاب النشطة
        self.active_trivia = {}
        self.active_word_games = {}
        self.active_number_games = {}

    @commands.command(name='سؤال', aliases=['trivia'])
    @commands.cooldown(1, 30, commands.BucketType.channel)
    async def trivia(self, ctx, difficulty="عشوائي"):
        """لعبة الأسئلة الثقافية"""
        if ctx.channel.id in self.active_trivia:
            embed = discord.Embed(
                title="❌ لعبة نشطة",
                description="يوجد سؤال نشط بالفعل في هذه القناة!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # فلترة الأسئلة حسب الصعوبة
        available_questions = self.trivia_questions
        if difficulty != "عشوائي":
            available_questions = [q for q in self.trivia_questions if q["difficulty"] == difficulty]
            if not available_questions:
                available_questions = self.trivia_questions
        
        question_data = random.choice(available_questions)
        
        # إنشاء الإيمبد
        embed = discord.Embed(
            title="🧠 سؤال ثقافي",
            description=question_data["question"],
            color=0x00ff00
        )
        
        options_text = ""
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        for i, option in enumerate(question_data["options"]):
            options_text += f"{emojis[i]} {option}\n"
        
        embed.add_field(name="الخيارات:", value=options_text, inline=False)
        embed.add_field(name="الصعوبة:", value=question_data["difficulty"], inline=True)
        embed.add_field(name="المكافأة:", value=f"{self.get_reward_by_difficulty(question_data['difficulty'])} نقطة", inline=True)
        embed.set_footer(text="⏰ لديك 30 ثانية للإجابة")
        
        message = await ctx.send(embed=embed)
        
        # إضافة التفاعلات
        for i in range(len(question_data["options"])):
            await message.add_reaction(emojis[i])
        
        # تسجيل اللعبة النشطة
        self.active_trivia[ctx.channel.id] = {
            "question": question_data,
            "message": message,
            "author": ctx.author,
            "start_time": asyncio.get_event_loop().time()
        }
        
        # انتظار الإجابة
        try:
            def check(reaction, user):
                return (user != self.bot.user and 
                       reaction.message.id == message.id and
                       str(reaction.emoji) in emojis[:len(question_data["options"])])
            
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            # التحقق من الإجابة
            user_answer = emojis.index(str(reaction.emoji))
            correct_answer = question_data["answer"]
            
            if user_answer == correct_answer:
                reward = self.get_reward_by_difficulty(question_data["difficulty"])
                await self.db.update_user_xp(user.id, reward)
                await self.db.update_game_stats(user.id, "trivia", True, reward)
                
                result_embed = discord.Embed(
                    title="🎉 إجابة صحيحة!",
                    description=f"أحسنت {user.mention}!\n"
                               f"**المكافأة:** {reward} نقطة خبرة",
                    color=0x00ff00
                )
            else:
                await self.db.update_game_stats(user.id, "trivia", False, 0)
                correct_option = question_data["options"][correct_answer]
                
                result_embed = discord.Embed(
                    title="❌ إجابة خاطئة",
                    description=f"للأسف {user.mention}\n"
                               f"**الإجابة الصحيحة:** {emojis[correct_answer]} {correct_option}",
                    color=0xff0000
                )
            
            await ctx.send(embed=result_embed)
            
        except asyncio.TimeoutError:
            correct_option = question_data["options"][question_data["answer"]]
            timeout_embed = discord.Embed(
                title="⏰ انتهى الوقت",
                description=f"**الإجابة الصحيحة:** {emojis[question_data['answer']]} {correct_option}",
                color=0xffaa00
            )
            await ctx.send(embed=timeout_embed)
        
        finally:
            # إزالة اللعبة من القائمة النشطة
            if ctx.channel.id in self.active_trivia:
                del self.active_trivia[ctx.channel.id]

    @commands.command(name='تخمين_كلمة', aliases=['guess_word'])
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def guess_word(self, ctx, category="عشوائي"):
        """لعبة تخمين الكلمة"""
        if ctx.channel.id in self.active_word_games:
            embed = discord.Embed(
                title="❌ لعبة نشطة",
                description="يوجد لعبة تخمين نشطة بالفعل في هذه القناة!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # اختيار فئة وكلمة
        if category == "عشوائي" or category not in self.word_categories:
            category = random.choice(list(self.word_categories.keys()))
        
        word = random.choice(self.word_categories[category])
        hidden_word = "_ " * len(word)
        guessed_letters = set()
        wrong_guesses = 0
        max_wrong = 6
        
        embed = discord.Embed(
            title="🔤 لعبة تخمين الكلمة",
            description=f"**الفئة:** {category}\n"
                       f"**الكلمة:** {hidden_word}\n"
                       f"**الأخطاء:** {wrong_guesses}/{max_wrong}",
            color=0x00ff00
        )
        embed.add_field(name="كيفية اللعب:", value="اكتب حرف واحد لتخمين الكلمة!", inline=False)
        embed.set_footer(text="⏰ لديك 5 دقائق لحل اللغز")
        
        message = await ctx.send(embed=embed)
        
        # تسجيل اللعبة النشطة
        self.active_word_games[ctx.channel.id] = {
            "word": word,
            "hidden_word": list(word),
            "guessed_letters": guessed_letters,
            "wrong_guesses": wrong_guesses,
            "max_wrong": max_wrong,
            "category": category,
            "author": ctx.author,
            "message": message
        }
        
        def check(m):
            return (m.channel == ctx.channel and 
                   len(m.content) == 1 and 
                   m.content.isalpha() and
                   m.author != self.bot.user)
        
        while wrong_guesses < max_wrong:
            try:
                msg = await self.bot.wait_for('message', timeout=300.0, check=check)
                letter = msg.content.upper()
                
                if letter in guessed_letters:
                    await msg.add_reaction("🔄")
                    continue
                
                guessed_letters.add(letter)
                
                if letter in word.upper():
                    # حرف صحيح
                    await msg.add_reaction("✅")
                    
                    # كشف الحرف في الكلمة
                    displayed_word = ""
                    all_revealed = True
                    for char in word:
                        if char.upper() in guessed_letters:
                            displayed_word += char + " "
                        else:
                            displayed_word += "_ "
                            all_revealed = False
                    
                    if all_revealed:
                        # فوز!
                        await self.db.update_user_xp(msg.author.id, 15)
                        await self.db.update_game_stats(msg.author.id, "word_guess", True, 15)
                        
                        win_embed = discord.Embed(
                            title="🎉 تهانينا!",
                            description=f"أحسنت {msg.author.mention}!\n"
                                       f"**الكلمة:** {word}\n"
                                       f"**المكافأة:** 15 نقطة خبرة",
                            color=0x00ff00
                        )
                        await ctx.send(embed=win_embed)
                        break
                    
                    # تحديث العرض
                    embed = discord.Embed(
                        title="🔤 لعبة تخمين الكلمة",
                        description=f"**الفئة:** {category}\n"
                                   f"**الكلمة:** {displayed_word}\n"
                                   f"**الأخطاء:** {wrong_guesses}/{max_wrong}",
                        color=0x00ff00
                    )
                    embed.add_field(name="الحروف المستخدمة:", value=" ".join(sorted(guessed_letters)), inline=False)
                    await message.edit(embed=embed)
                    
                else:
                    # حرف خاطئ
                    await msg.add_reaction("❌")
                    wrong_guesses += 1
                    
                    if wrong_guesses >= max_wrong:
                        # خسارة
                        await self.db.update_game_stats(msg.author.id, "word_guess", False, 0)
                        
                        lose_embed = discord.Embed(
                            title="💀 انتهت اللعبة",
                            description=f"للأسف! لقد نفدت المحاولات\n"
                                       f"**الكلمة كانت:** {word}",
                            color=0xff0000
                        )
                        await ctx.send(embed=lose_embed)
                        break
                    
                    # تحديث العرض
                    displayed_word = ""
                    for char in word:
                        if char.upper() in guessed_letters:
                            displayed_word += char + " "
                        else:
                            displayed_word += "_ "
                    
                    embed = discord.Embed(
                        title="🔤 لعبة تخمين الكلمة",
                        description=f"**الفئة:** {category}\n"
                                   f"**الكلمة:** {displayed_word}\n"
                                   f"**الأخطاء:** {wrong_guesses}/{max_wrong}",
                        color=0xffaa00 if wrong_guesses < max_wrong else 0xff0000
                    )
                    embed.add_field(name="الحروف المستخدمة:", value=" ".join(sorted(guessed_letters)), inline=False)
                    await message.edit(embed=embed)
                
            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(
                    title="⏰ انتهى الوقت",
                    description=f"انتهت اللعبة بسبب انتهاء الوقت\n"
                               f"**الكلمة كانت:** {word}",
                    color=0xffaa00
                )
                await ctx.send(embed=timeout_embed)
                break
        
        # إزالة اللعبة من القائمة النشطة
        if ctx.channel.id in self.active_word_games:
            del self.active_word_games[ctx.channel.id]

    @commands.command(name='تخمين_رقم', aliases=['guess_number'])
    @commands.cooldown(1, 30, commands.BucketType.channel)
    async def guess_number(self, ctx, max_number: int = 100):
        """لعبة تخمين الرقم"""
        if ctx.channel.id in self.active_number_games:
            embed = discord.Embed(
                title="❌ لعبة نشطة",
                description="يوجد لعبة تخمين رقم نشطة بالفعل في هذه القناة!",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        if max_number < 10 or max_number > 1000:
            max_number = 100
        
        secret_number = random.randint(1, max_number)
        attempts = 0
        max_attempts = min(10, max_number // 10 + 3)
        
        embed = discord.Embed(
            title="🔢 لعبة تخمين الرقم",
            description=f"فكرت في رقم بين 1 و {max_number}\n"
                       f"لديك {max_attempts} محاولات لتخمينه!",
            color=0x00ff00
        )
        embed.set_footer(text="⏰ لديك 3 دقائق للعب")
        
        message = await ctx.send(embed=embed)
        
        # تسجيل اللعبة النشطة
        self.active_number_games[ctx.channel.id] = {
            "secret_number": secret_number,
            "max_number": max_number,
            "attempts": attempts,
            "max_attempts": max_attempts,
            "author": ctx.author
        }
        
        def check(m):
            return (m.channel == ctx.channel and 
                   m.content.isdigit() and
                   m.author != self.bot.user)
        
        while attempts < max_attempts:
            try:
                msg = await self.bot.wait_for('message', timeout=180.0, check=check)
                guess = int(msg.content)
                attempts += 1
                
                if guess == secret_number:
                    # فوز!
                    score = max(1, (max_attempts - attempts + 1) * 2)
                    await self.db.update_user_xp(msg.author.id, score)
                    await self.db.update_game_stats(msg.author.id, "number_guess", True, score)
                    
                    win_embed = discord.Embed(
                        title="🎉 أحسنت!",
                        description=f"تهانينا {msg.author.mention}!\n"
                                   f"**الرقم:** {secret_number}\n"
                                   f"**المحاولات:** {attempts}/{max_attempts}\n"
                                   f"**المكافأة:** {score} نقطة خبرة",
                        color=0x00ff00
                    )
                    await ctx.send(embed=win_embed)
                    break
                
                elif guess < secret_number:
                    await msg.add_reaction("⬆️")
                    hint = "الرقم أكبر!"
                else:
                    await msg.add_reaction("⬇️")
                    hint = "الرقم أصغر!"
                
                remaining = max_attempts - attempts
                if remaining > 0:
                    hint_embed = discord.Embed(
                        title="🔢 تخمين خاطئ",
                        description=f"{hint}\n"
                                   f"**المحاولات المتبقية:** {remaining}",
                        color=0xffaa00
                    )
                    await ctx.send(embed=hint_embed, delete_after=10)
                else:
                    # خسارة
                    await self.db.update_game_stats(msg.author.id, "number_guess", False, 0)
                    
                    lose_embed = discord.Embed(
                        title="💀 انتهت اللعبة",
                        description=f"للأسف! لقد نفدت المحاولات\n"
                                   f"**الرقم كان:** {secret_number}",
                        color=0xff0000
                    )
                    await ctx.send(embed=lose_embed)
                    break
                
            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(
                    title="⏰ انتهى الوقت",
                    description=f"انتهت اللعبة بسبب انتهاء الوقت\n"
                               f"**الرقم كان:** {secret_number}",
                    color=0xffaa00
                )
                await ctx.send(embed=timeout_embed)
                break
        
        # إزالة اللعبة من القائمة النشطة
        if ctx.channel.id in self.active_number_games:
            del self.active_number_games[ctx.channel.id]

    @commands.command(name='إحصائيات_الألعاب', aliases=['game_stats'])
    async def game_stats(self, ctx, member: discord.Member = None):
        """عرض إحصائيات الألعاب"""
        if member is None:
            member = ctx.author
        
        # الحصول على إحصائيات من قاعدة البيانات
        async with self.db.db_path and aiosqlite.connect(self.db.db_path) as db:
            cursor = await db.execute(
                'SELECT game_type, wins, losses, total_played, best_score FROM game_stats WHERE user_id = ?',
                (member.id,)
            )
            stats = await cursor.fetchall()
        
        if not stats:
            embed = discord.Embed(
                title="📊 إحصائيات الألعاب",
                description=f"{member.display_name} لم يلعب أي ألعاب بعد!",
                color=0xffaa00
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"📊 إحصائيات الألعاب - {member.display_name}",
            color=0x00ff00
        )
        
        total_games = 0
        total_wins = 0
        
        for game_type, wins, losses, total_played, best_score in stats:
            total_games += total_played
            total_wins += wins
            
            win_rate = (wins / total_played * 100) if total_played > 0 else 0
            
            game_names = {
                "trivia": "🧠 الأسئلة الثقافية",
                "word_guess": "🔤 تخمين الكلمة",
                "number_guess": "🔢 تخمين الرقم"
            }
            
            game_name = game_names.get(game_type, game_type)
            
            embed.add_field(
                name=game_name,
                value=f"**المباريات:** {total_played}\n"
                     f"**الانتصارات:** {wins}\n"
                     f"**الخسائر:** {losses}\n"
                     f"**معدل الفوز:** {win_rate:.1f}%\n"
                     f"**أفضل نتيجة:** {best_score}",
                inline=True
            )
        
        overall_win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
        
        embed.add_field(
            name="📈 الإجمالي",
            value=f"**إجمالي المباريات:** {total_games}\n"
                 f"**إجمالي الانتصارات:** {total_wins}\n"
                 f"**معدل الفوز العام:** {overall_win_rate:.1f}%",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='قائمة_الألعاب', aliases=['games_list'])
    async def games_list(self, ctx):
        """عرض قائمة الألعاب المتاحة"""
        embed = discord.Embed(
            title="🎮 قائمة الألعاب المتاحة",
            description="إليك جميع الألعاب التي يمكنك لعبها:",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🧠 الأسئلة الثقافية",
            value="**الأمر:** `-سؤال [الصعوبة]`\n"
                 f"**الصعوبة:** سهل، متوسط، صعب، عشوائي\n"
                 f"**المكافآت:** 5-15 نقطة حسب الصعوبة\n"
                 f"**الوقت:** 30 ثانية",
            inline=False
        )
        
        embed.add_field(
            name="🔤 تخمين الكلمة",
            value="**الأمر:** `-تخمين_كلمة [الفئة]`\n"
                 f"**الفئات:** حيوانات، فواكه، بلدان، ألوان\n"
                 f"**المكافأة:** 15 نقطة\n"
                 f"**الوقت:** 5 دقائق",
            inline=False
        )
        
        embed.add_field(
            name="🔢 تخمين الرقم",
            value="**الأمر:** `-تخمين_رقم [الحد الأقصى]`\n"
                 f"**النطاق:** 1-1000 (افتراضي: 100)\n"
                 f"**المكافأة:** 1-20 نقطة حسب السرعة\n"
                 f"**الوقت:** 3 دقائق",
            inline=False
        )
        
        embed.add_field(
            name="📊 أوامر إضافية",
            value="**`-إحصائيات_الألعاب`** - عرض إحصائياتك\n"
                 f"**`-قائمة_الألعاب`** - هذه القائمة",
            inline=False
        )
        
        embed.set_footer(text="💡 نصيحة: العب بانتظام لتحسين إحصائياتك وكسب المزيد من النقاط!")
        
        await ctx.send(embed=embed)

    def get_reward_by_difficulty(self, difficulty):
        """حساب المكافأة حسب صعوبة السؤال"""
        rewards = {
            "سهل": 5,
            "متوسط": 10,
            "صعب": 15
        }
        return rewards.get(difficulty, 5)

async def setup(bot):
    await bot.add_cog(Games(bot))
