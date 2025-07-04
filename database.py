import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

class Database:
    def __init__(self, db_path="unreal_bot.json"):
        self.db_path = db_path
        self._setup_done = False
        self.data = {
            "users": {},
            "voice_activity": [],
            "warnings": [],
            "announcements": [],
            "game_stats": {},
            "tickets": {},
            "ticket_messages": {}
        }
    
    async def ensure_setup(self):
        """التأكد من إعداد قاعدة البيانات"""
        if not self._setup_done:
            await self.setup_database()
            self._setup_done = True

    async def setup_database(self):
        """إنشاء ملف قاعدة البيانات JSON"""
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            print(f"Setting up JSON database at: {os.path.abspath(self.db_path)}")
            
            # تحميل البيانات الموجودة أو إنشاء ملف جديد
            if os.path.exists(self.db_path):
                await self.load_data()
            else:
                await self.save_data()
            
            print("JSON Database setup completed successfully!")
                
        except Exception as e:
            print(f"Error setting up database: {e}")
            raise
    
    async def load_data(self):
        """تحميل البيانات من ملف JSON"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # إذا لم يكن الملف موجود أو تالف، استخدم البيانات الافتراضية
            pass
    
    async def save_data(self):
        """حفظ البيانات في ملف JSON"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
    
    async def add_user(self, user_id: int, username: str):
        """إضافة مستخدم جديد"""
        await self.ensure_setup()
        user_id = str(user_id)
        
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "user_id": user_id,
                "username": username,
                "total_xp": 0,
                "voice_time": 0,
                "messages_sent": 0,
                "games_won": 0,
                "last_daily": None,
                "is_verified": False,
                "join_date": datetime.now().isoformat()
            }
        else:
            # تحديث اسم المستخدم إذا تغير
            self.data["users"][user_id]["username"] = username
        
        await self.save_data()
    
    async def get_user(self, user_id: int):
        """الحصول على بيانات المستخدم"""
        await self.ensure_setup()
        user_id = str(user_id)
        return self.data["users"].get(user_id)
    
    async def update_user_xp(self, user_id: int, xp_amount: int):
        """تحديث خبرة المستخدم"""
        await self.ensure_setup()
        user_id = str(user_id)
        
        if user_id in self.data["users"]:
            self.data["users"][user_id]["total_xp"] += xp_amount
            await self.save_data()
    
    async def log_voice_activity(self, user_id: int, channel_id: int, join_time: datetime, leave_time: datetime = None):
        """تسجيل نشاط الصوت"""
        await self.ensure_setup()
        user_id = str(user_id)
        
        activity = {
            "id": len(self.data["voice_activity"]) + 1,
            "user_id": user_id,
            "channel_id": channel_id,
            "join_time": join_time.isoformat(),
            "leave_time": leave_time.isoformat() if leave_time else None,
            "duration": 0,
            "xp_earned": 0
        }
        
        if leave_time:
            duration = int((leave_time - join_time).total_seconds())
            xp_earned = duration // 60 * 2  # 2 XP لكل دقيقة
            
            activity["duration"] = duration
            activity["xp_earned"] = xp_earned
            
            # تحديث إجمالي وقت الصوت والخبرة للمستخدم
            if user_id not in self.data["users"]:
                await self.add_user(int(user_id), f"User_{user_id}")
            
            self.data["users"][user_id]["voice_time"] += duration
            self.data["users"][user_id]["total_xp"] += xp_earned
        
        self.data["voice_activity"].append(activity)
        await self.save_data()
    
    async def add_warning(self, user_id: int, moderator_id: int, reason: str):
        """إضافة تحذير"""
        await self.ensure_setup()
        
        warning = {
            "id": len(self.data["warnings"]) + 1,
            "user_id": str(user_id),
            "moderator_id": str(moderator_id),
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "active": True
        }
        
        self.data["warnings"].append(warning)
        await self.save_data()
    
    async def get_warnings(self, user_id: int):
        """الحصول على تحذيرات المستخدم"""
        await self.ensure_setup()
        user_id = str(user_id)
        
        return [w for w in self.data["warnings"] 
                if w["user_id"] == user_id and w["active"]]
    
    async def get_top_users(self, limit: int = 10, order_by: str = 'total_xp'):
        """الحصول على أفضل المستخدمين"""
        await self.ensure_setup()
        
        users = list(self.data["users"].values())
        users.sort(key=lambda x: x.get(order_by, 0), reverse=True)
        
        return [(user["user_id"], user["username"], user.get(order_by, 0)) 
                for user in users[:limit]]
    
    async def update_game_stats(self, user_id: int, game_type: str, won: bool = False, score: int = 0):
        """تحديث إحصائيات الألعاب"""
        await self.ensure_setup()
        user_id = str(user_id)
        
        if user_id not in self.data["game_stats"]:
            self.data["game_stats"][user_id] = {}
        
        if game_type not in self.data["game_stats"][user_id]:
            self.data["game_stats"][user_id][game_type] = {
                "wins": 0,
                "losses": 0,
                "total_played": 0,
                "best_score": 0
            }
        
        stats = self.data["game_stats"][user_id][game_type]
        
        if won:
            stats["wins"] += 1
            stats["best_score"] = max(stats["best_score"], score)
        else:
            stats["losses"] += 1
        
        stats["total_played"] += 1
        
        await self.save_data()
    
    async def verify_user(self, user_id: int):
        """تحديث حالة التحقق للمستخدم"""
        await self.ensure_setup()
        user_id = str(user_id)
        
        if user_id in self.data["users"]:
            self.data["users"][user_id]["is_verified"] = True
            await self.save_data()
    
    # طرق نظام التذاكر
    async def create_ticket(self, ticket_id: str, user_id: int, channel_id: int, 
                          category: str, title: str, description: str, priority: str = 'medium'):
        """إنشاء تذكرة جديدة"""
        await self.ensure_setup()
        
        self.data["tickets"][ticket_id] = {
            "id": len(self.data["tickets"]) + 1,
            "ticket_id": ticket_id,
            "user_id": str(user_id),
            "channel_id": channel_id,
            "category": category,
            "title": title,
            "description": description,
            "status": "open",
            "priority": priority,
            "assigned_to": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "closed_at": None,
            "closed_by": None
        }
        
        await self.save_data()
    
    async def get_ticket(self, ticket_id: str):
        """الحصول على تذكرة محددة"""
        await self.ensure_setup()
        return self.data["tickets"].get(ticket_id)
    
    async def update_ticket_status(self, ticket_id: str, status: str, closed_by: int = None):
        """تحديث حالة التذكرة"""
        await self.ensure_setup()
        
        if ticket_id in self.data["tickets"]:
            self.data["tickets"][ticket_id]["status"] = status
            self.data["tickets"][ticket_id]["updated_at"] = datetime.now().isoformat()
            
            if status == 'closed':
                self.data["tickets"][ticket_id]["closed_at"] = datetime.now().isoformat()
                self.data["tickets"][ticket_id]["closed_by"] = str(closed_by) if closed_by else None
            
            await self.save_data()
    
    async def assign_ticket(self, ticket_id: str, assigned_to: int):
        """تعيين تذكرة لموظف"""
        await self.ensure_setup()
        
        if ticket_id in self.data["tickets"]:
            self.data["tickets"][ticket_id]["assigned_to"] = str(assigned_to)
            self.data["tickets"][ticket_id]["updated_at"] = datetime.now().isoformat()
            await self.save_data()
    
    async def add_ticket_message(self, ticket_id: str, user_id: int, message_content: str, message_type: str = 'user'):
        """إضافة رسالة للتذكرة"""
        await self.ensure_setup()
        
        if ticket_id not in self.data["ticket_messages"]:
            self.data["ticket_messages"][ticket_id] = []
        
        message = {
            "id": len(self.data["ticket_messages"][ticket_id]) + 1,
            "ticket_id": ticket_id,
            "user_id": str(user_id),
            "message_content": message_content,
            "message_type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data["ticket_messages"][ticket_id].append(message)
        await self.save_data()
    
    async def get_ticket_messages(self, ticket_id: str):
        """الحصول على رسائل التذكرة"""
        await self.ensure_setup()
        return self.data["ticket_messages"].get(ticket_id, [])
    
    async def get_user_tickets(self, user_id: int, status: str = None):
        """الحصول على تذاكر المستخدم"""
        await self.ensure_setup()
        user_id = str(user_id)
        
        tickets = [ticket for ticket in self.data["tickets"].values() 
                  if ticket["user_id"] == user_id]
        
        if status:
            tickets = [ticket for ticket in tickets if ticket["status"] == status]
        
        # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
        tickets.sort(key=lambda x: x["created_at"], reverse=True)
        
        return tickets
    
    async def get_all_tickets(self, status: str = None, category: str = None, limit: int = 50):
        """الحصول على جميع التذاكر"""
        await self.ensure_setup()
        
        tickets = list(self.data["tickets"].values())
        
        if status:
            tickets = [ticket for ticket in tickets if ticket["status"] == status]
        
        if category:
            tickets = [ticket for ticket in tickets if ticket["category"] == category]
        
        # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
        tickets.sort(key=lambda x: x["created_at"], reverse=True)
        
        return tickets[:limit]
    
    # دوال مساعدة إضافية
    async def get_database_stats(self):
        """الحصول على إحصائيات قاعدة البيانات"""
        await self.ensure_setup()
        
        return {
            "total_users": len(self.data["users"]),
            "total_voice_activities": len(self.data["voice_activity"]),
            "total_warnings": len(self.data["warnings"]),
            "total_tickets": len(self.data["tickets"]),
            "open_tickets": len([t for t in self.data["tickets"].values() if t["status"] == "open"]),
            "closed_tickets": len([t for t in self.data["tickets"].values() if t["status"] == "closed"])
        }
    
    async def backup_database(self, backup_path: str = None):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        await self.ensure_setup()
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}_{self.db_path}"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Database backed up to: {backup_path}")
        return backup_path

# إضافة دالة للاختبار
async def test_database():
    """اختبار قاعدة البيانات"""
    db = Database()
    await db.setup_database()
    
    # اختبار إضافة مستخدم
    await db.add_user(123456789, "TestUser")
    user = await db.get_user(123456789)
    print(f"User data: {user}")
    
    # اختبار الإحصائيات
    stats = await db.get_database_stats()
    print(f"Database stats: {stats}")
    
    print("JSON Database test completed successfully!")

# تشغيل الاختبار إذا تم تشغيل الملف مباشرة
if __name__ == "__main__":
    asyncio.run(test_database())