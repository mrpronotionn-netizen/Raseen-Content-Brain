import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager

class RaseenScheduler:
    def __init__(self, check_interval_hours=3, unanswered_timeout_minutes=20):
        self.memory = MemoryManager()
        self.check_interval_hours = check_interval_hours
        self.unanswered_timeout_minutes = unanswered_timeout_minutes

    def process_cycle(self, is_emergency=False):
        """
        تشغيل دورة فحص وتقييم الفرص (سواء دورية كل 3 ساعات أو طوارئ)
        """
        cycle_type = "EMERGENCY_TREND" if is_emergency else "ROUTINE_CHECK"
        print(f"\n[🔄] بدء دورة المسح: {cycle_type}")
        
        # محاكاة تقييم وموثوقية الفرصة المكتشفة
        sample_trust_score = 92.0 if is_emergency else 85.0
        
        return self.handle_notification_and_fallback(
            topic="تحديثات نموذج الذكاء الاصطناعي الجديد",
            trust_score=sample_trust_score,
            user_replied=False  # محاكاة عدم الرد لتجربة المنطق المزدوج
        )

    def handle_notification_and_fallback(self, topic, trust_score, user_replied=False):
        """
        منطق التعامل مع الإشعارات وعدم الرد
        """
        if user_replied:
            status = "approved_by_user"
            action = "جاهز للنشر بموافقة المستخدم"
        else:
            # تطبيق المنطق المزدوج لعدم الرد بعد 20 دقيقة
            if trust_score >= 90.0:
                status = "auto_published_high_trust"
                action = f"🚀 نشر تلقائي طارئ لارتفاع الموثوقية ({trust_score}%) وحجز صدارة التريند."
            else:
                status = "frozen_pivoted_analysis"
                action = f"🧊 تجميد وتحويل السكريبت إلى تحليل عميق (الموثوقية {trust_score}%)."

        # تسجيل القرار في الذاكرة
        result = self.memory.add_memory(
            memory_type="scheduler_action",
            title=f"جدولة: {topic}",
            content=f"الإجراء: {action}\nدرجة الثقة: {trust_score}%",
            status=status
        )
        return {"action": action, "status": status, "memory_result": result}