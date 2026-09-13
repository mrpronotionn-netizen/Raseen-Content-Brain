import os
import json
from datetime import datetime

class MemoryManager:
    """
    مدير الذاكرة التراكمية لـ TikTokAgent (مشروع رصين)
    يقوم بحفظ المحتوى، الأفكار، وتقييمات الأداء لتطوير القرارات المستقبلية.
    """
    def __init__(self, memory_file="content_memory.json"):
        self.memory_file = memory_file
        self._ensure_memory_exists()

    def _ensure_memory_exists(self):
        """إنشاء ملف الذاكرة إذا لم يكن موجوداً"""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def load_memory(self):
        """تحميل سجل الذاكرة الكامل"""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ خطأ أثناء قراءة الذاكرة: {e}")
            return []

    def save_idea(self, title, score, reason, hook_type, status="inbox_ready"):
        """حفظ فكرة وتفاصيل فيديو جديد في الذاكرة"""
        memory = self.load_memory()
        record = {
            "id": len(memory) + 1,
            "title": title,
            "score": score,
            "reason": reason,
            "hook_type": hook_type,
            "status": status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analytics": {
                "views": 0,
                "saves": 0,
                "shares": 0,
                "follower_conversion": 0.0
            }
        }
        memory.append(record)
        
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        print(f"🧠 [MemoryManager]: تم حفظ الفكرة '{title}' في الذاكرة بنجاح.")
        return record

    def is_duplicate(self, title):
        """التحقق مما إذا كانت الفكرة قد أُنتجت سابقاً"""
        memory = self.load_memory()
        for item in memory:
            if item.get("title") == title:
                return True
        return False