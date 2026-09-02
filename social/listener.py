import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager

class SocialListeningEngine:
    def __init__(self):
        self.memory = MemoryManager()

    def process_social_signal(self, topic, source_platform, engagement_score, is_fact=True):
        """
        معالجة الإشارات الاجتماعية والتفريق بين التريند الحقيقي والتفاعل العابر
        """
        signal_type = "verified_trend" if is_fact else "unverified_rumor"
        
        content = (
            f"المنصة: {source_platform}\n"
            f"مستوى التفاعل (Engagement): {engagement_score}/100\n"
            f"تصنيف الإشارة: {signal_type}"
        )
        
        result = self.memory.add_memory(
            memory_type="social_signal",
            title=f"إشارة اجتماعية: {topic}",
            content=content,
            status="social_captured"
        )
        return result